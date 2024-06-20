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
from engine.base.calculate_statistics import StatsCalc
from library.classifiers.classifier import Classifier
from library.models import FunctionCost

PME_MAX_VECTOR_SIZE = 2048


class NonIntegerException(Exception):
    """This Exception indicates there is a non-integer feature in the feature vectors."""


class SizeError(Exception):
    """This Exception indicates there is a size mis-match. Either the number of neurons, meta data size, or vector length does not match."""


class InvalidIdError(Exception):
    """This Exception does not seem to be used."""


class LearnVectorError(Exception):
    """This indicates that the qrkLearnVector call failed."""


class WriteNeuronError(Exception):
    """This indicates that the qrkWriteNeurons call failed."""


class DLLNotFoundError(Exception):
    """This Exception indicates one of the needed dlls was not found."""


class struct_pme_result_dist_cat_id(ctypes.Structure):
    __slots__ = ["distance", "category", "pattern_id"]

    _fields_ = [
        ("distance", ctypes.c_uint16),
        ("category", ctypes.c_uint16),
        ("pattern_id", ctypes.c_uint16),
    ]


class struct_pattern(ctypes.Structure):
    __slots__ = ["vector"]

    _fields_ = [("vector", ctypes.c_uint8 * PME_MAX_VECTOR_SIZE)]


class struct_pattern_attributes(ctypes.Structure):
    __slots__ = ["influence", "category"]

    _fields_ = [
        ("influence", ctypes.c_uint16),
        ("category", ctypes.c_uint16),
    ]


class struct_pattern_scores(ctypes.Structure):
    __slots__ = ["error", "class_vector"]

    _fields_ = [
        ("error", ctypes.c_uint16),
        ("class_vector", ctypes.POINTER(ctypes.c_uint8)),
    ]


class struct_pme_classifier(ctypes.Structure):
    __slots__ = [
        "classifier_id",
        "num_patterns",
        "pattern_size",
        "max_patterrns",
        "num_classes",
        "num_channels",
        "classifier_mode",
        "norm_mode",
        "stored_patterns",
        "stored_attribs",
        "stored_scores",
    ]

    _fields_ = [
        ("classifier_id", ctypes.c_uint8),
        ("num_patterns", ctypes.c_uint16),
        ("pattern_size", ctypes.c_uint16),
        ("max_patterns", ctypes.c_uint16),
        ("num_classes", ctypes.c_uint8),
        ("num_channels", ctypes.c_uint8),
        ("classifier_mode", ctypes.c_int),
        ("norm_mode", ctypes.c_int),
        ("stored_patterns", ctypes.POINTER(struct_pattern)),
        ("stored_attributes", ctypes.POINTER(struct_pattern_attributes)),
        ("stored_scores", ctypes.POINTER(struct_pattern_scores)),
    ]


class PME(Classifier):
    """
    Base class for interfacing with PME.
    """

    CLASSIF_MODE_RBF = 0
    CLASSIF_MODE_KNN = 1
    NUM_CHANNELS = 1

    CLASSIF_MODES = [CLASSIF_MODE_RBF, CLASSIF_MODE_KNN]
    DIST_MODE_L1 = 0
    DIST_MODE_LSUP = 1
    DIST_MODEL_DTW = 2
    MAX_MAX_AIF = 0x4000  # 0x4000 = 16384 (16k)
    MIN_MIN_AIF = 0x2
    MAX_MIN_AIF = MAX_MAX_AIF - 1
    MIN_MAX_AIF = MIN_MIN_AIF + 1
    MAX_RESPONSES = 255

    def __init__(self, save_model_parameters=True, config=None):
        super(PME, self).__init__(
            save_model_parameters=save_model_parameters, config=config
        )

        clf_lib = CDLL(os.path.join(settings.CLASSIFIER_LIBS, "libpmeclassifier.so"))

        self.__reset_pattern_database = clf_lib.pme_flush_model
        self.__reset_pattern_database.argtypes = [ctypes.c_int32]
        self.__reset_pattern_database.restype = None

        self.__pme_init = clf_lib.pme_init
        self.__pme_init.argtypes = [
            ctypes.POINTER(struct_pme_classifier),
            ctypes.c_uint8,
        ]
        self.__pme_init.restype = ctypes.c_int8

        self.__pme_recognize_vector = clf_lib.pme_simple_submit_pattern_set_result
        self.__pme_recognize_vector.argtypes = [
            ctypes.c_uint8,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.POINTER(struct_pme_result_dist_cat_id),
        ]
        self.__pme_recognize_vector.restype = None

        self.__pme_learn_pattern = clf_lib.pme_learn_pattern
        self.__pme_learn_pattern.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint16,
            ctypes.c_uint16,
        ]
        self.__pme_learn_pattern.restype = ctypes.c_int

        self.__pme_get_number_patterns = clf_lib.pme_get_number_patterns
        self.__pme_get_number_patterns.argtypes = [ctypes.c_int]
        self.__pme_get_number_patterns.restype = ctypes.c_int

        self.__pme_add_new_pattern = clf_lib.pme_add_new_pattern
        self.__pme_add_new_pattern.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_uint16,
            ctypes.c_uint16,
        ]
        self.__pme_add_new_pattern.restype = ctypes.c_int

        self.max_aif = 16384
        self.min_aif = 1

    def initialize_model(self, max_pattern_count, max_vector_size):
        if max_vector_size > PME_MAX_VECTOR_SIZE:
            raise SizeError("Size of vector is too large.")

        stored_patterns = (struct_pattern * max_pattern_count)()
        stored_attributes = (struct_pattern_attributes * max_pattern_count)()
        pattern_vector = ctypes.c_uint8 * PME_MAX_VECTOR_SIZE

        for i in range(max_pattern_count):
            pattern = struct_pattern()
            vector = pattern_vector()

            for j in range(0, max_vector_size):
                vector[j] = ctypes.c_uint8(0)

            pattern.vector = vector

            stored_patterns[i] = pattern

            pattern_attributes = struct_pattern_attributes()
            pattern_attributes.category = ctypes.c_uint16()
            pattern_attributes.influence = ctypes.c_uint16()

            stored_attributes[i] = pattern_attributes

        self.pme_classifiers = (struct_pme_classifier * 1)()

        pme_classifier = struct_pme_classifier()
        pme_classifier.classifier_id = 0
        pme_classifier.num_patterns = 0
        pme_classifier.max_patterns = max_pattern_count
        pme_classifier.pattern_size = max_vector_size
        pme_classifier.num_classes = 100
        pme_classifier.classifier_mode = self.CLASSIF_MODE_RBF
        pme_classifier.norm_mode = self.DIST_MODE_L1
        pme_classifier.num_channels = self.NUM_CHANNELS
        pme_classifier.stored_patterns = stored_patterns
        pme_classifier.stored_attributes = stored_attributes

        self.pme_classifiers[0] = pme_classifier

        return self.__pme_init(self.pme_classifiers, 1)

    def _print_settings(self, classifier_id=0):
        print("norm_mode", self.pme_classifiers[classifier_id].norm_mode)
        print("classifier_mode", self.pme_classifiers[classifier_id].classifier_mode)
        print("num_channels", self.pme_classifiers[classifier_id].num_channels)
        print("num_patterns", self.pme_classifiers[classifier_id].num_patterns)
        print("pattern_size", self.pme_classifiers[classifier_id].pattern_size)
        print("max_patterns", self.pme_classifiers[classifier_id].max_patterns)

    def _reset_pme_database(self, classifier_id=0):
        """"""
        self.__reset_pattern_database(classifier_id)

    def get_number_patterns(self, classifier_id=0):
        return self.__pme_get_number_patterns(classifier_id)

    def get_max_patterns(self, classifier_id=0):
        return self.pme_classifiers[classifier_id].max_patterns

    def set_classification_mode(self, classifier_mode, classifier_id=0):
        if classifier_mode not in self.CLASSIF_MODES:
            raise Exception("Invalid Classification Mode")

        self.pme_classifiers[classifier_id].classifier_mode = classifier_mode

    def set_distance_mode(self, distance_mode, classifier_id=0):
        self.pme_classifiers[classifier_id].norm_mode = distance_mode

    def set_num_channels(self, num_channels, classifier_id=0):
        self.pme_classifiers[classifier_id].num_channels = num_channels

    def set_min_aif(self, value):
        self.min_aif = value

    def set_max_aif(self, value):
        self.max_aif = value

    def _learn_vector(self, classifier_id, vector, category):
        """Trains the Burlington model on a single training vector. This will
        learn that vector of length vector_length means Category."""

        vector_length = len(vector)

        if vector_length > self.pme_classifiers[classifier_id].pattern_size:
            raise SizeError("vector too large!")

        vector_array_type = ctypes.c_uint8 * vector_length
        vector_array = vector_array_type()
        for i in range(0, vector_length):
            vector_array[i] = ctypes.c_uint8(vector[i])

        resp = self.__pme_learn_pattern(
            classifier_id, vector_array, int(category), self.max_aif
        )

        return self.__pme_get_number_patterns(classifier_id)

    def learn_vectors(self, vectors, classifier_id=0):
        """Trains the Burlington model on a single training vector. This will
        learn that vector of length vector_length means Category."""

        for vector in vectors:
            self._learn_vector(classifier_id, vector["Vector"], vector["Category"])

        return self.__pme_get_number_patterns(classifier_id)

    def _recognize_vector(
        self, classifier_id, vector_to_recognize, desired_responses=1
    ):
        """

        # param - int classifier_id - classifier index
        # param - int array vector_to_recognize - the vector
        # param - int desired_responses - the number of neuron reponses expected
        # returns - integer - the number of neurons recongnized
        #         - boolean - was the recognition uncertain?
        """

        vector_length = len(vector_to_recognize)

        if vector_length > self.pme_classifiers[classifier_id].pattern_size:
            raise SizeError("vector too large!")

        if not all(isinstance(x, int) for x in vector_to_recognize):
            raise NonIntegerException(
                "\nFeature vector contains non integer "
                + "values. Make sure your pipeline contains a feature transform "
                + "that scales the feature vectors such as Min Max Scale."
            )

        vector_array_type = ctypes.c_uint8 * (vector_length)
        results_type = struct_pme_result_dist_cat_id * (desired_responses)

        vector_array = vector_array_type()
        results = results_type()

        for i in range(0, vector_length):
            vector_array[i] = ctypes.c_uint8(vector_to_recognize[i])

        for index in range(desired_responses):
            pme_result = struct_pme_result_dist_cat_id()

            pme_result.category = ctypes.c_uint16(0)
            pme_result.pattern_id = ctypes.c_uint16(0)
            pme_result.distance = ctypes.c_uint16(0)

            results[index] = pme_result

        self.__pme_recognize_vector(classifier_id, vector_array, results)

        for i in range(0, desired_responses):
            if results[i].category == 65535:  # unknown response
                results[i].category = 0

        return results

    def recognize_vectors(
        self, vectors_to_recognize, classifier_id=0, include_predictions=False
    ):
        """
        Format for the VectorList
        [{'Vector':[], 'Category': number,
        'DesiredResponses': number,
        'DistanceVector': this [] gets filled in by the code,
        'CategoryVector': this [] gets filled in by the code,
        'NIDVector': this [] gets filled in by the code}]
        """

        for i in range(0, len(vectors_to_recognize)):
            results = self._recognize_vector(
                classifier_id,
                vectors_to_recognize[i]["Vector"],
                vectors_to_recognize[i]["DesiredResponses"],
            )

            vectors_to_recognize[i]["DistanceVector"] = [
                int(x.distance) for x in results
            ]
            vectors_to_recognize[i]["CategoryVector"] = [
                int(x.category) for x in results
            ]
            vectors_to_recognize[i]["NIDVector"] = [int(x.pattern_id) for x in results]

        # return vectors_to_recognize
        return self._compute_classification_statistics(
            vectors_to_recognize, include_predictions=include_predictions
        )

    def dump_model(self, classifier_id=0):
        """ """

        model_parameters = []
        for i in range(self.__pme_get_number_patterns(classifier_id)):
            tmp_pattern = {}
            tmp_pattern["Vector"] = list(
                self.pme_classifiers[classifier_id]
                .stored_patterns[i]
                .vector[: self.pme_classifiers[classifier_id].pattern_size]
            )
            tmp_pattern["Category"] = int(
                self.pme_classifiers[classifier_id].stored_attributes[i].category
            )
            tmp_pattern["AIF"] = int(
                self.pme_classifiers[classifier_id].stored_attributes[i].influence
            )
            tmp_pattern["Identifier"] = i

            model_parameters.append(tmp_pattern)

        return model_parameters

    def load_model(self, model_parameters, classifier_id=0):
        """Load a database of patterns into the pme"""

        self._reset_pme_database(classifier_id)

        vector_array_type = ctypes.c_uint8 * (
            self.pme_classifiers[classifier_id].pattern_size
        )

        for pattern in model_parameters:
            vector_array = vector_array_type()

            for i, value in enumerate(pattern["Vector"]):
                vector_array[i] = ctypes.c_uint8(value)

            self.__pme_add_new_pattern(
                classifier_id, vector_array, pattern["Category"], pattern["AIF"]
            )

        return self.pme_classifiers[0].num_patterns

    def compute_cost(self, model_parameters):
        total_flash_size = 124
        total_sram_size = 0
        total_cycle_count = 0
        total_stack_size = 0
        f_cost = FunctionCost.objects.get(uuid="925c8b2f-9162-4538-9300-53d409b34f6b")

        if f_cost is None:
            return {}

        f_cost_dict = model_to_dict(
            f_cost, fields=["flash", "sram", "stack", "latency", "cycle_count"]
        )
        if len(model_parameters) == 0:
            # raise ValidationError("No patterns were added to model!")
            f_cost_dict["flash"] = 9999999
            f_cost_dict["cycle_count"] = 9999999
            f_cost_dict["sram"] = 9999999
            f_cost_dict["stack"] = 9999999
            return f_cost_dict

        number_of_features = len(model_parameters[0]["Vector"])
        num_neurons = len(model_parameters)

        total_flash_size += (num_neurons * number_of_features) + (15 * num_neurons)
        total_cycle_count += 1100 * number_of_features
        total_sram_size += int(f_cost_dict["sram"])
        total_stack_size += int(f_cost_dict["stack"])

        f_cost_dict["flash"] = total_flash_size
        f_cost_dict["cycle_count"] = total_cycle_count
        f_cost_dict["sram"] = total_sram_size
        f_cost_dict["stack"] = total_stack_size

        return f_cost_dict

    def _compute_classification_statistics(
        self, recognized_vectors, include_predictions=False
    ):
        unknown = 0
        properclass = 0
        improperclass = 0
        actual_category_counts = {}
        recognized_category_counts = {}  # based only on the first element in vector
        neuron_counts = {}
        confusion_matrix = {}
        temp = {}
        all_cats = set()
        allow_unknown = True

        # Create a confusion matrix
        # Initialize it
        nrns = self.dump_model()
        for v in nrns:
            all_cats.add(int(v["Category"]))
        for v in recognized_vectors:
            all_cats.add(int(v["Category"]))
        all_cats = sorted(all_cats)

        for v in all_cats:
            temp[v] = 0
        temp["UNC"] = 0
        temp["UNK"] = 0
        for v in all_cats:
            confusion_matrix[v] = dict(temp)

        for v in recognized_vectors:
            if v["CategoryVector"][0] == 0:
                # Report unknowns
                unknown = unknown + 1
                confusion_matrix[int(v["Category"])]["UNK"] += 1
            else:
                confusion_matrix[int(v["Category"])][v["CategoryVector"][0]] += 1
                if v["CategoryVector"][0] == int(v["Category"]):
                    properclass += 1
                else:
                    improperclass += 1

            if v["Category"] in actual_category_counts:
                actual_category_counts[v["Category"]] = (
                    actual_category_counts[v["Category"]] + 1
                )
            else:
                actual_category_counts[v["Category"]] = 1

            # These metrics are not too important yet, but might need to be updated for multiple firing neurons
            if v["CategoryVector"][0] in recognized_category_counts:
                recognized_category_counts[v["CategoryVector"][0]] = (
                    recognized_category_counts[v["CategoryVector"][0]] + 1
                )
            else:
                recognized_category_counts[v["CategoryVector"][0]] = 1

            if v["NIDVector"][0] in neuron_counts:
                neuron_counts[v["NIDVector"][0]] = neuron_counts[v["NIDVector"][0]] + 1
            else:
                neuron_counts[v["NIDVector"][0]] = 1

        # Gather truth and prediction values from recognized vectors
        y_true = [int(x["Category"]) for x in recognized_vectors]
        y_pred = [int(x["CategoryVector"][0]) for x in recognized_vectors]
        y_dist = [int(x["DistanceVector"][0]) for x in recognized_vectors]
        y_nid = [int(x["NIDVector"][0]) for x in recognized_vectors]

        # Calculate statistics from confusion matrix and y_true, y_pred

        if self._config:
            class_map = self._config.get("class_map", None)
        else:
            class_map = None

        stats_obj = StatsCalc(
            y_true,
            y_pred,
            confusion_matrix,
            allow_unknown,
            class_map=class_map,
        )
        stats_obj.calc_all_metrics()
        statistics = {
            "UnknownPercent": 100 * float(unknown) / float(len(recognized_vectors)),
            "ProperClassificationPercent": 100
            * float(properclass)
            / float(len(recognized_vectors)),
            "ImproperClassificationPercent": 100
            * float(improperclass)
            / float(len(recognized_vectors)),
            "VectorInTestSet": len(recognized_vectors),
            # assumption is that they are all the same size
            "FeaturesPerVector": len(recognized_vectors[0]["Vector"]),
            "NeuronsUsed": self.get_number_patterns(),
            "NeuronsUsedPercent": 100
            * self.get_number_patterns()
            / float(len(neuron_counts)),
            "ActualCategoryCounts": actual_category_counts,
            "RecognizedCategoryCounts": recognized_category_counts,
            "NeuronFireCount": neuron_counts,
            "ConfusionMatrix": confusion_matrix,
            "accuracy": stats_obj.accuracy,
            "sensitivity": stats_obj.sensitivity,
            "positive_predictive_rate": stats_obj.positive_predictive_rate,
            "f1_score": stats_obj.f1_score,
            "precision": stats_obj.precision,
            "specificity": stats_obj.specificity,
            "y_true": None,
            "y_pred": None,
        }

        if include_predictions:
            statistics.update(
                {
                    "y_true": y_true,
                    "y_pred": y_pred,
                    "distance": y_dist,
                    "neuron_id": y_nid,
                }
            )

        return statistics
