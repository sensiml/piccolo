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

#!/usr/bin/env python
# coding: utf-8

import json
import os


os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
from mltk.core.tflite_micro.tflite_micro import TfliteMicro
from mltk.core.tflite_model.tflite_model import TfliteModel

"""
def recognize_feature(tflm_model,vectors_to_recognize):

    tflm_model = None

    for index, feature_vector in enumerate(vectors_to_recognize):


        if len(feature_vector["Vector"]) == 1:
            tflm_model.input(value=feature_vector["Vector"][0])
        else:
            if 'input_dtype' == 'float':
                fv = array(feature_vector["Vector"], dtype=np.float32)
            elif 'input_dtype' == 'int8':
                input_scale, input_zero_point = self._model.get_input_details()[0][
                    "quantization"
                ]
                fv = (
                    np.array(feature_vector["Vector"]) / input_scale
                    + input_zero_point
                ).astype(np.int8)
            elif self._model.get_input_details()[0]["dtype"] == np.uint8:
                fv = array(feature_vector["Vector"], dtype=np.uint8)

            self._tflm_model.input(
                value=fv.reshape(self._model.get_input_details()[0]["shape"])
            )

        self._tflm_model.invoke()
        distance_vector = self._tflm_model.output()

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

      


"""

if __name__ == "__main__":

    import json
    import sys

    from wurlitzer import pipes

    tflite_buffer_file = sys.argv[1]
    accelerator = None if len(sys.argv) == 2 else sys.argv[2]
    accelerator = None if accelerator != "MVP" else "MVP"
    with open(tflite_buffer_file, "rb") as fid:
        tflite_model_buffer = fid.read()

    tflite_model = TfliteModel(tflite_model_buffer)
    tf_micro = TfliteMicro()
    with pipes() as (out, err):
        results = tf_micro.profile_model(tflite_model, accelerator=accelerator)
        ret = results.to_dict()

    print(json.dumps({"status": 1, "message": ret}))
    exit()
