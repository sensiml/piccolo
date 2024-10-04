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

import logging

from datamanager.datasegments import dataframe_to_datasegments
from datamanager.models import PipelineExecution
from engine.base.pipeline_utils import (
    clean_feature_cascade,
    get_data_columns,
    get_group_columns,
    get_max_vector_size,
    get_type_index,
    make_recognition_pipeline,
)
from engine.base.temp_cache import TempCache
from engine.base.utils import return_labels_to_original_values
from library.classifiers.bonsai import Bonsai
from library.classifiers.boosted_tree_ensemble import BoostedTreeEnsemble
from library.classifiers.decision_tree_ensemble import DecisionTreeEnsemble
from library.classifiers.linear_regression import LinearRegression
from library.classifiers.pme import PME
from library.classifiers.tensorflow_micro import TensorFlowMicro
from engine.parallelexecutionengine import ParallelExecutionEngine
from library.models import CompilerDescription, ProcessorDescription
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class RecognitionError(Exception):
    pass


class RecognitionEngine(object):
    def __init__(
        self,
        task_id,
        user,
        project_id,
        reco_data,
        knowledgepack=None,
        config=None,
        start_step=None,
        stop_step=False,
        segmenter=True,
        compare_labels=True,
        overwrite_labels=True,
        feature_table=None,
    ):
        self.task_id = task_id
        self.recognition_data = reco_data
        self.neuron_array = knowledgepack.neuron_array
        self.project_id = project_id
        self.kp = knowledgepack
        self.stop_step = stop_step
        self.start_step = start_step
        self.segmenter = segmenter
        self.compare_labels = compare_labels
        self.overwrite_labels = overwrite_labels
        self.classifier_type = knowledgepack.pipeline_summary[-1]["classifiers"][0][
            "name"
        ]
        self.class_map = (
            knowledgepack.class_map if knowledgepack and knowledgepack.class_map else {}
        )
        self.reverse_map = {v: k for k, v in self.class_map.items()}

        self.feature_table = feature_table
        self.initialize_classifier(config)
        self._user = user
        self._team_id = str(user.teammember.team.uuid)

    def initialize_classifier(self, config):
        if self.classifier_type in ["PME"]:
            self.classifier = PME()
            # There is an off-by-one problem if you use the exact number!
            self.max_neuron_count = len(self.neuron_array) + 1
            self.max_vector_size = get_max_vector_size(self.neuron_array)
            self.classifier.initialize_model(
                self.max_neuron_count, self.max_vector_size
            )
            self.classifier.load_model(self.neuron_array)

            # RBF and L1 are the defaults. Set KNN and LSup if requested.
            if config:
                if (
                    "classification_mode" in config
                    and config["classification_mode"].lower() == "knn"
                ):
                    self.classifier.set_classification_mode(1)
                if (
                    "distance_mode" in config
                    and config["distance_mode"].lower() == "lsup"
                ):
                    self.classifier.set_distance_mode(1)
                if (
                    "distance_mode" in config
                    and config["distance_mode"].lower() == "dtw"
                ):
                    self.classifier.set_distance_mode(2)

            else:
                self.classifier.set_classification_mode(
                    self.kp.device_configuration["classification_mode"]
                )
                self.classifier.set_distance_mode(
                    self.kp.device_configuration["distance_mode"]
                )

        elif self.classifier_type == "Bonsai":
            self.classifier = Bonsai()
            self.classifier.load_model(self.neuron_array)

        elif self.classifier_type == "Decision Tree Ensemble":
            self.classifier = DecisionTreeEnsemble()
            self.classifier.load_model(self.neuron_array)

        elif self.classifier_type in [
            "TF Micro",
            "TensorFlow Lite for Microcontrollers",
        ]:
            self.classifier = TensorFlowMicro()
            self.classifier.load_model(self.neuron_array)

        elif self.classifier_type == "Boosted Tree Ensemble":
            self.classifier = BoostedTreeEnsemble()
            self.classifier.load_model(self.neuron_array)

        elif self.classifier_type == "Linear Regression":
            self.classifier = LinearRegression()
            self.classifier.load_model(self.neuron_array)

        else:
            raise Exception("Classifier {} not supported".format(self.classifier_type))

    def _add_mapped_category_vector(self, response_dict):
        if self.kp and self.class_map:
            response_dict["MappedCategoryVector"] = []
            if isinstance(response_dict["CategoryVector"], int):
                if str(response_dict["CategoryVector"]) in self.class_map.keys():
                    response_dict["MappedCategoryVector"] = self.class_map[
                        str(response_dict["CategoryVector"])
                    ]
            if isinstance(response_dict["CategoryVector"], list):
                for i, _ in enumerate(response_dict["CategoryVector"]):
                    if str(response_dict["CategoryVector"][i]) in self.class_map.keys():
                        response_dict["MappedCategoryVector"].append(
                            self.class_map[str(response_dict["CategoryVector"][i])]
                        )
        return response_dict

    def reco_many_vector(self, with_labels=False):
        """Recognize classes of multiple feature vectors in a list of dictionaries."""
        dict_recognition_vectors = self.recognition_data

        for i in range(0, len(dict_recognition_vectors)):
            if "DesiredResponses" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["DesiredResponses"] = 1
            if "Context" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["Context"] = 1
            if "CategoryVector" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["CategoryVector"] = []
            if "DistanceVector" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["DistanceVector"] = []
            if "NIDVector" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["NIDVector"] = []
            if "Uncertain" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["Uncertain"] = None
            if "Category" not in dict_recognition_vectors[i]:
                dict_recognition_vectors[i]["Category"] = 1

        stats = self.classifier.recognize_vectors(
            dict_recognition_vectors, include_predictions=True
        )

        if self.kp and self.class_map:
            stats = return_labels_to_original_values(stats, self.class_map)

        # reco_vectors in kb_engine would return a vector
        # with the same key. emulate that functionality
        list_results = []
        for d in dict_recognition_vectors:
            d = self._add_mapped_category_vector(d)
            list_results.append(
                {
                    key: d.get(key, None)
                    for key in (
                        "CategoryVector",
                        "DistanceVector",
                        "NIDVector",
                        "MappedCategoryVector",
                    )
                }
            )

        dict_results = {"vectors": list_results}
        if with_labels:
            dict_results["metrics"] = stats

        return dict_results

    def reco_series(self):
        """Recognize class of a single set of raw sensor streams. Uses the
        knowledgepack to create a pipeline that transforms data into features
        and applies the model's recognition routine."""

        logger.userlog(
            {
                "message": "Recognition Pipeline Submitted",
                "log_type": "PID",
                "UUID": str(self.kp.uuid),
                "task_id": self.task_id,
            }
        )

        (recognition_pipeline, _, _) = make_recognition_pipeline(
            self.kp.sandbox.project, segmenter=self.segmenter, **self.kp.__dict__
        )

        logger.userlog(
            {
                "message": "Initial Recognition Pipeline",
                "data": recognition_pipeline,
                "log_type": "PID",
                "UUID": str(self.kp.uuid),
                "task_id": self.task_id,
            }
        )

        # Insert stored transform variables
        for i in recognition_pipeline:
            for parameter in ["group_columns", "passthrough_columns"]:
                if parameter in i["inputs"]:
                    for column in [
                        c
                        for c in i["inputs"][parameter]
                        if c not in self.recognition_data.columns
                    ]:
                        if column not in ["SegmentID", "CascadeID"]:
                            self.recognition_data[column] = -1

        if not self.compare_labels and self.overwrite_labels:
            label_column = self.kp.pipeline_summary[-1]["label_column"]
            self.recognition_data[label_column] = -1

        # Provide the feature summary for correctly naming the dynamically generated features
        fg_index = get_type_index(recognition_pipeline, "generatorset")
        recognition_pipeline[fg_index]["feature_summary"] = clean_feature_cascade(
            self.kp.feature_summary
        )

        # Add metadata group columns to output
        generator_set = recognition_pipeline[fg_index]

        # a stop step to return
        if self.stop_step != False:
            recognition_pipeline = recognition_pipeline[: self.stop_step]

        if self.start_step:
            recognition_pipeline = recognition_pipeline[self.start_step :]

        if recognition_pipeline:
            # Create an ExecutionEngine, save the dataframe to temp, and execute the altered pipeline
            execution_engine = ParallelExecutionEngine(
                task_id=self.task_id,
                user=self._user,
                project_id=self.project_id,
                sandbox=None,
                execution_type=PipelineExecution.ExecutionTypeEnum.RECOGNITION,
                execution_id=str(self.kp.uuid),
            )

            # set feature table input to None for the first step if there is one
            if self.feature_table is not None:
                TempCache(str(self.kp.uuid)).write_file(
                    self.feature_table, "temp.features"
                )
                recognition_pipeline[0]["feature_table"] = "temp.features"

                input_data = TempCache(str(self.kp.uuid)).write_file(
                    self.recognition_data, "temp.raw"
                )
            else:
                recognition_pipeline[0]["feature_table"] = None
                datasegments = dataframe_to_datasegments(
                    self.recognition_data,
                    group_columns=get_group_columns(
                        self.kp.pipeline_summary, self.project_id
                    ),
                    data_columns=get_data_columns(
                        self.kp.pipeline_summary, self.project_id
                    ),
                )

                input_data = TempCache(str(self.kp.uuid)).write_file(
                    datasegments, "temp.raw"
                )

            recognition_pipeline[0]["inputs"]["input_data"] = input_data

            logger.userlog(
                {
                    "message": "Modified Recognition Pipeline",
                    "data": recognition_pipeline,
                    "log_type": "PID",
                    "UUID": str(self.kp.uuid),
                    "task_id": self.task_id,
                }
            )

            try:
                execution_engine.execute(
                    recognition_pipeline,
                    caching=False,
                    compute_cost=False,
                    store_errors=False,
                )
            except Exception as e:
                execution_engine._temp.clean_up_temp()
                raise e

            results = execution_engine.get_result()
            execution_summary = execution_engine.execution_summary

            if self.stop_step != False:
                return {
                    "results": results.to_json(),
                    "summary": [],
                    "execution_summary": execution_summary,
                }

        else:
            logger.userlog(
                {
                    "message": "Empty Recognition Pipeline",
                    "data": recognition_pipeline,
                    "log_type": "PID",
                    "UUID": str(self.kp.uuid),
                    "task_id": self.task_id,
                }
            )

            execution_summary = None
            results = self.recognition_data

        # Ensure that features are in the right order
        ordered_columns = [f["Feature"] for f in self.kp.feature_summary]
        feature_vectors = results[ordered_columns]

        # Recognize the vectors with or without ground truth labels
        with_labels = False
        label_column = self.kp.pipeline_summary[-1]["label_column"]

        if self.compare_labels and self.overwrite_labels:
            if label_column not in results.columns:
                raise Exception("Label column was not provided with dataset.")

            if set(results[label_column]) == set([""]):
                raise Exception("No labels in label column.")

            with_labels = True
            categories = results[label_column]

            check_categories(categories, self.reverse_map)

            self.recognition_data = [
                {"Vector": vector, "Category": self.reverse_map[categories[i]]}
                for i, vector in enumerate(feature_vectors.values.tolist())
            ]
        else:
            self.recognition_data = [
                {"Vector": vector}
                for i, vector in enumerate(feature_vectors.values.tolist())
            ]

        result_dict = self.reco_many_vector(with_labels)

        # Add metadata group columns to output
        if len(generator_set["inputs"]["group_columns"]):
            columns = [
                col
                for col in generator_set["inputs"]["group_columns"]
                if set(results[col]) != set([""])
            ]
            metadata = results[columns]

            for i, vector in enumerate(result_dict["vectors"]):
                for column in metadata.columns:
                    if metadata[column].dtype == "int64":
                        result_dict["vectors"][i][column] = int(metadata.loc[i, column])
                    elif metadata[column].dtype == "float64":
                        result_dict["vectors"][i][column] = float(
                            metadata.loc[i, column]
                        )
                    else:
                        result_dict["vectors"][i][column] = metadata.loc[i, column]

        return {
            "results": result_dict,
            "summary": [],
            "execution_summary": execution_summary,
        }

    # This is kind of sloppy, and should be improved in the future to take more parameters
    def reco_kb_pipeline(self, kb_description):
        from codegen.codegen_gcc_generic import GCCGenericCodeGenerator

        # device_config = {"target_platform": 4, "debug": True, "sample_rate": 100}
        device_config = {
            "target_platform": "26eef4c2-6317-4094-8013-08503dcd4bc5",
            "debug": True,
            "sample_rate": 100,
            "application": "AI Model Runner",
            "target_processor": ProcessorDescription.objects.get(
                uuid="822581d2-8845-4692-bcac-4446d341d4a0"
            ),
            "target_compiler": CompilerDescription.objects.get(
                uuid="62aabe7e-4f5d-4167-a786-072e4a8dc158"
            ),
            "nn_inference_engine":'nnom'
        }

        logger.userlog(
            {
                "message": "Recognition Emulator Submitted",
                "log_type": "PID",
                "UUID": str(self.kp.uuid),
                "task_id": self.task_id,
            }
        )

        kb_pipeline_sim = GCCGenericCodeGenerator(
            kb_description,
            self.kp.uuid,
            self.task_id,
            device_config,
            "recognize",
            test_data=self.recognition_data,
            target_os="linux",
        )

        return kb_pipeline_sim.recognize()

    def recognize(self, platform="kbengine", kb_description=None):

        if isinstance(self.recognition_data, list):
            if (
                "Category" in self.recognition_data[0]
                and self.recognition_data[0]["Category"]
            ):
                return self.reco_many_vector(True)
            else:
                return self.reco_many_vector(False)
        elif isinstance(self.recognition_data, DataFrame):
            if platform in ["emulator"]:
                return self.reco_kb_pipeline(kb_description)
            else:
                return self.reco_series()
        else:
            raise Exception("Unexpected Input")


def check_categories(categories, reverse_map):
    # check that all categories are in the map and add them if they are not
    max([int(v) for k, v in reverse_map.items()])
    for cat in categories.unique():
        if cat not in reverse_map.keys():
            raise Exception(
                "Category {} is not a valid category for this moel".format(cat)
            )
