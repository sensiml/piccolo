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
from library.classifiers.classifier import Classifier
from pandas import DataFrame


class struct_linear_regression(ctypes.Structure):
    __slots__ = ["coefficients", "num_coefficients", "intercept"]

    _fields_ = [
        ("coefficients", ctypes.POINTER(ctypes.c_float)),
        ("num_coefficients", ctypes.c_int32),
        ("intercept", ctypes.c_float),
    ]


class NoFeaturesError(Exception):
    pass


class LinearRegression(Classifier):
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
        try:
            # Attempt to cast floating point representations to integers
            data[data.columns[0:num_cols]] = data[data.columns[0:num_cols]].astype(
                float
            )
            assert isinstance(data, DataFrame)
            assert len(data.columns) >= num_cols
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

        model = get_linear_regression_model(model_parameters)

        clf_lib = CDLL(os.path.join(settings.CLASSIFIER_LIBS, "liblinregression.so"))

        model_predict = clf_lib.linear_regression_model_predict

        linear_t = struct_linear_regression
        model_predict.argtypes = [
            ctypes.POINTER(linear_t),
            ctypes.POINTER(ctypes.c_float),
        ]
        model_predict.restype = ctypes.c_float
        feature_vector_c_array = (
            ctypes.c_float * model_parameters["num_coefficients"]
        )()

        for index, feature_vector in enumerate(vectors_to_recognize):
            for i, feature in enumerate(feature_vector["Vector"]):
                feature_vector_c_array[i] = ctypes.c_float(float(feature))

            y_pred = model_predict(
                model,
                feature_vector_c_array,
            )

            vectors_to_recognize[index]["CategoryVector"] = float(
                y_pred
            )  # shift categories by 1
            vectors_to_recognize[index]["DistanceVector"] = [0]

        return self._compute_regression_statistics(
            vectors_to_recognize,
        )

    def compute_cost(self, model_parameters):
        f_cost_dict = {}
        f_cost_dict["flash"] = int(100)
        f_cost_dict["sram"] = int(32 * model_parameters["num_coefficients"])
        f_cost_dict["stack"] = int(32)

        return f_cost_dict


def get_linear_regression_model(model_parameters):
    model = struct_linear_regression()

    array_len = len(model_parameters["coefficients"])
    model_array = ctypes.c_float * array_len
    coefficients = model_array()

    for i in range(array_len):
        coefficients[i] = model_parameters["coefficients"][i]

    model.coefficients = ctypes.cast(coefficients, ctypes.POINTER(ctypes.c_float))
    model.num_coefficients = ctypes.c_int32(model_parameters["num_coefficients"])
    model.intercept = ctypes.c_float(model_parameters["intercept"])

    return model
