"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

import ctypes
import os
from ctypes import CDLL

from django.conf import settings
from django.forms.models import model_to_dict
from library.classifiers.classifier import Classifier
from library.models import FunctionCost
from numpy import dtype
from pandas import DataFrame


class struct_tree(ctypes.Structure):
    __slots__ = ["left_children", "right_children", "threshold", "features"]

    _fields_ = [
        ("left_children", ctypes.POINTER(ctypes.c_uint16)),
        ("right_children", ctypes.POINTER(ctypes.c_uint16)),
        ("threshold", ctypes.POINTER(ctypes.c_ubyte)),
        ("features", ctypes.POINTER(ctypes.c_uint16)),
    ]


class TrainingFailedException(Exception):
    pass


class NoModelException(Exception):
    pass


class ScalingError(Exception):
    pass


class NoFeaturesError(Exception):
    pass


class DecisionTreeEnsemble(Classifier):
    """
    Uses SCIKIT learn to train the classifier and then quantizes it to 1byte tree ensemble
    """

    def preprocess(self, num_cols, data, **kwargs):
        """Assumes input dataframe has already been sorted into {features,
        label, groupby} columns and tests that feature columns have been scaled for .
        :param data: an input dataframe, with at least num_cols
        :param num_cols: the number of columns to test are in range (0, 255)
        :return: the unchanged dataframe, if all tests pass
        """
        integer_dtypes = [
            dtype("int64"),
            dtype("int32"),
            dtype("int8"),
            dtype("int16"),
            dtype("uint64"),
            dtype("uint32"),
            dtype("uint8"),
            dtype("uint16"),
        ]
        try:
            # Attempt to cast floating point representations to integers
            data[data.columns[0:num_cols]] = data[data.columns[0:num_cols]].astype(int)
            assert isinstance(data, DataFrame)
            assert len(data.columns) >= num_cols
            assert data[data.columns[0:num_cols]].values.max() < 256
            assert data[data.columns[0:num_cols]].values.min() >= 0
            assert (
                data[data.columns[0:num_cols]]
                .apply(lambda c: c.dtype)
                .isin(integer_dtypes)
                .all()
            )
        except AssertionError:
            raise ScalingError(
                "Tree Ensemble Classifier can only be trained with integers between 0 and 255. Select a feature scaler or quantizer and add it to your pipeline."
            )
        except ValueError:
            raise NoFeaturesError(
                "There are no features for training. Check the preceding pipeline steps and make sure there are some features for modeling."
            )
        return data

    def load_model(self, model_parameters):
        self.model_parameters = model_parameters

    def recognize_vectors(
        self, vectors_to_recognize, model_parameters=None, include_predictions=False
    ):
        if model_parameters is None:
            model_parameters = self.model_parameters

        tree_ensemble = get_tree_ensemble(model_parameters)

        num_classes = len(model_parameters[0]["classes"])
        num_features = len(model_parameters[0]["feature_importances"])

        clf_lib = CDLL(os.path.join(settings.CLASSIFIER_LIBS, "libclassifiers.so"))

        uint8_t = ctypes.c_ubyte
        ensemble_classification = clf_lib.ensemble_classification

        tree_t = struct_tree
        ensemble_classification.argtypes = [
            ctypes.POINTER(tree_t),
            ctypes.POINTER(uint8_t),
            uint8_t,
            uint8_t,
            ctypes.POINTER(uint8_t),
        ]
        ensemble_classification.restype = uint8_t

        number_of_classes = uint8_t(num_classes)

        number_of_trees = uint8_t(len(model_parameters))
        feature_vector_c_array = (uint8_t * num_features)()

        for index, feature_vector in enumerate(vectors_to_recognize):
            classifications_c_array = (uint8_t * num_classes)()

            for i, feature in enumerate(feature_vector["Vector"]):
                feature_vector_c_array[i] = uint8_t(feature)

            y_pred = ensemble_classification(
                ctypes.cast(tree_ensemble, ctypes.POINTER(tree_t)),
                classifications_c_array,
                number_of_trees,
                number_of_classes,
                feature_vector_c_array,
            )

            vectors_to_recognize[index]["CategoryVector"] = int(
                y_pred
            )  # shift categories by 1
            vectors_to_recognize[index]["DistanceVector"] = [0]

        return self._compute_classification_statistics(
            [x + 1 for x in model_parameters[0]["classes"]],
            vectors_to_recognize,
            include_predictions=include_predictions,
        )

    def compute_cost(self, model_parameters):
        total_flash_size = 0
        f_cost = FunctionCost.objects.get(uuid="6a28716f-501b-4baf-8743-5ab32d3bc789")

        if f_cost is None:
            return {}

        f_cost_dict = model_to_dict(f_cost, fields=["flash", "sram", "stack"])
        total_flash_size += int(f_cost_dict["flash"])
        for tree in model_parameters:
            total_flash_size += len(tree["feature"])
            total_flash_size += len(tree["children_right"]) * 2  # size of int16
            total_flash_size += len(tree["children_left"]) * 2  # size of int16
            total_flash_size += len(tree["threshold"])
        f_cost_dict["flash"] = int(total_flash_size)
        f_cost_dict["sram"] = int(f_cost_dict["sram"])
        f_cost_dict["stack"] = int(f_cost_dict["stack"])
        # TODO: calcluate cycle_count based on average tree #/depth

        return f_cost_dict


def get_tree_ensemble(model_parameters):
    tree_ensemble = (struct_tree * len(model_parameters))()

    for index, model in enumerate(model_parameters):
        array_len = len(model["children_left"])
        model_array = ctypes.c_ubyte * array_len
        int_16_model_array = ctypes.c_uint16 * array_len

        left_children = int_16_model_array()
        right_children = int_16_model_array()
        threshold = model_array()
        feature_array = (ctypes.c_uint16 * array_len)()

        for i in range(array_len):
            left_children[i] = model["children_left"][i]
            right_children[i] = model["children_right"][i]
            threshold[i] = model["threshold"][i]
            feature_array[i] = model["feature"][i]

        tree_ensemble[index].left_children = ctypes.cast(
            left_children, ctypes.POINTER(ctypes.c_uint16)
        )
        tree_ensemble[index].right_children = ctypes.cast(
            right_children, ctypes.POINTER(ctypes.c_uint16)
        )
        tree_ensemble[index].threshold = ctypes.cast(
            threshold, ctypes.POINTER(ctypes.c_ubyte)
        )
        tree_ensemble[index].features = ctypes.cast(
            feature_array, ctypes.POINTER(ctypes.c_uint16)
        )

    return tree_ensemble
