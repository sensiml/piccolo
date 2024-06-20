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

if __name__ == "__main__":
    """
    python model_profiler.py <tflite-file-buffer> <accelerator>

    tflite-file-buffer: path to file buffer to use
    accelerator: MVP or empty, empty is for cmsis


    to test

    python model_profiler.py test.tflite

    """

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
