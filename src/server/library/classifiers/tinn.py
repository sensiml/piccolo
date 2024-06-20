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
import random
from ctypes import CDLL

from django.conf import settings
from library.classifiers.classifier import Classifier
from numpy import dtype
from pandas import DataFrame


class ScalingError(Exception):
    pass


class NoFeaturesError(Exception):
    pass


class struct_tinn(ctypes.Structure):
    __slots__ = [
        "weights",
        "output_weights",
        "biases",
        "hidden_layer",
        "output_layer",
        "num_biases",
        "num_weights",
        "num_inputs",
        "num_hidden_neurons",
        "num_outputs",
    ]

    _fields_ = [
        ("weights", ctypes.POINTER(ctypes.c_float)),
        ("output_weights", ctypes.POINTER(ctypes.c_float)),
        ("biases", ctypes.POINTER(ctypes.c_float)),
        ("hidden_layer", ctypes.POINTER(ctypes.c_float)),
        ("output_layer", ctypes.POINTER(ctypes.c_float)),
        ("num_biases", ctypes.c_int32),
        ("num_weights", ctypes.c_int32),
        ("num_inputs", ctypes.c_int32),
        ("num_hidden_neurons", ctypes.c_int32),
        ("num_outputs", ctypes.c_int32),
    ]


class Tinn(Classifier):
    def __init__(self, save_model_parameters=True, config=None):

        super(Tinn, self).__init__(
            save_model_parameters=save_model_parameters, config=config
        )

        clf_lib = CDLL(os.path.join(settings.CLASSIFIER_LIBS, "libtinn.so"))

        self.__xtbuild = clf_lib.xtbuild
        self.__xtbuild.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
        self.__xtbuild.restype = struct_tinn

        self.__xtrain = clf_lib.xttrain
        self.__xtrain.argtypes = [
            struct_tinn,
            ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
            ctypes.c_float,
        ]

        self.__xtrain.restype = ctypes.c_float
        self.__xtpredict = clf_lib.xtpredict
        self.__xtpredict.argtypes = [struct_tinn, ctypes.POINTER(ctypes.c_float)]
        self.__xtpredict.restype = ctypes.POINTER(ctypes.c_float)

        self._num_inputs = None
        self._num_outputs = None
        self._num_hidden_layer = None
        self._model = None

    def preprocess(self, num_cols, data):
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

            data[data.columns[0:num_cols]] -= 127

        except AssertionError:
            raise ScalingError(
                "Tree Ensemble Classifier can only be trained with integers between 0 and 255. Please select a feature scaler or quantizer and add it to your pipeline."
            )
        except ValueError:
            raise NoFeaturesError(
                "There are no features for training. Check the preceding pipeline steps and make sure there are some features for modeling."
            )
        return data

    def load_model(self, model_parameters):

        self.initialize_tinn(
            model_parameters["num_inputs"],
            model_parameters["num_outputs"],
            model_parameters["num_hidden_layer"],
        )

        for index, bias in enumerate(model_parameters["biases"]):
            self._model.biases[index] = bias

        for index, weight in enumerate(model_parameters["weights"]):
            self._model.weights[index] = weight

        self.model_parameters = model_parameters

    def recognize_vectors(
        self, vectors_to_recognize, model_parameters=None, include_predictions=False
    ):

        if model_parameters is not None:
            self.load_model(model_parameters)

        for index, feature_vector in enumerate(vectors_to_recognize):

            # shift categories by 1
            y_pred = self.predict(feature_vector["Vector"]) + 1

            vectors_to_recognize[index]["CategoryVector"] = int(y_pred)
            vectors_to_recognize[index]["DistanceVector"] = [0]

        return self._compute_classification_statistics(
            range(1, model_parameters["num_outputs"] + 1),
            vectors_to_recognize,
            include_predictions=include_predictions,
        )

    def dump_model(self):

        model = {}

        model["biases"] = self._model.biases[: self._model.num_biases]
        model["weights"] = self._model.weights[: self._model.num_weights]
        model["num_inputs"] = self._num_inputs
        model["num_outputs"] = self._num_outputs
        model["num_hidden_layer"] = self._num_hidden_layer
        model["num_weights"] = self._model.num_weights
        model["num_biasses"] = self._model.num_biases

        return model

    def initialize_tinn(self, num_inputs, num_outputs, num_hidden_layer):

        self._num_inputs = num_inputs
        self._num_outputs = num_outputs
        self._num_hidden_layer = num_hidden_layer

        nips = ctypes.c_int32(self._num_inputs)
        nhid = ctypes.c_int32(self._num_hidden_layer)
        nops = ctypes.c_int32(self._num_outputs)

        self._model = self.__xtbuild(nips, nhid, nops)

    def predict(self, feature_vector):
        feature_vector_c_array = (ctypes.c_float * self._num_inputs)()

        for i, value in enumerate(feature_vector):
            feature_vector_c_array[i] = ctypes.c_float(value)

        self.__xtpredict(self._model, feature_vector_c_array)

        max_index = 0
        max_value = self._model.output_layer[0]
        for i in range(1, self._num_outputs):
            if self._model.output_layer[i] > max_value:
                max_value = self._model.output_layer[i]
                max_index = i

        return max_index

    def fit(self, xtrain, ytrue, learning_rate=0.01):

        feature_vector_c_array = (ctypes.c_float * self._num_inputs)()
        result_c_array = (ctypes.c_float * self._num_outputs)()
        alpha = ctypes.c_float(learning_rate)

        indexes = list(range(xtrain.shape[0]))
        random.shuffle(indexes)

        err = 0
        for i in indexes:
            for j, value in enumerate(xtrain.iloc[i]):
                feature_vector_c_array[j] = ctypes.c_float(value)

            result_c_array = (ctypes.c_float * self._num_outputs)()
            result_c_array[ytrue.iloc[i] - 1] = 1.0
            err += self.__xtrain(
                self._model, feature_vector_c_array, result_c_array, alpha
            )

        return err / xtrain.shape[0]
