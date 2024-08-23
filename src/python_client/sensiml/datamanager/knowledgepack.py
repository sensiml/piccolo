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

from __future__ import annotations
import copy
import json
import logging
import os
import re
import sys
import warnings
from time import sleep

import numpy as np
import pandas as pd
from numpy import int64
from pandas import DataFrame

import sensiml.base.utility as utility
from sensiml.datamanager.clientplatformdescription import ClientPlatformDescription
from sensiml.datamanager.confusion_matrix import (
    ConfusionMatrix,
)
from sensiml.datamanager.deviceconfig import DeviceConfig
from sensiml.datamanager.featurefile import FeatureFile
from sensiml.method_calls.functioncall import FunctionCall
from sensiml.visualize.knowledgepack_visualize_mixin import VisualizeMixin
from requests import Response


from typing import TYPE_CHECKING, Optional, Tuple


if TYPE_CHECKING:
    from sensiml.connection import Connection

logger = logging.getLogger(__name__)


def render_confusion_matrix(cm):
    GT_txt = "GroundTruth_Total"
    keys = [k for k, v in cm.items()]
    gt = [cm[k][GT_txt] for k in keys]
    df = pd.DataFrame.from_dict(
        {k: [cm[k][_] for _ in keys] for k in keys}, orient="index"
    )
    df.columns = keys
    df[GT_txt] = gt

    return df[keys + [GT_txt]]


class KnowledgePackException(Exception):
    """Base exception for KnowledgePacks"""


class KnowledgePack(VisualizeMixin):
    """Base class for a KnowledgePack"""

    def __init__(
        self, connection: Connection, project_uuid: str, sandbox_uuid: str = ""
    ):
        """Initializes a KnowledgePack instance

        Args:
            project (Project): the parent project of the KnowledgePack
            sandbox (Sandbox): the parent sandbox of the KnowledgePack
        """
        self._uuid = ""
        self._connection = connection
        self._project_uuid = project_uuid
        self._sandbox_uuid = sandbox_uuid
        self._feature_file_uuid = None
        self._project_name = ""
        self._sandbox_name = ""
        self._configuration_index = ""
        self._name = ""
        self._model_index = ""
        self._execution_time = ""
        self._neuron_array = ""
        self._model_results = ""
        self._pipeline_summary = ""
        self._query_summary = ""
        self._feature_summary = ""
        self._device_configuration = ""
        self._transform_summary = ""
        self._knowledgepack_summary = ""
        self._knowledgepack_description = ""
        self._sensor_summary = ""
        self._cost_summary = ""
        self._class_map = ""
        self._device_config = DeviceConfig()
        self._feature_file_cache = None
        self._training_metrics = None

    @property
    def uuid(self) -> str:
        return self._uuid

    @property
    def sandbox_uuid(self) -> str:
        return self._sandbox_uuid

    @property
    def project_uuid(self) -> str:
        return self._project_uuid

    @property
    def sandbox_name(self) -> str:
        return self._sandbox_name

    @property
    def project_name(self) -> str:
        return self._project_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def execution_time(self) -> int:
        return self._execution_time

    @property
    def neuron_array(self) -> dict:
        """The model's neuron array"""
        return self._neuron_array

    @property
    def model_parameters(self) -> dict:
        """The model's parameters"""
        return self._neuron_array

    @property
    def model_configuration(self) -> dict:
        """Model Configuration"""
        return self.device_configuration

    @property
    def model_results(self) -> dict:
        """The model results associated with the KnowledgePack (in JSON form)"""
        return self._model_results

    @property
    def training_metrics(self) -> dict:
        """The training metrics associated with the KnowledgePack"""
        return self.model_parameters.get("training_metrics", None)

    @property
    def pipeline_summary(self) -> list[dict]:
        """A summary specification of the pipeline which created the KnowledgePack"""
        return self._pipeline_summary

    @property
    def query_summary(self) -> dict:
        """A summary specification of the query used by the pipeline which created the KnowledgePack"""
        return self._query_summary

    @property
    def feature_summary(self) -> dict:
        """A summary of the features generated by the KnowledgePack"""
        return self._feature_summary

    @property
    def configuration_index(self) -> int:
        return self._configuration_index

    @property
    def model_index(self) -> int:
        return self._model_index

    @property
    def device_configuration(self) -> dict:
        return self._device_configuration

    @property
    def transform_summary(self) -> dict:
        """A summary of transform parameters used by the KnowledgePack"""
        return self._transform_summary

    @property
    def sensor_summary(self) -> dict:
        """A summary of sensor streams used by the KnowledgePack"""
        return self._sensor_summary

    @property
    def class_map(self) -> dict:
        """A summary of the integer classes/categories used by the KnowledgePack and the corresponding application
        categories"""
        return self._class_map

    @property
    def reverse_class_map(self) -> dict:
        """A summary of the category/integer class used by the KnowledgePack and the corresponding application
        categories"""
        if self._class_map:
            return {v: k for k, v in self._class_map.items()}
        return {}

    @property
    def feature_statistics(self) -> DataFrame:
        if self._model_results.get("metrics", None) is None:
            return None

        return DataFrame(self._model_results["feature_statistics"]["validation"])

    def feature_statistics_by_metric(self, metric: str = "validation"):
        if self._model_results.get("feature_statistics", None) is None:
            return None
        return DataFrame(self._model_results["feature_statistics"][metric])

    @property
    def confusion_matrix(self) -> ConfusionMatrix:
        if self._model_results.get("metrics", None) is None:
            return ConfusionMatrix(self._model_results)

        return ConfusionMatrix(self._model_results["metrics"]["validation"])

    def confusion_matrix_by_metric(self, metric="validation") -> ConfusionMatrix:
        if self._model_results.get("metrics", None) is None:
            return ConfusionMatrix(self._model_results)

        return ConfusionMatrix(self._model_results["metrics"][metric])

    @property
    def cost_dict(self) -> dict:
        """A summary of device costs incurred by the KnowledgePack"""
        return self._cost_summary

    @property
    def knowledgepack_description(self) -> dict:
        """Description of knowledgepack. It is for the hierarchical model which created by Autosense"""
        return self._knowledgepack_description

    @property
    def knowledgepack_summary(self) -> dict:
        """A summary of device costs incurred by the KnowledgePack"""
        return self._knowledgepack_summary

    @property
    def cost_report(self) -> str:
        """A printed tabular report of the device cost incurred by the KnowledgePack"""
        return self.get_report("cost")

    @property
    def cost_report_json(self) -> str:
        """A JSON report of the Knowledge Pack cost summary"""
        return self.get_report("json")

    def cost_resource_summary(
        self,
        processor_uuid: Optional[str] = None,
        hardware_accelerator: Optional[str] = None,
    ):
        """A summary of resources and time needed in a classification from a Knowledge Pack"""
        return self.get_report(
            "resource_summary",
            processor_uuid=processor_uuid,
            hardware_accelerator=hardware_accelerator,
        )

    def get_report(
        self,
        report_type: str,
        processor_uuid: Optional[str] = None,
        hardware_accelerator: Optional[str] = None,
    ):
        """Sends a request for a report to the server and returns the result.

        Args:
            report_type (string): string name of report, ex: 'cost'

        Returns:
            (string): string representation of desired report

        """
        url = "project/{0}/knowledgepack/{1}/report/{2}/".format(
            self._project_uuid, self.uuid, report_type
        )

        if report_type == "cost":
            response = self._connection.request(
                "get", url, headers={"Accept": "text/plain"}
            )
            return response.text
        elif report_type == "json":
            response = self._connection.request(
                "get", url, headers={"Accept": "application/json"}
            )
            return response.json()
        elif report_type == "resource_summary":
            params = {}
            if processor_uuid:
                params["processor_uuid"] = processor_uuid
            if hardware_accelerator:
                params["accelerator"] = hardware_accelerator

            url = "project/{0}/knowledgepack/{1}/report/{2}/".format(
                self._project_uuid, self.uuid, report_type
            )

            response = self._connection.request(
                "get", url, params=params, headers={"Accept": "application/json"}
            )
            return response.json()

    def recognize_features(self, data: dict) -> DataFrame:
        """Sends a single vector of features to the KnowledgePack for recognition.

        Args:
            data (dict): dictionary containing

              - a feature vector in the format 'Vector': [126, 32, 0, ...]
              - 'DesiredResponses' indicating the number of neuron responses to return

        Returns:
            (dict): dictionary containing

            - CategoryVector (list): numerical categories of the neurons that fired
            - MappedCategoryVector (list): original class categories of the neurons that fired
            - NIDVector (list): ID numbers of the neurons that fired
            - DistanceVector (list): distances of the feature vector to each neuron that fired

        """
        url = f"project/{self._project_uuid}/sandbox/{self._sandbox_uuid}/knowledgepack/{self.uuid}/recognize_features/"

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return response_data

    def recognize_signal(
        self,
        capture: Optional[str] = None,
        datafile: Optional[str] = None,
        test_plan: Optional[str] = None,
        stop_step: Optional[int] = False,
        segmenter: bool = True,
        platform: str = "emulator",
        get_result: bool = True,
        kb_description: Optional[dict] = None,
        compare_labels: bool = False,
        renderer: Optional[str] = None,
    ) -> DataFrame:
        """Sends a DataFrame of raw signals to be run through the feature generation pipeline and recognized.

        Args:
            capturefile (str): The name of a file uploaded through the data capture lab
            datafile (str): The name of an uploading datafile
            platform (str): "emulator" or "cloud". The "emulator" will run compiled c code giving device exact results,
                 the cloud runs similarly to training providing more flexibility in returning early results by setting the
                 stop step.
            stop_step (int): for debugging, if you want to stop the pipeline at a particular step, set stop_step
              to its index
            compare_labels (bool): If there are labels for the input dataframe, use them to create a confusion matrix
            segmenter (bool or FunctionCall): to suppress or override the segmentation algorithm in the original
              pipeline, set this to False or a function call of type 'segmenter' (defaults to True)
            lock (bool, True): If True, waits for the result to return before releasing the ipython cell.

        Returns:
            (dict): dictionary of results and summary statistics from the executed pipeline and recognition
        """
        url = f"project/{self._project_uuid}/sandbox/{self._project_uuid}/knowledgepack/{self.uuid}/recognize_signal/"

        if capture:
            data_for_recognition = {"capture": capture}
        elif datafile:
            if datafile[-4:] != ".csv":
                datafile = f"{datafile}.csv"
            data_for_recognition = {"datafile": datafile}
        elif platform == "emulator" and not test_plan is None:
            data_for_recognition = {"test_plan": test_plan}
        else:
            print(
                "You must specify a capture, featurefile, datafile or test_plan to execute the recognition process."
            )
            return None

        data_for_recognition["test_plan"] = test_plan

        if platform not in ["cloud", "emulator"]:
            print("Platform must either be cloud or emulator.")

        data_for_recognition["stop_step"] = stop_step
        data_for_recognition["platform"] = platform
        data_for_recognition["kb_description"] = json.dumps(kb_description)
        data_for_recognition["compare_labels"] = compare_labels
        if isinstance(segmenter, bool):
            data_for_recognition["segmenter"] = segmenter
        elif isinstance(segmenter, FunctionCall):
            data_for_recognition["segmenter"] = segmenter._to_dict()
        else:
            raise KnowledgePackException(
                "Segmenter input requires a valid segmentation call object or None."
            )

        if renderer:
            renderer.render("Executing signal classification.")

        try:
            response = self._connection.request("post", url, data_for_recognition)
            response_data, err = utility.check_server_response(response)
            print(response_data)
            if err is False:
                if get_result:
                    results = utility.wait_for_pipeline_result(
                        self, lock=True, silent=True, wait_time=5, renderer=renderer
                    )
                    print("Results retrieved.")

                    if (
                        results[0] is not None
                        and type(results[0]) == DataFrame
                        and "ClassificationName" in results[0].columns.values
                    ):
                        class_count = {}
                        for classification in results[0]["ClassificationName"].values:
                            class_count[classification] = list(
                                results[0]["ClassificationName"].values
                            ).count(classification)
                        if results[1] is None:
                            results[1] = {}
                        results[1]["summary"] = {"class_count": class_count}

                        if "confusion_matrix" in results[1]:
                            results[1]["summary"]["confusion_matrix"] = {}
                            results[1]["summary"]["accuracy"] = {}
                            for session in results[1]["confusion_matrix"].columns:
                                cm = results[1]["confusion_matrix"][session]

                                df = sum(
                                    [
                                        render_confusion_matrix(cm.iloc[i])
                                        for i in range(cm.shape[0])
                                    ]
                                )

                                classes = [
                                    col
                                    for col in df.columns.values
                                    if col != "GroundTruth_Total"
                                ]

                                df["Support"] = df.apply(
                                    lambda row: np.nansum(
                                        [row[col] for col in classes]
                                    ),
                                    axis=1,
                                )
                                df.loc["Predicted"] = df.apply(
                                    lambda row: np.nansum(row)
                                ).values
                                diagonals = []
                                for x in df.index:
                                    if not x in ["Predicted", "Pos_Predic(%)"]:
                                        df.at[x, "Sensitivty(%) "] = (
                                            100 * df.at[x, x] / df.at[x, "Support"]
                                        )
                                        df.at["Pos_Predic(%)", x] = (
                                            100 * df.at[x, x] / df.at["Predicted", x]
                                        )
                                        diagonals.append(df.at[x, x])
                                df.at["Pos_Predic(%)", "Sensitivty(%)"] = (
                                    100.0
                                    * np.nansum(diagonals)
                                    / df.at["Predicted", "Support"]
                                )
                                results[1]["summary"]["confusion_matrix"][session] = df[
                                    classes
                                    + ["GroundTruth_Total", "Support", "Sensitivty(%)"]
                                ]
                                results[1]["summary"]["accuracy"][session] = df.at[
                                    "Pos_Predic(%)", "Sensitivty(%)"
                                ]

                    return results[0], results[1]
                else:
                    print(response_data.get("message", ""))
                    return None, None
        except MemoryError:
            warnings.warn(
                "ERROR: Your system has run out of RAM while performing this operation. Try freeing up some RAM or using less data before attempting this again."
            )
            return None

    def stop_recognize_signal(self):
        """Sends a kill signal to a pipeline"""

        url = "project/{0}/sandbox/{1}/knowledgepack/{2}/recognize_signal/".format(
            self._project_uuid, self._sandbox_uuid, self.uuid
        )
        response = self._connection.request("DELETE", url)
        utility.check_server_response(response)

        return response

    def _handle_result(self, response_data) -> Tuple[DataFrame, dict]:
        def fix_index(df):
            """Converts a string index to an int for a DataFrame"""
            df.index = df.index.astype(int64)
            return df.sort_index()

        def parse_classification_results(df_result):
            """Parses the results returned by knowledgepack recognize_signal into a DataFrame when a classification has
            occurred."""

            df_result.index.name = None
            ordered_columns = [
                "DistanceVector",
                "NIDVector",
                "CategoryVector",
                "MappedCategoryVector",
            ] + [
                i
                for i in df_result.columns
                if i
                not in [
                    "DistanceVector",
                    "NIDVector",
                    "CategoryVector",
                    "MappedCategoryVector",
                ]
            ]
            df_result = df_result[
                [col for col in ordered_columns if col in df_result.columns]
            ]

            return df_result

        summary = {}
        for key in response_data:
            if key not in ["results"]:
                try:
                    summary[key] = DataFrame(response_data[key])
                except:
                    summary[key] = response_data[key]

        # Check for a unicode string which can be returned sometimes
        if isinstance(response_data["results"], str):
            return fix_index(DataFrame(json.loads(response_data["results"]))), summary

        # Check for the results vector and parse appropriately
        if isinstance(response_data["results"], dict) and response_data["results"].get(
            "vectors", None
        ):
            df_result = parse_classification_results(
                DataFrame(response_data["results"]["vectors"])
            )
        else:
            df_result = fix_index(DataFrame(response_data["results"]))

        # If there was labeled data we will have a confusion matrix as well
        if "metrics" in response_data["results"]:
            summary["confusion_matrix"] = ConfusionMatrix(
                response_data["results"]["metrics"]
            )

        return df_result, summary

    def retrieve(self, silent: bool = False):
        """Gets the result of a prior asynchronous execution of the sandbox.

        Returns:
            (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
            (dict): execution summary including execution time and whether cache was used for each
            step; also contains a feature cost table if applicable
        """

        url = "project/{0}/sandbox/{1}/knowledgepack/{2}/recognize_signal/".format(
            self._project_uuid, self._sandbox_uuid, self.uuid
        )
        response = self._connection.request("get", url)
        data, err = utility.check_server_response(response)
        if err is False:
            response_data = data or {}
            return utility.check_pipeline_status(
                response_data, self._handle_result, silent=silent
            )

    def delete(self) -> Response:
        """Deletes the knowledgepack

        Returns:
            (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
            (dict): execution summary including execution time and whether cache was used for each
            step; also contains a feature cost table if applicable
        """

        uuids = {self.uuid}

        if self.knowledgepack_description:
            for _, value in self.knowledgepack_description.items():
                uuids.add(value["uuid"])

        for uuid in uuids:
            url = "project/{0}/sandbox/{1}/knowledgepack/{2}/".format(
                self._project_uuid, self._sandbox_uuid, uuid
            )
            response = self._connection.request("delete", url)
            _, err = utility.check_server_response(response)
            if err is False:
                print(f"Knowledgepack {uuid} deleted.")

            return response

    def rename(self, name: str) -> Response:
        return self.save(name)

    def save(self, name) -> Response:
        """Rename a knowledge pack

        Returns:
            (DataFrame or ModelResultSet): result of executed pipeline, specified by the sandbox
            (dict): execution summary including execution time and whether cache was used for each
            step; also contains a feature cost table if applicable
        """

        url = f"project/{self._project_uuid}/sandbox/{self._sandbox_uuid,}/knowledgepack/{self.uuid}/"

        data = {"name": name}
        response = self._connection.request("put", url, data)
        _, err = utility.check_server_response(response)
        if err is False:
            self._name = name
            print(f"Knowledgepack {name} updated.")

        return response

    def terminate_download(self) -> Response:
        url = f"project/{self._project_uuid}/sandbox/{self._sandbox_uuid}/knowledgepack/{self.uuid}/generate_lib/"

        response = self._connection.request("delete", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            print(response_data)

        return response

    def download_library(
        self,
        folder: str = "",
        run_async: bool = True,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        self.download_library_v2(
            folder=folder,
            run_async=run_async,
            platform=platform,
            renderer=renderer,
            *args,
            **kwargs,
        )

    def download_source(
        self,
        folder: str = "",
        run_async: bool = True,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        self.download_source_v2(
            folder=folder,
            run_async=run_async,
            platform=platform,
            renderer=renderer,
            *args,
            **kwargs,
        )

    def download_binary(
        self,
        folder: str = "",
        run_async: bool = True,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        self.download_binary_v2(
            folder=folder,
            run_async=run_async,
            platform=platform,
            renderer=renderer,
            *args,
            **kwargs,
        )

    def download_library_v2(
        self,
        folder: str = "",
        run_async: bool = True,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        """Calls the server to generate static library image based on device config.

        Args:
            folder (str): Folder to save to if not generating a link

        Returns:
            str: Denoting success, or link to file download
        """
        return self._download_v2(
            folder=folder,
            bin_or_lib="lib",
            run_async=run_async,
            platform=platform,
            renderer=renderer,
            *args,
            **kwargs,
        )

    def download_source_v2(
        self,
        folder: str = "",
        run_async: bool = True,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        """Calls the server to generate static library image based on device config.

        Args:
            folder (str): Folder to save to if not generating a link

        Returns:
            str: Denoting success, or link to file download
        """
        return self._download_v2(
            folder=folder,
            bin_or_lib="source",
            run_async=run_async,
            platform=platform,
            renderer=renderer,
            *args,
            **kwargs,
        )

    def download_binary_v2(
        self,
        folder: str = "",
        run_async: bool = True,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        """Calls the server to generate full binary image based on device config.

        Args:
            folder (str): Folder to save to if not generating a link

        Returns:
            str: Denoting success, or link to file download
        """
        return self._download_v2(
            folder=folder,
            bin_or_lib="bin",
            run_async=run_async,
            platform=platform,
            renderer=renderer,
            *args,
            **kwargs,
        )

    def get_sandbox_device_config(self) -> dict:
        url = (
            f"project/{self._project_uuid}/sandbox/{self._sandbox_uuid}/device_config/"
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response, is_octet=True)
        if err is False:
            return response_data.json().get("device_config")

    def _download_v2(
        self,
        folder: str,
        bin_or_lib: str,
        run_async: bool = False,
        platform: Optional[ClientPlatformDescription] = None,
        renderer=None,
        *args,
        **kwargs,
    ):
        _path = r"{0}".format(folder)
        url = f"project/{self._project_uuid}/knowledgepack/{self.uuid}/generate_{bin_or_lib}/v2"
        # config = self._sandbox.device_config.copy() # get a regular dictionary

        if platform is not None and type(platform) is ClientPlatformDescription:
            kwargs["config"] = {"target_platform": platform.id}
        elif platform is not None and type(platform) is not ClientPlatformDescription:
            err_msg = "Platform not properly specified. Specify via client.platforms()"
            if renderer:
                renderer.render(err_msg)
            return err_msg, False

        config = kwargs.pop("config", None)
        if config:
            if "kb_description" in config and isinstance(
                config["kb_description"], dict
            ):
                config["kb_description"] = json.dumps(config["kb_description"])
            for key in kwargs:
                if key in [
                    "debug",
                    "test_data",
                    "sample_rate",
                    "output_options",
                    "debug_level",
                    "profile",
                    "profile_iterations",
                    "target_processor",
                    "target_compiler",
                    "float_options",
                    "extra_build_flags",
                ]:
                    config.update({key: kwargs[key]})
                if key == "kb_description":
                    config.update({key: json.dumps(kwargs[key])})
        else:
            config = self.get_sandbox_device_config()

        print(f"Generating {bin_or_lib} with configuration")
        for key in config:
            print(f"{key} : {config[key]}")

        if config.get("target_platform", None) is None:
            raise KnowledgePackException("Target platform must be specified.")
        config["asynchronous"] = run_async
        response = self._connection.request("post", url, data=config)
        response_data, err = utility.check_server_response(
            response, is_octet=True, renderer=renderer
        )

        msg = "Generating Knowledge Pack"
        while True:
            response = self._connection.request("get", url)
            response_data, err = utility.check_server_response(
                response, is_octet=True, renderer=renderer
            )
            if (
                err
                or "content-disposition" in response_data.headers
                or response_data.json().get("task_state") in ("FAILURE",)
            ):
                break
            sys.stdout.write(".")
            if renderer:
                msg += " ."
                renderer.render(msg)
            sleep(5)
        if "content-disposition" in response_data.headers:
            if kwargs.get("save_as"):
                filename = kwargs.get("save_as", None)
            else:
                filename = re.findall(
                    'filename="([^"]+)"', response_data.headers["content-disposition"]
                )[0]
            if filename is None:
                filename = re.findall(
                    'filename="([^"]+)"', response_data.headers["content-disposition"]
                )[0]
            file_path = os.path.join(_path, filename)
            with open(file_path, "wb") as f:
                for d in response_data.iter_content(2048):
                    f.write(d)

            output_path = os.path.join(os.path.abspath("."), file_path)
            if renderer:
                renderer.render(f"KnowledgePack saved to\n{output_path}")

            return output_path, True
        else:
            err_msg = response_data.json().get("task_result")
            print(err_msg)
            if renderer:
                renderer.render(err_msg)
            return err_msg, False

    def get_build_log(self, renderer=None, save_as: Optional[str] = None) -> str:
        url = f"knowledgepack/{self.uuid}/build-logs/"

        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(
            response, is_octet=True, renderer=renderer
        )

        if "content-disposition" in response_data.headers:
            if save_as:
                filename = save_as
            else:
                filename = re.findall(
                    'filename="([^"]+)"', response_data.headers["content-disposition"]
                )[0]

            with open(filename, "wb") as f:
                for d in response_data.iter_content(2048):
                    f.write(d)

            output_path = os.path.join(os.path.abspath("."), filename)
            if renderer:
                renderer.render(f"Build Log saved to\n{output_path}")
            else:
                print(f"Build Log saved to: {output_path}")

            return output_path, True
        else:
            err_msg = response_data.body
            print(err_msg)
            if renderer:
                renderer.render(err_msg)
            return err_msg, False

    def get_featurefile(self) -> DataFrame:
        if self._feature_file_cache is not None:
            return self._feature_file_cache

        class DummyProject:
            def __init__(self, uuid):
                self.uuid = uuid

        ff = FeatureFile(
            self._connection,
            project=DummyProject(self.project_uuid),
            uuid=self._feature_file_uuid,
        )
        ff.refresh()
        res = ff.download_json()

        self._feature_file_cache = DataFrame(json.loads(res.json()))

        return self._feature_file_cache

    def create(self) -> KnowledgePack:
        """Create a new knowledge pack on the server using the internal data for this model

        Returns:
            KnowledgePack object
        """

        print(
            "Creating Knowledge Packs is currently beta and the API is subject to change."
        )

        data = {
            "project": self.project_uuid,
            "pipeline_summary": self.pipeline_summary,
            "query_summary": self.query_summary,
            "feature_summary": self.feature_summary,
            "class_map": self.class_map,
            "sensor_summary": self.sensor_summary,
            "transform_summary": self.transform_summary,
            "knowledgepack_summary": self.knowledgepack_summary,
            "sandbox": self.sandbox_uuid,
            "name": self.name,
            "model_parameters": self.model_parameters,
            "model_configuration": self.model_configuration,
        }

        url = f"project/{self.project_uuid}/knowledgepack/"
        response = self._connection.request("post", url, json=data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            kp = KnowledgePack(
                self._connection,
                response_data.get("project_uuid"),
                response_data.get("sandbox_uuid"),
            )
            kp.initialize_from_dict(response_data)
            return kp

        return response_data

    def export(self) -> dict:
        """Export a Knowledge Pack Model

        Returns:
            Knowledge Pack Export Dict
        """

        url = f"knowledgepack/{self.uuid}/export/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            return response_data

        return response

    def initialize_from_dict(self, init_dict):
        self._init_dict = init_dict
        self._uuid = init_dict["uuid"]
        self._name = init_dict["name"]
        self._configuration_index = init_dict.get("configuration_index", None)
        self._model_index = init_dict.get("model_index", None)
        self._execution_time = init_dict.get("execution_time", None)

        self._class_map = init_dict["class_map"]
        self._pipeline_summary = init_dict["pipeline_summary"]
        self._query_summary = init_dict["query_summary"]
        self._feature_summary = init_dict["feature_summary"]
        self._transform_summary = init_dict["transform_summary"]
        self._sensor_summary = init_dict["sensor_summary"]

        self._neuron_array = (
            init_dict.get("neuron_array")
            if init_dict.get("neuron_array")
            else init_dict.get("model_parameters")
        )
        self._device_configuration = (
            init_dict.get("device_configuration")
            if init_dict.get("device_configuration")
            else init_dict.get("model_configuration")
        )

        self._model_results = init_dict.get("model_results", None)

        self._cost_summary = init_dict.get("cost_summary", None)
        self._project_name = init_dict.get("project_name")
        self._sandbox_name = init_dict.get("sandbox_name")
        self._feature_file_uuid = init_dict.get("feature_file_uuid")
        self._knowledgepack_summary = init_dict.get("knowledgepack_summary", None)
        self._knowledgepack_description = init_dict.get(
            "knowledgepack_description", None
        )
        self._training_metrics = init_dict.get("training_metrics", None)

    def add_feature_only_generators(self, generators: list[dict]):
        """
        Adds feature only generators to a knowledge pack. You can add the
        features and then create a new knowledgepack. The new KnowledgePack
        will generate these features, but not use them as part of the classifier.

        new_generators = [{'family': None,
                        'inputs': {'columns': ['channel_0']},
                        'num_outputs': 1,
                        'function_name': '100th Percentile',
                        "subtype": "Stats"}]

        kp.add_feature_only_generators(new_generators)
        kp._name = "KP with Extra Features"
        kp.create()

        """

        for generator in generators:
            self._feature_summary = add_generator_to_feature_summary(
                self.feature_summary,
                generator["inputs"]["columns"],
                generator["subtype"],
                generator["function_name"],
                generator["num_outputs"],
            )
            tmp_generator = copy.deepcopy(generator)
            tmp_generator["outputs"] = list(range(generator["num_outputs"]))
            self._knowledgepack_summary = add_generator_to_knowledgepack_summary(
                self.knowledgepack_summary, tmp_generator
            )


def get_knowledgepack(
    kp_uuid, connection: Connection, get_flatbuffer: bool = False
) -> KnowledgePack:
    """Gets a KnowledgePack by uuid.

    Returns:
        a KnowledgePack instance, list of instances, or None
    """
    url = f"knowledgepack/{kp_uuid}/"
    response = connection.request("get", url, params={"tflite": get_flatbuffer})
    response_data, err = utility.check_server_response(response)
    if err is False:
        kp = KnowledgePack(
            connection,
            (
                response_data.get("project_uuid")
                if response_data.get("project_uuid") is not None
                else response_data.get("project")
            ),
            (
                response_data.get("sandbox_uuid")
                if response_data.get("sandbox_uuid") is not None
                else response_data.get("sandbox")
            ),
        )
        kp.initialize_from_dict(response_data)
        return kp


def delete_knowledgepack(kp_uuid: str, connection: Connection) -> Response:
    """Gets a KnowledgePack by uuid.

    Returns:
        a KnowledgePack instance, list of instances, or None
    """
    url = f"knowledgepack/{kp_uuid}/"
    response = connection.request("delete", url)

    return response


def get_knowledgepacks(connection: Connection) -> DataFrame:
    """Gets the KnowledgePack(s) created by the sandbox.

    Returns:
        a KnowledgePack instance, list of instances, or None
    """
    url = "knowledgepack/"
    response = connection.request("get", url)
    response_data, err = utility.check_server_response(response)
    if err is False:
        return DataFrame(response_data)


def add_generator_to_feature_summary(
    feature_summary: dict,
    sensors: list,
    category: str,
    generator: str,
    num_features: int,
):
    new_feature_summary = []

    name = "_".join(sensors) + generator.replace(" ", "_")

    def get_tmp(sensors, category, generator, num_features):
        return {
            "Feature": None,
            "Sensors": sensors,
            "Category": category,
            "Generator": generator,
            "LibraryPack": None,
            "ContextIndex": None,
            "EliminatedBy": "GeneratorOnly",
            "GeneratorIndex": None,
            "GeneratorTrueIndex": None,
            "GeneratorFamilyIndex": None,
            "GeneratorFamilyFeatures": num_features,
        }

    cascade_index = 0

    for feature in feature_summary:
        if cascade_index != feature["CascadeIndex"]:
            cascade_index = feature["CascadeIndex"]
            tmp = get_tmp(sensors, category, generator, num_features)
            for family_feature_index in range(num_features):
                print(f"adding generator at {cascade_index-1}")
                tmp["GeneratorIndex"] = generator_index + 1
                tmp["ContextIndex"] = context_index + 1 + family_feature_index
                tmp["GeneratorTrueIndex"] = generator_true_index + 1
                tmp["GeneratorFamilyIndex"] = family_feature_index + 1
                tmp["Feature"] = f"agen_{name}_{tmp['ContextIndex']}"
                tmp["CascadeIndex"] = cascade_index - 1

            new_feature_summary.append(tmp)
        else:
            context_index = feature["ContextIndex"]
            generator_index = feature["GeneratorIndex"]
            generator_true_index = feature["GeneratorTrueIndex"]

        new_feature_summary.append(feature)

    tmp = get_tmp(sensors, category, generator, num_features)
    tmp["GeneratorIndex"] = generator_index + 1
    tmp["ContextIndex"] = context_index + 1 + family_feature_index
    tmp["GeneratorTrueIndex"] = generator_true_index + 1
    tmp["GeneratorFamilyIndex"] = family_feature_index + 1
    tmp["Feature"] = f"agen_Name_{name}_{tmp['ContextIndex']}"
    tmp["CascadeIndex"] = cascade_index

    new_feature_summary.append(tmp)

    return new_feature_summary


def add_generator_to_knowledgepack_summary(knowledgepack_summary: dict, generator: str):
    tmp = copy.deepcopy(knowledgepack_summary)

    gen_index = 0
    for index, step in enumerate(knowledgepack_summary["recognition_pipeline"]):
        if step.get("type") == "generatorset":
            gen_index = index
            break

    tmp["recognition_pipeline"][gen_index]["set"].append(generator)

    return tmp
