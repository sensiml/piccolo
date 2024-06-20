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

import binascii
import copy
import json
import os
from abc import abstractmethod
from uuid import uuid4

import numpy as np

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
import tensorflow as tf
from django.conf import settings
from django.forms.models import model_to_dict
from library.classifiers.classifier import Classifier
from library.models import FunctionCost
from numpy import argmax, array, dtype
from pandas import DataFrame


class TensorFlowMicro(Classifier):
    @abstractmethod
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

        # Attempt to cast floating point representations to integers
        data[data.columns[0:num_cols]] = data[data.columns[0:num_cols]].astype(np.int16)
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

        if self._config.get("input_type", "uint8") == "uint8":
            pass
        elif self._config.get("input_type", "uint8") == "int8":
            data[data.columns[0:num_cols]] -= 127

        return data

    def load_model(self, model_parameters):
        self.model_parameters = model_parameters
        tflite_model_buffer = binascii.unhexlify(
            model_parameters["tflite"].encode("ascii")
        )

        self._model = tf.lite.Interpreter(model_content=tflite_model_buffer)
        self._model.allocate_tensors()

    @staticmethod
    def get_model_profile(tflite_model_buffer, accelerator=None):
        librunner_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "utils",
            settings.MODEL_PROFILER,
        )

        tflite_dump = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "utils", f"tflite_{uuid4()}.tmp"
        )

        with open(tflite_dump, "wb") as out:
            out.write(tflite_model_buffer)

        if accelerator:
            p = os.popen(
                f"bash -c 'python {librunner_path} {tflite_dump} {accelerator}'"
            )
        else:
            p = os.popen(f"bash -c 'python {librunner_path} {tflite_dump}'")
        try:
            result = p.read()
            model_profile = json.loads(result)["message"]
        except:
            return {}
        finally:
            os.remove(tflite_dump)

        return model_profile

    @staticmethod
    def compute_tensor_arena_size(
        model_profile,
    ):
        return ((model_profile["summary"]["runtime_memory_size"] // 1024) + 1) * 1024

    def get_input_output_details(self, model_parameters):
        def num_inputs(values):
            tmp = values[0]
            for i in values[1:]:
                tmp *= i

            return tmp

        _model = tf.lite.Interpreter(
            model_content=binascii.unhexlify(model_parameters["tflite"].encode("ascii"))
        )

        quantization = _model.get_input_details()[0]["quantization"]
        if quantization[0] == 0.0:
            quantization = (1, quantization[1])

        return {
            "input_shape": _model.get_input_details()[0]["shape"].tolist(),
            "num_outputs": int(_model.get_output_details()[0]["shape"][1]),
            "num_inputs": num_inputs(_model.get_input_details()[0]["shape"].tolist()),
            "input_quantization": quantization,
        }

    def compute_cost(self, model_parameters):
        total_flash_size = 0
        total_sram_size = 0
        total_cycle_count = 0
        total_stack_size = 0
        f_cost = FunctionCost.objects.get(uuid="dc3a0c60-ce9c-4892-96c6-e8bf292e1bd7")

        tflite_model_buffer = binascii.unhexlify(
            model_parameters["tflite"].encode("ascii")
        )
        model_profile = self.get_model_profile(tflite_model_buffer)

        if f_cost is None:
            return {}

        f_cost_dict = model_to_dict(
            f_cost, fields=["flash", "sram", "stack", "cycle_count"]
        )
        total_flash_size += int(f_cost_dict["flash"])
        total_sram_size += int(f_cost_dict["sram"])
        total_stack_size += int(f_cost_dict["stack"])
        total_cycle_count += int(f_cost_dict["cycle_count"])

        total_flash_size += model_profile["summary"]["tflite_size"]

        model_parameters["tensor_arena_size"] = self.compute_tensor_arena_size(
            model_profile
        )
        self.model_parameters = model_parameters["tensor_arena_size"]

        mvp_profiler_mvp = self.get_model_profile(
            tflite_model_buffer, accelerator="MVP"
        )

        total_sram_size += model_parameters.get("tensor_arena_size", None)
        f_cost_dict["flash"] = total_flash_size
        f_cost_dict["sram"] = total_sram_size
        f_cost_dict["stack"] = total_stack_size

        f_cost_dict["cycle_count"] = int(model_profile["summary"]["cpu_cycles"])
        f_cost_dict["cmnsis_nn"] = model_profile
        f_cost_dict["siliconlabs"] = mvp_profiler_mvp

        return f_cost_dict

    def recognize_vectors(
        self, vectors_to_recognize, model_parameters=None, include_predictions=False
    ):
        if model_parameters is not None:
            self.load_model(model_parameters)
        else:
            model_parameters = self.model_parameters

        input_tensor = self._model.tensor(self._model.get_input_details()[0]["index"])
        num_classes = None

        for index, feature_vector in enumerate(vectors_to_recognize):
            output_tensor = self._model.tensor(
                self._model.get_output_details()[0]["index"]
            )

            if len(feature_vector["Vector"]) == 1:
                input_tensor().fill(feature_vector["Vector"][0])
                # self._tflm_model.input(value=feature_vector["Vector"][0])
            else:
                if self._model.get_input_details()[0]["dtype"] == np.float32:
                    fv = array(feature_vector["Vector"], dtype=np.float32)
                elif self._model.get_input_details()[0]["dtype"] == np.int8:
                    input_scale, input_zero_point = self._model.get_input_details()[0][
                        "quantization"
                    ]
                    fv = (
                        np.array(feature_vector["Vector"]) / input_scale
                        + input_zero_point
                    ).astype(np.int8)
                elif self._model.get_input_details()[0]["dtype"] == np.uint8:
                    fv = array(feature_vector["Vector"], dtype=np.uint8)

                input_tensor()[:] = fv.reshape(
                    self._model.get_input_details()[0]["shape"]
                )
                # self._tflm_model.input(
                #    value=fv.reshape(self._model.get_input_details()[0]["shape"])
                # )

            self._model.invoke()
            distance_vector = copy.deepcopy(output_tensor())
            # self._tflm_model.invoke()
            # distance_vector = self._tflm_model.output()

            while len(distance_vector.shape) > 1:
                distance_vector = distance_vector[0]

            distance_vector = distance_vector.tolist()

            if self.model_parameters["estimator_type"] == "regression":
                category_vector = distance_vector
                vectors_to_recognize[index]["DistanceVector"] = distance_vector
            else:
                category_vector = int(argmax(distance_vector) + 1)

                if self._model.get_output_details()[0]["dtype"] == np.int8:
                    max_distance = float((max(distance_vector) + 127) / 256)
                elif self._model.get_output_details()[0]["dtype"] == np.uint8:
                    max_distance = float((max(distance_vector)) / 256)
                else:
                    max_distance = float((max(distance_vector)))

                if max_distance < model_parameters.get("threshold", 0.0):
                    category_vector = 0

                vectors_to_recognize[index]["DistanceVector"] = distance_vector

            vectors_to_recognize[index]["CategoryVector"] = category_vector

            num_classes = output_tensor().shape[-1]

        if self.model_parameters["estimator_type"] == "regression":
            return self._compute_regression_statistics(vectors_to_recognize)
        else:
            return self._compute_classification_statistics(
                range(1, num_classes + 1),
                vectors_to_recognize,
                include_predictions=include_predictions,
            )
