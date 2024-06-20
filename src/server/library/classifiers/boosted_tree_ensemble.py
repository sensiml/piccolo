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

import numpy as np
from django.conf import settings
from django.forms.models import model_to_dict
from library.classifiers.classifier import Classifier
from library.models import FunctionCost
from pandas import DataFrame


class struct_boosted_tree(ctypes.Structure):
    __slots__ = ["node_list", "leafs", "threshold", "features"]

    _fields_ = [
        ("node_list", ctypes.POINTER(ctypes.c_ubyte)),
        ("leafs", ctypes.POINTER(ctypes.c_float)),
        ("threshold", ctypes.POINTER(ctypes.c_ubyte)),
        ("features", ctypes.POINTER(ctypes.c_ubyte)),
    ]


class TrainingFailedException(Exception):
    pass


class NoModelException(Exception):
    pass


class ScalingError(Exception):
    pass


class NoFeaturesError(Exception):
    pass


class BoostedTreeEnsemble(Classifier):
    """
    Uses SCIKIT learn to train the classifier and then quantizes it to 1byte tree ensemble
    """

    def __init__(self, save_model_parameters=True, config=None):

        super(BoostedTreeEnsemble, self).__init__(
            save_model_parameters=save_model_parameters, config=config
        )

        clf_lib = CDLL(os.path.join(settings.CLASSIFIER_LIBS, "libgbtclassifiers.so"))

        uint8_t = ctypes.c_ubyte
        self.__predict = clf_lib.boosted_tree_ensemble_classification

        self.__predict.argtypes = [
            ctypes.POINTER(struct_boosted_tree),
            uint8_t,
            ctypes.POINTER(uint8_t),
        ]
        self.__predict.restype = uint8_t

    def load_model(self, model_parameters):

        self.model_parameters = model_parameters

    def recognize_vectors(
        self, vectors_to_recognize, model_parameters=None, include_predictions=False
    ):
        uint8_t = ctypes.c_ubyte

        if model_parameters is None:
            model_parameters = self.model_parameters

        gb_tree_ensemble, number_of_trees = get_tree_ensemble_c_struct(model_parameters)

        num_features = len(vectors_to_recognize[0]["Vector"])

        num_classes = 2  # currently binary

        number_of_trees = uint8_t(number_of_trees)
        feature_vector_c_array = (uint8_t * num_features)()

        for index, feature_vector in enumerate(vectors_to_recognize):

            for i, feature in enumerate(feature_vector["Vector"]):
                feature_vector_c_array[i] = uint8_t(feature)

            y_pred = self.__predict(
                ctypes.cast(gb_tree_ensemble, ctypes.POINTER(struct_boosted_tree)),
                number_of_trees,
                feature_vector_c_array,
            )

            vectors_to_recognize[index]["CategoryVector"] = int(
                y_pred
            )  # shift categories by 1
            vectors_to_recognize[index]["DistanceVector"] = [0]

        return self._compute_classification_statistics(
            [1, 2], vectors_to_recognize, include_predictions=include_predictions
        )

    def compute_cost(self, model_parameters):
        return compute_cost(model_parameters)


class gtree_t:
    def __init__(self, tree):
        self.features = []
        self.threshold = []
        self.node_list = []
        self.leafs = []

        leaf_node = 0
        node_list = []
        node_count = 1

        for feature in tree["Feature"]:
            if feature != "Leaf":
                self.features.append(int(feature[1:]))
                node_list.append(node_count)
                node_count += 1
            else:
                self.features.append(leaf_node)
                leaf_node += 1

        self.threshold = np.round(tree["Split"].fillna(0).values).astype(int)
        self.leafs = tree[tree["Feature"] == "Leaf"]["Gain"].values
        self.node_list = (
            tree["Yes"]
            .apply(lambda x: int(x.split("-")[1] if isinstance(x, str) else 0))
            .values
        )


def get_tree_ensemble_c_struct(model_parameters):

    df_xgb = DataFrame(model_parameters)
    tree_groups = df_xgb.groupby("Tree")
    models = []

    for key, group in tree_groups:
        models.append(gtree_t(group))

    tree_ensemble = (struct_boosted_tree * len(tree_groups))()

    for index, model in enumerate(models):

        node_array_len = len(model.node_list)
        model_array = ctypes.c_ubyte * node_array_len
        leaf_array_len = len(model.leafs)
        leaf_array_float = ctypes.c_float * leaf_array_len

        node_list = model_array()
        leafs = leaf_array_float()
        threshold = model_array()
        features = model_array()

        for i in range(node_array_len):
            node_list[i] = model.node_list[i]

            threshold[i] = model.threshold[i]
            features[i] = model.features[i]

        for i in range(leaf_array_len):
            leafs[i] = model.leafs[i]

        tree_ensemble[index].node_list = ctypes.cast(
            node_list, ctypes.POINTER(ctypes.c_ubyte)
        )
        tree_ensemble[index].threshold = ctypes.cast(
            threshold, ctypes.POINTER(ctypes.c_ubyte)
        )
        tree_ensemble[index].features = ctypes.cast(
            features, ctypes.POINTER(ctypes.c_ubyte)
        )
        tree_ensemble[index].leafs = ctypes.cast(leafs, ctypes.POINTER(ctypes.c_float))

    return tree_ensemble, len(models)


# python implementation


def boosted_tree_classification(model, feature_vector: list, verbose=False) -> float:
    current_node = 0
    while 1:
        next_node = model.node_list[current_node]
        if feature_vector[model.features[current_node]] > model.threshold[current_node]:
            next_node += 1

        if model.node_list[next_node] == 0:
            return model.leafs[model.features[next_node]]

        current_node = next_node


def get_tree_ensemble(model_parameters):

    df_xgb = DataFrame(model_parameters)
    tree_groups = df_xgb.groupby("Tree")
    models = []

    for key, group in tree_groups:
        models.append(gtree_t(group))

    return models


def boosted_ensemble_classification(tree_ensemble, feature_vector):
    margin = 0

    for tree in tree_ensemble:
        margin += boosted_tree_classification(tree, feature_vector)

    return 1 if margin < 0 else 2


def compute_cost(model_parameters):

    total_flash_size = 0
    f_cost = FunctionCost.objects.get(uuid="8f2e3ec8-c4e4-47c1-a8fd-f61eaaa44469")

    if f_cost is None:
        return {}

    f_cost_dict = model_to_dict(
        f_cost, fields=["flash", "sram", "stack", "latency", "cycle_count"]
    )
    total_flash_size += int(f_cost_dict["flash"])

    df_xgb = DataFrame(model_parameters)
    tree_groups = df_xgb.groupby("Tree")
    models = []
    ptr_flash_size = 4
    num_ptrs_per_tree = 4

    for key, group in tree_groups:
        models.append(gtree_t(group))

    num_trees = len(models)
    for index, model in enumerate(models):
        leaf_array_len = len(model.leafs)
        node_array_len = len(model.node_list)

        leaf_bytes = leaf_array_len * 4
        feature_bytes = node_array_len * 1
        threshold_bytes = node_array_len * 1
        node_bytes = node_array_len * 1

        total_flash_size += leaf_bytes + feature_bytes + threshold_bytes + node_bytes

    total_flash_size += num_trees * ptr_flash_size * num_ptrs_per_tree
    f_cost_dict["flash"] = total_flash_size
    f_cost_dict.pop("cycle_count")
    return f_cost_dict
