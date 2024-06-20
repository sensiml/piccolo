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

from django.conf import settings
from django.forms.models import model_to_dict
from library.classifiers.classifier import Classifier
from library.models import FunctionCost


class struct_bonsai_f32(ctypes.Structure):
    __slots__ = [
        "Theta",
        "W",
        "V",
        "Z",
        "X",
        "mean",
        "depth",
        "d_l",
        "d_input",
        "d_proj",
        "num_nodes",
    ]

    _fields_ = [
        ("Theta", ctypes.POINTER(ctypes.c_float)),
        ("W", ctypes.POINTER(ctypes.c_float)),
        ("V", ctypes.POINTER(ctypes.c_float)),
        ("Z", ctypes.POINTER(ctypes.c_float)),
        ("X", ctypes.POINTER(ctypes.c_float)),
        ("mean", ctypes.POINTER(ctypes.c_float)),
        ("depth", ctypes.c_ubyte),
        ("d_l", ctypes.c_ubyte),
        ("d_input", ctypes.c_ubyte),
        ("d_proj", ctypes.c_ubyte),
        ("num_nodes", ctypes.c_ubyte),
    ]


class Bonsai(Classifier):
    def __init__(self, save_model_parameters=True, config=None):
        super(Bonsai, self).__init__(
            save_model_parameters=save_model_parameters, config=config
        )

        clf_lib = ctypes.CDLL(
            os.path.join(settings.CLASSIFIER_LIBS, "libbonsaiclassifier.so")
        )

        uint8_t = ctypes.c_ubyte
        self.__predict = clf_lib.bonsai_classification

        self.__predict.argtypes = [
            ctypes.POINTER(struct_bonsai_f32),
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

        bonsai, _ = get_bonsai_c_struct(model_parameters)

        num_features = len(vectors_to_recognize[0]["Vector"])

        feature_vector_c_array = (uint8_t * num_features)()

        for index, feature_vector in enumerate(vectors_to_recognize):

            for i, feature in enumerate(feature_vector["Vector"]):
                feature_vector_c_array[i] = uint8_t(feature)
                if i < model_parameters["num_features"]:
                    bonsai.X[i] = ctypes.c_float(feature)

                bonsai.X[model_parameters["num_features"] - 1] = ctypes.c_float(1)

            y_pred = self.__predict(bonsai, feature_vector_c_array)

            vectors_to_recognize[index]["CategoryVector"] = int(y_pred)
            vectors_to_recognize[index]["DistanceVector"] = [0]

        return self._compute_classification_statistics(
            range(1, model_parameters["num_classes"] + 1),
            vectors_to_recognize,
            include_predictions=include_predictions,
        )

    def compute_cost(self, model_parameters):
        total_flash_size = 100
        total_sram_size = 0
        total_cycle_count = 0
        total_stack_size = 0
        f_cost = FunctionCost.objects.get(uuid="22d0d4ce-e92c-4422-81be-fa7414e68d23")

        if f_cost is None:
            return {}

        f_cost_dict = model_to_dict(
            f_cost, fields=["flash", "sram", "stack", "cycle_count"]
        )

        projection_dimension = model_parameters["projection_dimension"]
        num_nodes = model_parameters["num_nodes"]
        num_classes = model_parameters["num_classes"]
        total_flash_size += (5 * 4 * num_classes) + (4 * num_nodes)
        total_sram_size += (
            (3 * 4 * num_classes) + (4 * projection_dimension) + (4 * num_nodes)
        )
        total_stack_size += int(f_cost_dict["stack"])
        total_cycle_count += int(f_cost_dict["cycle_count"])
        mean_shape = int(model_parameters["Mean"].shape[0])
        var_shape = int(model_parameters["Variance"].shape[0])

        total_flash_size += 4 * len(model_parameters["V"])
        total_flash_size += 4 * len(model_parameters["W"])
        total_flash_size += 4 * len(model_parameters["Z"])
        total_flash_size += 4 * len(model_parameters["T"])
        total_flash_size += 4 * mean_shape
        total_flash_size += 4 * var_shape

        f_cost_dict["flash"] = int(total_flash_size)
        f_cost_dict["sram"] = int(total_sram_size)
        f_cost_dict["stack"] = int(total_stack_size)
        f_cost_dict["cycle_count"] = 0

        return f_cost_dict


def get_bonsai_c_struct(model_parameters):
    def get_length(model_parameters, param):
        return len(model_parameters[param])

    def fill_matrix(c_array, numpy_array):
        for i in range(len(numpy_array)):
            c_array[i] = numpy_array[i]

    def scale_matrix(c_array, scale_factor):
        for i in range(len(c_array)):
            c_array[i] = c_array[i] * scale_factor

    def divide_matrix(c_array, array, rows, cols):
        for i in range(rows):
            for j in range(cols):
                c_array[i * cols + j] /= array[j]

    def multiply_matrix_by_vector(c_array, array, matrix_mean, rows, cols):
        for i in range(rows):
            for j in range(cols):
                matrix_mean[i] += c_array[i * cols + j] * array[j]

    matrix_v_array = ctypes.c_float * get_length(model_parameters, "V")
    matrix_w_array = ctypes.c_float * get_length(model_parameters, "W")
    matrix_t_array = ctypes.c_float * get_length(model_parameters, "T")
    matrix_z_array = ctypes.c_float * get_length(model_parameters, "Z")
    matrix_x_array = ctypes.c_float * (model_parameters["num_features"])
    matrix_mean_array = ctypes.c_float * model_parameters["projection_dimension"]

    depth = ctypes.c_ubyte(model_parameters["tree_depth"])
    d_input = ctypes.c_ubyte(model_parameters["num_features"])
    d_proj = ctypes.c_ubyte(model_parameters["projection_dimension"])
    d_l = ctypes.c_ubyte(model_parameters["num_classes"])
    num_nodes = ctypes.c_ubyte(model_parameters["num_nodes"])

    matrix_v = matrix_v_array()
    matrix_w = matrix_w_array()
    matrix_t = matrix_t_array()
    matrix_z = matrix_z_array()
    matrix_x = matrix_x_array()
    matrix_mean = matrix_mean_array()

    fill_matrix(matrix_v, model_parameters["V"])
    fill_matrix(matrix_t, model_parameters["T"])
    fill_matrix(matrix_w, model_parameters["W"])
    fill_matrix(matrix_z, model_parameters["Z"])
    fill_matrix(matrix_x, [0.0 for _ in range(model_parameters["num_features"])])

    # The last X parameter is a bias term that should be 1.0
    matrix_x[model_parameters["num_features"] - 1] = float(1.0)

    # precompute sigma * V
    scale_matrix(matrix_v, float(model_parameters["sigma"]))

    # Normalize the Z matrix by the projection dimensions
    scale_matrix(matrix_z, 1.0 / float(model_parameters["projection_dimension"]))

    # precopmoute Z (X - m) / V by pulling out Z * m/V and Z/V
    divide_matrix(
        matrix_z,
        model_parameters["Variance"],
        model_parameters["projection_dimension"],
        model_parameters["num_features"],
    )

    multiply_matrix_by_vector(
        matrix_z,
        model_parameters["Mean"],
        matrix_mean,
        model_parameters["projection_dimension"],
        model_parameters["num_features"],
    )

    bonsai = struct_bonsai_f32()

    bonsai.V = matrix_v
    bonsai.Theta = matrix_t
    bonsai.Z = matrix_z
    bonsai.W = matrix_w
    bonsai.X = matrix_x
    bonsai.mean = matrix_mean
    bonsai.depth = depth
    bonsai.d_input = d_input
    bonsai.d_l = d_l
    bonsai.num_nodes = num_nodes
    bonsai.d_proj = d_proj

    sizes = {
        "V": len(matrix_v),
        "Theta": len(matrix_t),
        "Z": len(matrix_z),
        "W": len(matrix_w),
        "X": len(matrix_x),
        "Mean": len(matrix_mean),
    }

    return bonsai, sizes
