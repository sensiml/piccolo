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

import json
import logging
from copy import deepcopy

import engine.base.pipeline_utils as pipeline_utils
from datamanager.models import KnowledgePack
from engine.automationengine_mixin.parameter_optimizer_utils import get_step_id
from engine.base.utils import clean_results
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class SaveKnowledgepackMixin:
    def __init__(self):
        pass

    def save_results_tvo_knowledgepacks(self, fitted_population, results_tvo):
        fitted_population["knowledgepack"] = "N/A"
        fitted_population["name"] = None
        models_object = {"configurations": {}}

        for index, models in enumerate(results_tvo):
            # name can only be 40 characters long so we have to truncate the sandbox name to a speific value
            name_length = 40 - len("_rank_{index}".format(index=index))
            name = "{sandbox_name}_rank_{index}".format(
                sandbox_name=self._sandbox.name[:name_length].replace(" ", "_"),
                index=index,
            )

            # get the model results from the recall will always be fold 0
            recall_fold = "Fold 0"
            model_result = models["model_stats"]["models"][recall_fold]

            model_result = update_model_validation_metrics_from_fitness_summary(
                model_result, fitted_population.iloc[index]
            )

            pipeline_summary = json.loads(fitted_population.loc[index, "pipeline"])

            summary = json.loads(fitted_population.loc[index, "summary"])

            feature_file = pipeline_utils.save_cache_as_featurefile(
                self._sandbox.project,
                self._sandbox.uuid,
                summary["pipeline_summary"][-1]["input_data"],
                fmt=".csv.gz",
                label_column=summary["pipeline_summary"][-1]["label_column"],
            )

            knowledgepack = self._save_knowledgepack(
                model_result,
                recall_fold,
                index,
                name,
                summary,
                pipeline_summary,
                feature_file,
            )

            fitted_population.loc[index, "knowledgepack"] = str(knowledgepack.uuid)
            fitted_population.loc[index, "name"] = name

            models_object["configurations"][name] = models["model_stats"]
            models_object["configurations"][name]["models"] = {
                name: models["model_stats"]["models"][recall_fold]
            }
            models_object["configurations"][name]["models"][name][
                "KnowledgePackID"
            ] = str(knowledgepack.uuid)

        return fitted_population, models_object

    def _save_knowledgepack(
        self,
        model_results,
        c_index,
        m_index,
        name,
        summary,
        pipeline_summary,
        feature_file,
    ):
        logger.debug(
            {
                "message": "Saving auto generated knowledgepack uuid: {} name: {}".format(
                    self.sandbox.uuid, name
                ),
                "UUID": self._sandbox.id,
                "log_type": "PID",
            }
        )

        # TODO: Make this work for all of our classifiers call it something other than neurons
        summary["cost_summary"]["classifier"] = model_results["classifier_costs"]

        model_stats = deepcopy(model_results)
        model_parameters = model_stats.pop("parameters")

        # Create the KnowledgePack
        return KnowledgePack.objects.create(
            sandbox=self._sandbox,
            project=self._sandbox.project,
            configuration_index=c_index,
            name=name,
            model_index=m_index,
            neuron_array=model_parameters,
            model_results=model_stats,
            sensor_summary=summary["sensor_summary"],
            query_summary=summary["query_summary"],
            feature_summary=summary["feature_summary"],
            feature_file=feature_file,
            device_configuration=summary["device_configuration"],
            transform_summary=summary["transform_summary"],
            knowledgepack_summary=summary.get("knowledgepack_summary", ""),
            class_map=summary["class_map"],
            cost_summary=summary["cost_summary"],
            pipeline_summary=pipeline_summary,
            knowledgepack_description=None,
        )

    def write_the_internal_cache_variables(self, fitted_population, results):
        if self.last_iteration is not None:
            self._cache_manager.evict_key("auto_results")

        # Write the internal cache variables needed for future generations
        self._cache_manager.save_variable_to_cache(
            "iteration_{}_models".format(self.last_iteration),
            results,
            cache_key="auto_results",
        )

        self._cache_manager.save_variable_to_cache(
            "iteration_{}_summary".format(self.last_iteration),
            fitted_population.to_dict(orient="list"),
            cache_key="auto_results",
        )

        fitness_summary = DataFrame(fitted_population)

        for column in [
            "flash",
            "sram",
            "stack",
            "latency",
            "pipeline",
            "summary",
            "iteration",
            "classifiers",
            "feature_table",
            "ignore_columns",
            "individual",
            "input_data",
            "label_column",
            "optimizers",
            "outputs",
            "type",
            "validation_methods",
            "validation_seed",
        ] + [get_step_id(step) for step in self.ga_pipeline]:
            if column in fitness_summary.columns:
                fitness_summary.drop(column, axis=1, inplace=True)

        fitness_summary_columns = [
            "fitness",
            "accuracy",
            "f1_score",
            "sensitivity",
            "positive_predictive_rate",
            "features",
            "classifiers_sram",
            "knowledgepack",
            "name",
        ]

        if "kb_description" in fitness_summary.columns:
            fitness_summary_columns = fitness_summary_columns + ["kb_description"]

        fitness_summary = fitness_summary[fitness_summary_columns]

        # Write the final results to return
        self._cache_manager.save_result_data(
            "auto_models", str(self.pipeline_id), data=results
        )
        self._cache_manager.save_result_data(
            "auto_extra",
            str(self.pipeline_id),
            data=fitness_summary.to_dict(orient="list"),
        )

        return fitness_summary


def update_model_validation_metrics_from_fitness_summary(model, fitness_values):
    for key in model["metrics"]["validation"].keys():
        if key in fitness_values.index:
            model["metrics"]["validation"][key] = clean_results(fitness_values[key])

    model["metrics"]["validation"]["ConfusionMatrix"] = clean_results(
        fitness_values["AvgConfusionMatrix"]
    )

    model["metrics"]["AllConfusionMatrix"] = clean_results(
        fitness_values["AllConfusionMatrix"]
    )

    model["metrics"]["AllTrainingMetrics"] = clean_results(
        fitness_values["TrainingMetrics"]
    )

    return model
