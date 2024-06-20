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

# In[1]:


import os
import json
import ctypes
from ctypes import CDLL
import binascii

library_name = "libtensorflow-microlite.so"


class ImportPathException(Exception):
    pass


class TensorFlowMicroRunner(object):
    """
    Used to check if the tensor size is enough to be allocated.

    tf_ml = TensorFlowMicroRunner(<path_to_libsensiml.so>)
    tf_ml.set_model(tfmodel)
    tf_ml.init_model()


    """

    def __init__(self, path):
        self._model_initialized = False
        self._lib_path = path

        if not os.path.exists(os.path.join(path, library_name)):
            raise ImportPathException(
                "ERROR: {} as not found in {}".format(library_name, path)
            )

        self.clf_lib = CDLL(os.path.join(path, library_name))
        self.handle = self.clf_lib._handle

        self._micro_model_setup = self.clf_lib.micro_model_setup
        self._micro_model_setup.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ubyte),
        ]
        self._micro_model_setup.restype = ctypes.c_int

    def set_model(self, model_data):

        self.model_data_array = (ctypes.c_ubyte * len(tflite_model)).from_buffer_copy(
            model_data
        )

    def init_model(self, tensor_arena_size):
        """
        This will initialize the parameters of all the models, it should be run once before
        running anything elese.
        """
        if not self._model_initialized:
            self._model_initialized = True

            tensor_arena = (ctypes.c_uint8 * tensor_arena_size)()
            tensor_arena_size = ctypes.c_int(tensor_arena_size)

            ret = self._micro_model_setup(
                self.model_data_array, tensor_arena_size, tensor_arena
            )

            return ret

        else:
            raise Exception("Model was already initialized!")


if __name__ == "__main__":

    import sys
    import json
    from wurlitzer import pipes

    tf_size = int(sys.argv[1])
    model_parameters_file = sys.argv[2]
    model_parameters = open(model_parameters_file, "r").read()

    tflite_model = binascii.unhexlify(model_parameters.encode("ascii"))

    tfmr = TensorFlowMicroRunner(
        os.path.join(os.path.dirname(os.path.abspath(__file__)))
    )
    tfmr.set_model(tflite_model)
    with pipes() as (out, err):
        ret = tfmr.init_model(tf_size)

    if ret == 0:
        for line in err.read().split("\n"):
            if "FOUND TENSOR SIZE:" in line:
                print(json.dumps({"status": ret, "message": line}))
                exit()

    elif ret == -1:
        print(json.dumps({"status": ret, "message": "Model version missmatch"}))
    elif ret == 2:
        print(json.dumps({"status": ret, "message": "Failed to allocate Tensor"}))

    del tfmr.clf_lib
    libdl = ctypes.CDLL("libdl.so")
    libdl.dlclose(tfmr.handle)
    del tfmr
