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
import json
import os
import subprocess
import zipfile
from ctypes import CDLL

try:
    from typing import Literal
except:
    from typing_extensions import Literal

try:
    from wurlitzer import pipes
except:
    pass

from typing import Dict, List, Optional

from numpy import ndarray
from pandas import DataFrame, Series

USE_PIPES = True if os.name == "posix" else False


class ImportPathException(Exception):
    pass


def get_activation(tensor):
    return (max(tensor) + 128) / 256.0


def dummy_function(*args, **kwrags):
    print("Not Supported by this version of the Knowledge Pack.")
    return None


def compile_libsensiml_shared_library(path):
    current_dir = os.getcwd()
    try:
        os.chdir(path)

        if os.path.exists("libtensorflow-microlite.a"):
            print("calling: g++ --shared libtensorflow-microlite.a")
            subprocess.call(
                "g++ --shared -o libsensiml.so -Wl,--whole-archive libtensorflow-microlite.a libsensiml.a  -Wl,--no-whole-archive",
                shell=True,
            )
        else:
            print("calling: ar -x libsensiml.a")
            subprocess.call(["ar", "-x", "libsensiml.a"])
            print("calling: g++ -shared -o libsensiml.so *.o")
            subprocess.call("g++ -shared -o libsensiml.so *.o", shell=True)

        if os.path.exists("libsensiml.so"):
            print("Successfully created libsensiml.so")
    except Exception as e:
        raise e
    finally:
        os.chdir(current_dir)

    os.chdir(current_dir)


def parse_model_json_for_class_map(path):
    if os.path.exists(os.path.join(path, "model.json")):
        model_info = json.load(open(os.path.join(path, "model.json"), "r"))
        class_maps = [x["ClassMaps"] for x in model_info["ModelDescriptions"]]
        return [{int(k): v for k, v in class_map.items()} for class_map in class_maps]

    return None


def parse_model_json_for_model_type(path):
    if os.path.exists(os.path.join(path, "model.json")):
        model_info = json.load(open(os.path.join(path, "model.json"), "r"))
        return [
            description["ModelType"] for description in model_info["ModelDescriptions"]
        ]

    return None


def is_tensorflow(ModelType):
    if type(ModelType) != str:
        return False

    if "TF Micro" in ModelType:
        return True

    if "TensorFlow Lite for Microcontrollers" in ModelType:
        return True

    return False


class struct_pme_pattern(ctypes.Structure):
    __slots__ = ["influence", "category", "vector"]

    _fields_ = [
        ("influence", ctypes.c_uint16),
        ("category", ctypes.c_uint16),
        ("vector", ctypes.POINTER(ctypes.c_uint8)),
    ]


class struct_pme_model_header(ctypes.Structure):
    __slots__ = ["number_patterns", "pattern_length"]

    _fields_ = [
        ("number_patterns", ctypes.c_uint16),
        ("pattern_length", ctypes.c_uint16),
    ]


class struct_float_data_t(ctypes.Structure):
    __slots__ = ["data", "size"]

    _fields_ = [
        ("data", ctypes.POINTER(ctypes.c_float)),
        ("size", ctypes.c_int),
    ]


class struct_model_result(ctypes.Structure):
    __slots__ = ["model_type", "result", "output_tensor"]

    _fields_ = [
        ("model_type", ctypes.c_uint8),
        ("result", ctypes.c_float),
        ("output_tensor", ctypes.POINTER(struct_float_data_t)),
    ]


def empty_function(*args, **kwargs):
    print("Not Supported by this Knowledge Pack.")
    return


class Model(object):
    def __init__(self, neuron_array, class_map, configuration, feature_summary=None):
        self._class_map = None
        self._feature_summary = None
        self._neuron_array = None
        self._configuration = None

        self.class_map = class_map
        self.neuron_array = neuron_array
        self.configuration = configuration

        if feature_summary:
            self.feature_summary = feature_summary
        else:
            self.feature_summary_from_neurons()

    @property
    def class_map(self):
        return self._class_map

    @class_map.setter
    def class_map(self, value):
        self._class_map = value

    @property
    def neuron_array(self):
        return self._neuron_array

    @neuron_array.setter
    def neuron_array(self, value):
        self._neuron_array = value

    @property
    def configuration(self):
        return self._configuration

    @configuration.setter
    def configuration(self, value):
        self._configuration = value

    @property
    def feature_summary(self):
        return self._feature_summary

    @feature_summary.setter
    def feature_summary(self, value):
        self._feature_summary = [{"Feature": str(x)} for x in value]

    def feature_summary_from_neurons(self):
        feature_vector = self.neuron_array[0]["Vector"]
        self.feature_summary = [{"Feature": str(x)} for x in range(len(feature_vector))]


class ModelRunner:
    def __init__(self, path: str, class_map: Optional[Dict] = None):
        """
        This class provides a Python interface to the Knowledge Pack library C code.

        Args:
            path (str): Path to the downloaded Knowledge Pack .zip, the libsensiml.so, or libsensiml.dll.
            class_map (Dict, optional): The class map to use for this model. Defaults to None.

        Example:

            After downloading the Knowledge Pack for Windows or Linux:

                sml = ModelRunner(<path_to_knowledgepack.zip>)
                sml.init_model()

        """

        self._run_type = None
        self._model_initialized = False

        if path[-3:] == "zip":
            unzip_dir = os.path.basename(path)[:-4]
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(unzip_dir)
                lib_path = os.path.join(unzip_dir, "knowledgepack", "sensiml", "lib")
                model_json_path = os.path.join(unzip_dir, "knowledgepack")
        else:
            lib_path = os.path.join(path, "knowledgepack", "sensiml", "lib")
            model_json_path = os.path.join(path, "knowledgepack")

        if os.name == "nt":
            if not os.path.exists(os.path.join(lib_path, "libsensiml.dll")):
                print(f"ERROR: libsensiml.dll as not found in {lib_path}.")
                raise ImportPathException(
                    f"ERROR: libsensiml.dll as not found in {lib_path}"
                )

            self.clf_lib = CDLL(os.path.join(lib_path, "libsensiml.dll"))

        if os.name == "posix":
            if not os.path.exists(os.path.join(lib_path, "libsensiml.so")):
                print(f"Warning: libsensiml.so as not found in {lib_path}. Attempting")
                if not os.path.exists(os.path.join(path, "libsensiml.a")):
                    print(f"ERROR: libsensiml.a as not found in {lib_path}.")

                print("Attempting to compile libsensiml.so")

                compile_libsensiml_shared_library(lib_path)

                if not os.path.exists(os.path.join(lib_path, "libsensiml.so")):
                    raise ImportPathException(
                        f"ERROR: libsensiml.so as not found in {lib_path}"
                    )

            self.clf_lib = CDLL(
                os.path.join(lib_path, "libsensiml.so"), mode=ctypes.RTLD_GLOBAL
            )

        if class_map is not None:
            if isinstance(class_map, dict):
                self.class_map = [{int(k): v for k, v in class_map.items()}]
            elif isinstance(class_map, list):
                self.class_map = []
                for model_class_map in class_map:
                    self.class_map.append(
                        {int(k): v for k, v in model_class_map.items()}
                    )
        else:
            self.class_map = parse_model_json_for_class_map(model_json_path)

        self.model_type = parse_model_json_for_model_type(model_json_path)

        self.set_kb_api_standard()

    def set_kb_api_standard(self):

        clf_lib = self.clf_lib

        self._model_init = clf_lib.kb_model_init
        self._model_init.argtypes = []

        self._run_model = clf_lib.kb_run_model
        self._run_model.argtypes = [
            ctypes.POINTER(ctypes.c_int16),
            ctypes.c_int,
            ctypes.c_int,
        ]
        self._run_model.restype = ctypes.c_int

        self._run_model_cascade_features = clf_lib.kb_run_model_with_cascade_features
        self._run_model_cascade_features.argtypes = [
            ctypes.POINTER(ctypes.c_int16),
            ctypes.c_int,
            ctypes.c_int,
        ]
        self._run_model_cascade_features.restype = ctypes.c_int

        self._run_segment = clf_lib.kb_run_segment
        self._run_segment.argtypes = [ctypes.c_int]
        self._run_segment.restype = ctypes.c_int

        self._add_segment = clf_lib.kb_add_segment
        self._add_segment.argtypes = [
            ctypes.POINTER(ctypes.c_int16),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]

        self._reset_model = clf_lib.kb_reset_model
        self._reset_model.argtypes = [ctypes.c_int]
        self._reset_model.restype = ctypes.c_int

        self._kb_get_model_sg_length = clf_lib.kb_get_model_sg_length
        self._kb_get_model_sg_length.argtypes = [
            ctypes.c_int,
        ]
        self._kb_get_model_sg_length.restype = ctypes.c_int

        self._kb_get_sg_start_index = clf_lib.kb_get_sg_start_index
        self._kb_get_sg_start_index.argtypes = [
            ctypes.c_int,
        ]
        self._kb_get_sg_start_index.restype = ctypes.c_int

        self._kb_get_segment_length = clf_lib.kb_get_segment_length
        self._kb_get_segment_length.argtypes = [
            ctypes.c_int,
        ]
        self._kb_get_segment_length.restype = ctypes.c_int

        self._sml_get_feature_bank_number = clf_lib.sml_get_feature_bank_number
        self._sml_get_feature_bank_number.argtypes = [
            ctypes.c_int,
        ]
        self._sml_get_feature_bank_number.restype = ctypes.c_int

        self._kb_get_segment_data = clf_lib.kb_get_segment_data
        self._kb_get_segment_data.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_int16),
        ]

        self._kb_get_num_sensor_buffers = clf_lib.kb_get_num_sensor_buffers
        self._kb_get_num_sensor_buffers.argtypes = [
            ctypes.c_int,
        ]

        # self._print_model_map = clf_lib.kb_print_model_map

        # self._print_model_result = clf_lib.kb_print_model_result
        # self._print_model_result.argtypes = [ctypes.c_int, ctypes.c_int]

        # self._print_model_score = clf_lib.kb_print_model_score
        # self._print_model_score.argtypes = [ctypes.c_int]
        # self._print_model_score.restype = ctypes.c_int

        # self._score_model = clf_lib.kb_score_model
        # self._score_model.argtypes = [ctypes.c_int, ctypes.c_uint16]
        # self._score_model.restype = ctypes.c_int

        # self._retrain_model = clf_lib.kb_retrain_model
        # self._retrain_model.argtypes = [ctypes.c_int]
        # self._retrain_model.restype = ctypes.c_int

        if hasattr(clf_lib, "kb_flush_model_buffer"):
            self._flush_model_buffer = clf_lib.kb_flush_model_buffer
            self._flush_model_buffer.argtypes = [ctypes.c_int]
            self._flush_model_buffer.restype = ctypes.c_int
        else:
            self._flush_model_buffer = dummy_function

        self._add_last_pattern_to_model = clf_lib.kb_add_last_pattern_to_model
        self._add_last_pattern_to_model.argtypes = [
            ctypes.c_int,
            ctypes.c_uint16,
            ctypes.c_uint16,
        ]
        self._add_last_pattern_to_model.restype = ctypes.c_int

        self._kb_get_model_result_info = clf_lib.kb_get_model_result_info
        self._kb_get_model_result_info.argtypes = [
            ctypes.c_int,
        ]
        self._kb_get_model_result_info.restype = ctypes.POINTER(struct_model_result)

        self._add_custom_pattern_to_model = clf_lib.kb_add_custom_pattern_to_model
        self._add_custom_pattern_to_model.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint16,
            ctypes.c_uint16,
        ]
        self._add_custom_pattern_to_model.restype = ctypes.c_int

        # self._print_model_class_map = clf_lib.kb_print_model_class_map
        # self._print_model_class_map.argtypes = [ctypes.c_int, ctypes.c_char_p]

        self._get_model_header = clf_lib.kb_get_model_header
        self._get_model_header.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(struct_pme_model_header),
        ]
        self._get_model_header.restype = ctypes.c_int

        self._get_model_pattern = clf_lib.kb_get_model_pattern
        self._get_model_pattern.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.POINTER(struct_pme_pattern),
        ]
        self._get_model_pattern.restype = ctypes.c_int

        self._flush_model = clf_lib.kb_flush_model_buffer
        self._flush_model.argtypes = [ctypes.c_int]
        self._flush_model.restype = ctypes.c_int

        try:
            self._sml_recognition_run = clf_lib.sml_recognition_run
            self._sml_recognition_run.argtypes = [
                ctypes.POINTER(ctypes.c_int16),
                ctypes.c_int,
            ]
            self._sml_recognition_run.restype = ctypes.c_int
        except:
            self._sml_recognition_run = None

        try:
            self._get_feature_vector_type = clf_lib.get_feature_vector_type
            self._get_feature_vector_type.argtypes = [
                ctypes.c_int,
            ]
            self._get_feature_vector_type.restype = ctypes.c_uint8
        except:
            self._get_feature_vector_type = empty_function

        try:
            self._get_feature_vector_size = clf_lib.kb_get_feature_vector_size
            self._get_feature_vector_size.argtypes = [
                ctypes.c_int,
            ]
            self._get_feature_vector_size.restype = ctypes.c_uint16
        except:
            self._get_feature_vector_size = empty_function

        try:
            self._copy_feature_vector = clf_lib.copy_feature_vector
            self._copy_feature_vector.argtypes = [
                ctypes.c_int,
                ctypes.c_void_p,
            ]
        except:
            self._copy_feature_vector = empty_function

        try:
            self._set_feature_vector = clf_lib.kb_set_feature_vector
            self._set_feature_vector.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_void_p),
            ]
        except:
            self._set_feature_vector = empty_function

        try:
            self._set_feature_vector_raw = clf_lib.kb_set_feature_vector_raw
            self._set_feature_vector_raw.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_float),
            ]
            self._set_feature_vector_raw.restype = ctypes.c_int32
        except:
            self._set_feature_vector = empty_function

        try:
            self._get_feature_vector_raw_size = clf_lib.kb_get_feature_vector_raw_size
            self._get_feature_vector_raw_size.argtypes = [
                ctypes.c_int,
            ]
            self._get_feature_vector_raw_size.restype = ctypes.c_uint16
        except:
            self._get_feature_vector_raw_size = empty_function

        try:
            self._copy_feature_vector_raw = clf_lib.kb_copy_feature_vector_raw
            self._copy_feature_vector_raw.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_float),
            ]
        except:
            self._copy_feature_vector_raw = empty_function

        try:
            self._get_feature_vector_raw_pointer = (
                clf_lib.get_feature_vector_raw_pointer
            )
            self._get_feature_vector_raw_pointer.argtypes = [
                ctypes.c_int,
            ]
            self._get_feature_vector_raw_pointer.restype = ctypes.POINTER(
                ctypes.c_float
            )
        except:
            self._get_feature_vector_raw_pointer = empty_function

        try:
            self._recognize_feature_vector = clf_lib.kb_recognize_feature_vector
            self._recognize_feature_vector.argtypes = [ctypes.c_int]
            self._recognize_feature_vector.restype = ctypes.c_uint16
        except:
            self._recognize_feature_vector = empty_function

    def _initialized(self):
        if not self._model_initialized:
            print("Initialize the model before running this function")
            return None

        return True

    def _run_with(self, run_type):
        if self._run_type is None:
            self._run_type = run_type

        if self._run_type != run_type:
            print(
                "This model has already been run with {}. You will need to restart your kernel to run in this mode.".format(
                    self._run_type
                )
            )
            return False

        return True

    def init_model(self):
        """
        This will initialize the parameters of all the models, it should be run once before
        running any other APIs.
        """
        if not self._model_initialized:
            self._model_initialized = True
            self._model_init()

    def flush_model_buffer(self, model_index: int = 0):
        """
        This will flush the data buffer of a Knowledge Pack.
        """
        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        self._flush_model_buffer(model_index_ctype)

    def run_model(
        self,
        data_sample,
        model_index: int = 0,
        debug_log: bool = True,
        model_api: Literal[
            "run_model", "run_model_cascade_features", "sml_recognition_run"
        ] = "run_model",
    ):
        """
        This is the main entry point into the pipeline. It takes a single timepoint of data as an array. Adds that sample to the internal ring buffer
        checks for a segment, generates features if there is a segment,
        produces a classification and returns the result.

        Args:
            data_sample(array):  single timepoint of data as an array from all sensors
            nsensors(int): unused
            model_index(int): Index of the model to run
            debug_log(bool): Prints the debug output from the Knowledge Pack
            model_api(str): use run_model, run_model_cascade_features or sml_recognition_run. These correspond to the API's in the kb.h file

        Returns:
            Classification results will be 0 if unknown through the classification numbers
                you have. This function returns -1 when a segment hasn't yet been identified.

        """
        if not self._initialized():
            return

        if self._run_with("run_model") is False:
            return

        if isinstance(data_sample, DataFrame) or isinstance(data_sample, Series):
            data = data_sample.values
        elif isinstance(data_sample, ndarray):
            data = data_sample
        else:
            print("Input data Must be either dataframe or array.")
            return

        data_array = (ctypes.c_int16 * data.shape[0])()
        nsensors_ctype = ctypes.c_int(0)
        model_index_ctype = ctypes.c_int(model_index)

        for index, value in enumerate(data):
            data_array[index] = ctypes.c_int16(value)

        if model_api == "run_model":
            ret = self._run_model(data_array, nsensors_ctype, model_index_ctype)
        elif model_api == "sml_recognition_run":
            ret = self._sml_recognition_run(data_array, model_index_ctype)
        elif model_api == "run_model_cascade_features":
            ret = self._run_model_cascade_features(
                data_array, nsensors_ctype, model_index_ctype
            )
        else:
            raise Exception("Invalid model_api")

        return ret

    def recognize_capture(
        self,
        data: DataFrame,
        model_index: int = 0,
        model_api: Literal[
            "run_model", "run_model_cascade_features", "sml_recognition_run"
        ] = "run_model",
        get_unscaled_feature_vector: bool = False,
        get_feature_vector: bool = False,
        get_sensor_data: bool = False,
        get_output_tensor: bool = True,
        verbose: bool = True,
    ) -> DataFrame:
        """Run the model against a DataFrame of sensor data

        Args:
            data (DataFrame): Input sensor data
            model_index (int, optional): The index of model to use. Defaults to 0.
            model_api (Literal[&quot;run_model&quot;,&quot;run_model_cascade_features&quot;,&quot;sml_recognition_run&quot;], optional): Model API to use. Defaults to "run_model".
            get_feature_vector (bool, optional): Includes the feature vector output in the returned result. Defaults to False.
            get_sensor_data (bool, optional): Includes the sensor data in the returned result. Defaults to False.
            get_output_tensor (bool, optional): Includes the output tensor probabilities in the returned result (if applicable). Defaults to True.

        Returns:
            DataFrame: results of the model along with the feature_vectors and output probabilities
        """

        M = []

        status = [len(data) // 4, len(data) // 2, 3 * len(data) // 4]
        self.flush_model_buffer(model_index=model_index)

        for i in range(0, len(data)):
            # pass a single sample
            ret = self.run_model(
                data.iloc[i], model_index=model_index, model_api=model_api
            )

            if ret >= 0:
                output_columns = {
                    "label_value": (
                        ret
                        if self.get_class_map(model_index) is None
                        else self.get_class_map(model_index).get(ret, ret)
                    ),
                    "capture_sample_sequence_start": i
                    + 1
                    - self.get_segment_length(model_index=model_index),
                    "capture_sample_sequence_end": i,
                }

                if get_unscaled_feature_vector:
                    output_columns["unscaled_feature_vector"] = (
                        self.get_unscaled_feature_vector(model_index)
                    )

                if get_feature_vector:
                    output_columns["feature_vector"] = self.get_feature_vector(
                        model_index
                    )

                n_sensors = self.get_model_framelen(model_index)

                if get_sensor_data:
                    for i in range(n_sensors):
                        sensor_data = self.get_segment_data(model_index)
                        output_columns["sensor_data_%d" % i] = sensor_data[i]

                if get_output_tensor:
                    output_tensor = self.get_model_result(model_index)
                    output_columns["output_tensor"] = output_tensor
                    if self.model_type and is_tensorflow(self.model_type[model_index]):
                        output_columns["activation"] = get_activation(output_tensor)

                M.append(output_columns)

                # After a classification is received, call sml_reset model to advance the internal buffer.
                if model_api != "sml_recognition_run":
                    self.reset_model(model_index=model_index)

            if verbose and i in status:
                print(f"processed {i} samples")

        print(f"finished processing {len(data)} samples")

        return DataFrame(M)

    def run_segment(
        self, data_segment: DataFrame, model_index: int = 0, debug_log: bool = False
    ):
        """
        Add a segment of data to the model as input. Then runs the model on the current segment, skipping the data streaming steps.

        (Warning: using this call will flush the models internal ring buffer. Alternating between this and run_and_score model may produce incorrect results or crashes)

        Args:
            data(array):  Array of timseries data
            model_index(int): Index of the model to run
            debug_log(bool): Prints the debug output from the Knowledge Pack

        Returns:
            Classification results will be 0 if unknown through the classification numbers
            you have. This function returns -1 when a segment hasn't yet been identified.

        """
        if not self._initialized():
            return

        if self._run_with("run_segment") is False:
            return

        if isinstance(data_segment, (DataFrame, Series)):
            data = data_segment.values
        elif isinstance(data_segment, ndarray):
            data = data_segment
        else:
            print("Input data Must be either dataframe or array.")
            return

        data_array = (ctypes.c_int16 * (data.shape[0] * data.shape[1]))()
        length_ctype = ctypes.c_int(data.shape[0])
        nbuffs = ctypes.c_int(data.shape[1])
        model_index_ctype = ctypes.c_int(model_index)

        for col in range(data.shape[1]):
            for index, value in enumerate(data[:, col]):
                data_array[col * data.shape[0] + index] = ctypes.c_int16(value)

        self._add_segment(data_array, length_ctype, nbuffs, model_index_ctype)

        model_index_ctype = ctypes.c_int(model_index)

        if USE_PIPES:
            with pipes() as (out, _):
                ret = self._run_segment(model_index_ctype)
        else:
            ret = self._run_segment(model_index_ctype)

        if debug_log and USE_PIPES:
            print(out.read())

        return ret

    def reset_model(self, model_index: int = 0):
        """
        Advances the model state to so that it is ready for a more input data. Use
        only after classification steps.

        (Note: this does not reset the model to a clean state, only init_model does this)

        Args:
           model_index(int): Index of the model to update
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        self._reset_model(model_index_ctype)

    def flush_model(self, model_index: int = 0):
        """
        Deletes all of the patterns in the database.

        Args:
           model_index(int): Index of the model to update
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        self._flush_model(model_index_ctype)

    def get_model(self, model_index: int = 0):
        """
        Prints the model weights and info for current model if supported by this model type.

        Args:
            model index - number of axes in the data stream

        """

        if not self._initialized():
            return

        model_header = self.get_model_header(model_index)
        model = []

        for index in range(model_header.number_patterns):
            tmp_dict = {}
            pattern = self.get_model_pattern(model_index, index)
            tmp_dict["Category"] = pattern.category
            tmp_dict["Vector"] = [
                pattern.vector[i] for i in range(model_header.pattern_length)
            ]
            tmp_dict["AIF"] = pattern.influence
            tmp_dict["Identifier"] = index
            model.append(tmp_dict)

        return DataFrame(model)

    def get_class_map(self, model_index: int = 0) -> Dict:
        """Returns the class map for the model

        Args:
            model_index (int, optional): The model index. Defaults to 0.

        Returns:
            dict: Class map for the specified model_index
        """

        if not self._initialized():
            return None

        return self.class_map[model_index]

    def get_model_header(self, model_index: int = 0):
        """Returns the model header for a PME model

        Args:
            model_index (int, optional): The model index. Defaults to 0.

        Returns:
            struct_pme_model_header: A struct object containing information about the PME model header
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)
        pme_model_header = struct_pme_model_header()

        with pipes() as (out, _):
            self._get_model_header(model_index_ctype, pme_model_header)

        return pme_model_header

    def get_model_pattern(self, model_index: int = 0, pattern_index: int = 0):
        """Returns the pattern for a PME model at a particular index

        Args:
            model_index (int, optional): The model index. Defaults to 0.
            pattern_index (int, optional): The index of the pattern in the database to retrieve. Defaults to 0.

        Returns:
            struct_pme_pattern: struct_pme_pattern object
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)
        pattern_index_ctype = ctypes.c_int(pattern_index)
        pme_pattern = struct_pme_pattern()

        with pipes() as (out, _):
            self._get_model_pattern(model_index_ctype, pattern_index_ctype, pme_pattern)

        return pme_pattern

    def get_segment_data(self, model_index: int = 0) -> List:
        """Returns the segment data currently stored in the models internal ring buffer.

        Args:
            model_index (int, optional): The model index. Defaults to 0.

        Returns:
            list: the sensor data stored in the model ring buffer
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        n_sensors = self._kb_get_num_sensor_buffers(model_index_ctype)

        number_samples = self._kb_get_model_sg_length(model_index_ctype)
        index = self._kb_get_sg_start_index(model_index_ctype)

        number_samples_ctype = ctypes.c_int(number_samples)
        index_ctype = ctypes.c_int(index)

        buffer_size = number_samples * n_sensors
        sensor_data_buffer = (ctypes.c_short * buffer_size)()

        self._kb_get_segment_data(
            model_index_ctype, number_samples_ctype, index_ctype, sensor_data_buffer
        )

        sensor_data_buffer = list(sensor_data_buffer)
        sensor_data = []
        for i in range(0, buffer_size, number_samples):
            sensor_data.append(sensor_data_buffer[i : i + number_samples])

        return sensor_data

    def get_model_framelen(self, model_index: int = 0) -> int:
        """Returns the number of channels expected by the model

        Args:
            model_index (int): The model index

        Returns:
            int: The number of input channels used by the model
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        framelen = self._kb_get_num_sensor_buffers(model_index_ctype)

        return int(framelen)

    def get_unscaled_feature_vector(self, model_index: int = 0) -> List:
        """Get the current feature vector from the model

        Args:
            model_index (int, optional): The model index. Defaults to 0.
            feature_vector_buffer_size (int, optional): The size of the array to use for getting the feature vector (This should be equal to or greater the size of the feature vector used by the model). Defaults to 4096.

        Returns:
            List: The models current feature vector
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        size = self._get_feature_vector_raw_size(model_index_ctype)
        feature_vector_raw_ctype = (ctypes.c_float * size)()

        self._copy_feature_vector_raw(model_index, feature_vector_raw_ctype)

        return list(feature_vector_raw_ctype)

    def get_feature_vector(self, model_index: int = 0) -> List:
        """Get the current feature vector from the model

        Args:
            model_index (int, optional): The model index. Defaults to 0.
            feature_vector_buffer_size (int, optional): The size of the array to use for getting the feature vector (This should be equal to or greater the size of the feature vector used by the model). Defaults to 4096.

        Returns:
            List: The models current feature vector
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        size = self._get_feature_vector_size(model_index_ctype)
        fv_type = self._get_feature_vector_type(model_index_ctype)
        if fv_type == 1:
            feature_vector_ctype = (ctypes.c_ubyte * size)()
        else:
            feature_vector_ctype = (ctypes.c_float * size)()

        void_pointer = ctypes.cast(feature_vector_ctype, ctypes.c_void_p)

        self._copy_feature_vector(model_index, void_pointer)

        return list(feature_vector_ctype)

    def get_segment_length(self, model_index: int = 0) -> int:
        """Get the length of the current segment

        Args:
            model_index (int, optional): The model index. Defaults to 0.

        Returns:
            int: The length of the current segment
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        segment_length = self._kb_get_segment_length(model_index_ctype)

        return segment_length

    def get_feature_bank_number(self, model_index: int = 0) -> int:
        """Get the number of feature banks this model uses

        Args:
            model_index (int, optional): The model index. Defaults to 0.

        Returns:
            int: The number of feature banks
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        feature_bank_number = self._sml_get_feature_bank_number(
            model_index_ctype,
        )

        return feature_bank_number.value

    def set_feature_vector(self, model_index: int, feature_vector: list):
        """Sets the models feature vector to the specified values

        Args:
            model_index (int): The model index
            feature_vector (list): the feature vector
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)
        feature_vector_array = (ctypes.c_ubyte * len(feature_vector))()

        for index, value in enumerate(feature_vector):
            feature_vector_array[index] = ctypes.c_ubyte(value)

        return self._set_feature_vector(
            model_index_ctype,
            ctypes.cast(feature_vector_array, ctypes.POINTER(ctypes.c_void_p)),
        )

    def recognize_feature_vector(self, model_index: int = 0) -> int:
        """Classify the feature vector that is currently in the model buffer

        Args:
            model_index (int, optional): The model index. Defaults to 0.

        Returns:
            int: the classification result
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        return self._recognize_feature_vector(model_index_ctype)

    def get_model_result(self, model_index: int = 0, tensor_size: int = 128):
        """
        Get the model tensor output for the most recent classification

        Args:
            model_index (int): the model index to use
            tensor_size (int): the size of the tensor, should be larger than the largest output_tensor size

        Returns:
            model results object for the specified model
        """
        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        model_results = self._kb_get_model_result_info(model_index_ctype)

        outputs = []
        for i in range(model_results.contents.output_tensor.contents.size):
            outputs.append(model_results.contents.output_tensor.contents.data[i])

        return outputs

    def knowledgepack(
        self, model_index: int = 0, distance_mode: int = 0, feature_list=None
    ):
        """
        Turn into a Knowledge Pack model object (only works for PME)
        """
        self.init_model()
        neuron_array = self.get_model(model_index).to_dict("records")
        class_map = self.get_class_map(model_index)

        return Model(
            neuron_array,
            class_map,
            {"distance_mode": distance_mode},
            feature_summary=feature_list,
        )

    def add_custom_pattern_to_model(self, model_index, feature_vector, category, aif):
        """
        Updates a PME model by adding the last pattern to the internal database
        with the specified category and influence field

        Args:
           model_index(int): Index of the model to update
           feature_vector(list): List of uint8 values that will be added to the database
           category(uint16): category of the vector to add
           aif(uint16): weight function for the new pattern

         Returns:
             int: 0 if model does not support dynamic updates, -1 if model cannot be updated anymore, 1 if model was successfully updated
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)
        category_ctype = ctypes.c_uint16(category)
        aif_ctype = ctypes.c_uint16(aif)

        feature_vector_array = (ctypes.c_uint8 * len(feature_vector))()

        for index, value in enumerate(feature_vector):
            feature_vector_array[index] = ctypes.c_uint8(value)

        return self._add_custom_pattern_to_model(
            model_index_ctype, feature_vector_array, category_ctype, aif_ctype
        )

    def add_last_pattern_to_model(self, model_index, category, aif):
        """
        Updates a PME model by adding the last feature vector created to the database
        with a new category and influence field

        Args:
           model_index(int): Index of the model to update
           category(uint16): category of the vector to add
           aif(uint16): weight function for the new pattern

        Returns:
            int: 0 if model does not support dynamic updates, -1 if model cannot be updated anymore, 1 if model was successfully updated
        """

        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)
        category_ctype = ctypes.c_uint16(category)
        aif_ctype = ctypes.c_uint16(aif)

        return self._add_last_pattern_to_model(
            model_index_ctype, category_ctype, aif_ctype
        )

    def score_model(self, model_index, category, silent=False):
        """
        Given the ground truth of the current feature vector, this will score the model
        internally

        Args:
           model_index(int): Index of the model to update
           category(uint16): category of the vector to add

        Returns:
           int: 0 if model does not support dynamic scoring, -1 if model cannot be scored, 1 if model was successfully scored
        """
        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)
        category_ctype = ctypes.c_uint16(category)

        res = None
        with pipes() as (out, _):
            res = self._score_model(model_index_ctype, category_ctype)

        if silent:
            print(out.read())

        return res

    def retrain_model(self, model_index: int = 0):
        """
        After a model has been scored, this will retrain the model according
        to the models online learning approach

        Args:
           model_index(int): Index of the model to update

        Returns:
           int: 0 if model does not support dynamic scoring, 1 if model was scored
        """
        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        ret = self._retrain_model(model_index_ctype)

        if ret == 0:
            print("Retraining is not supported/enabled for this model.")

        return ret

    def get_model_score(self, model_index):
        if not self._initialized():
            return

        model_index_ctype = ctypes.c_int(model_index)

        with pipes() as (out, _):
            self._print_model_score(model_index_ctype)

        model_scores = []
        for line in out.read().split("\n")[:-1]:
            model_scores.append(json.loads(line))

        cats = [str(x) for x in range(1, len(DataFrame(model_scores).columns) - 1)]

        return DataFrame(model_scores)[["ID", "ERR"] + cats].style.apply(_color, axis=1)

    def run_and_score_model(self, data_sample, category, model_index=0):
        """
        Runs a PME model and updates the internal model score.
        """

        ret = self.run_model(data_sample, model_index)

        if ret is None:
            return

        if ret >= 0:
            print(f"Class: {ret}")
            if ret > 0:  # only retrain if greater than 0
                score_ret = self.score_model(model_index, category)
                if score_ret == 0:
                    print("Retraining is not supported for this model.")
            self.reset_model(model_index)

            return self.get_model_score(model_index)

        return -1

    def run_and_score_model_on_segment(self, segment, category, model_index=0):
        """
        Run a PME model and updates the internal scores based on a segment of data.

        (Warning: using this call will flush the models internal ring buffer. Alternating between this and run_and_score model may produce incorrect results or crashes)

        """

        ret = self.run_segment(segment, model_index)

        if ret is None:
            return

        if ret >= 0:
            print(f"Class: {ret}")
            if ret > 0:  # only retrain if greater than 0
                self.score_model(model_index, category)
            self.reset_model(model_index)

        return self.get_model_score(model_index)


def _color(val):
    color = "white"
    if val.ERR > 0:
        color = "#90ee90"
    elif val.ERR < 0:
        color = "red"
    return [f"background-color: {color}"] * len(val)
