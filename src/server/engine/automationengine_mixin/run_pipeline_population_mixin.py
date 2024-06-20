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
from copy import deepcopy

from django.conf import settings
from engine.automationengine_mixin.parameter_optimizer_utils import (
    create_genetic_step,
    get_step_id,
)
from engine.base.pipeline_steps import parallel_pipeline_step
from logger.log_handler import LogHandler
from pandas import DataFrame

logger = LogHandler(logging.getLogger(__name__))


class RunPipelinePopulationMixin:
    def parallel_population_pipeline_step_batch(
        self,
        func,
        step_id,
        steps,
        team_id,
        project_id,
        pipeline_id,
        user_id,
        return_results=False,
        step_info=None,
        **kwargs,
    ):
        """A parallel implementation of the pipeline step with a batch size"""

        batch_size = settings.MAX_BATCH_SIZE

        num_batches = len(steps) // batch_size
        results = []

        for batch in range(num_batches):
            self._update_step_info(
                {
                    "step_index": step_id + len(self.static_pipeline) + 1,
                    "step_type": steps[0].get("type"),
                    "step_name": steps[0].get("name"),
                    "iteration": "RCL"
                    if self.last_iteration == "RCL"
                    else self.last_iteration + 1,
                    "total_iterations": self.iterations,
                    "batch_size": batch_size,
                    "batch": num_batches if num_batches else len(steps),
                    "population_size": len(steps),
                    "iteration_start_index": len(self.static_pipeline) + 1,
                }
            )

            results.extend(
                parallel_pipeline_step(
                    func,
                    steps[batch * batch_size : (batch + 1) * batch_size],
                    team_id,
                    project_id,
                    pipeline_id,
                    user_id,
                    return_results,
                    **kwargs,
                )
            )

        if len(steps) - (num_batches * batch_size) > 0:
            self._update_step_info(
                {
                    "step_index": step_id + len(self.static_pipeline) + 1,
                    "step_type": steps[0].get("type"),
                    "step_name": steps[0].get("name"),
                    "iteration": "RCL"
                    if self.last_iteration == "RCL"
                    else self.last_iteration + 1,
                    "total_iterations": self.iterations,
                    "batch_size": batch_size,
                    "batch": num_batches if num_batches else len(steps),
                    "population_size": len(steps),
                    "iteration_start_index": len(self.static_pipeline) + 1,
                }
            )

            results.extend(
                parallel_pipeline_step(
                    func,
                    steps[num_batches * batch_size :],
                    team_id,
                    project_id,
                    pipeline_id,
                    user_id,
                    return_results,
                    **kwargs,
                )
            )

        return results

    def parallel_population_pipeline_step(
        self,
        func,
        step_id,
        steps,
        team_id,
        project_id,
        pipeline_id,
        user_id,
        return_results=False,
        step_info=None,
        **kwargs,
    ):
        """A parallel implementation of the pipeline step"""

        logger.info(
            {
                "message": {
                    "static_pipeline": self.static_pipeline,
                    "steps_id": step_id,
                    "last_iteration": self.last_iteration,
                    "pipeline": self.pipeline,
                    "steps": steps[0],
                },
                "log_type": "datamanager",
            }
        )

        self._update_step_info(
            {
                "step_index": step_id + len(self.static_pipeline) + 1,
                "step_type": steps[0].get("type"),
                "step_name": steps[0].get("name"),
                "total_steps": len(self.pipeline),
                "iteration": "RCL"
                if self.last_iteration == "RCL"
                else self.last_iteration + 1,
                "total_iterations": self.iterations,
                "population_size": len(steps),
                "iteration_start_index": len(self.static_pipeline) + 1,
            }
        )

        results = parallel_pipeline_step(
            func,
            steps,
            team_id,
            project_id,
            pipeline_id,
            user_id,
            return_results,
            **kwargs,
        )

        def remove_results_summary(results):
            new_results = []
            for result in results:
                if isinstance(result[1], dict):
                    if result[1].get("filename"):
                        new_results.append((result[0], result[1]["filename"]))
                else:
                    new_results.append(result)

            return new_results

        return remove_results_summary(results)

    def set_error_log(self, index_pp, population, error_message, error_step):
        # recording the pipeline/s that cause problem

        # assign predefined pipeline
        pipeline = deepcopy(self.pipeline)

        for population_index in population.keys():
            for pipeline_index in range(len(pipeline)):
                if population_index == pipeline[pipeline_index]["name"]:
                    pipeline[pipeline_index] = population[population_index][index_pp]

        self.error_log.append(
            {
                "error_message": error_message,
                "pipeline": pipeline,
                "iteration_number": self.last_iteration,
                "error_step": error_step,
            }
        )

    def run_population(
        self,
        step_index,
        step,
        func,
        population,
        iteration,
        mapped_inputs=None,
        map_inputs=True,
        clean_cache=False,
        return_results=True,
    ):
        error_flag = False
        step_id = get_step_id(step)

        temp_list = []
        for index, s in enumerate(population[step_id]):
            temp_val = create_genetic_step(
                s, iteration, index, map_inputs, mapped_inputs
            )
            temp_list.append(temp_val)

        population[step_id] = temp_list

        results = []
        mapped_results = []
        failed_pipeline_indexes = []

        cached_population = []
        cached_mapped_inputs = []

        if step_id != "tvo" and iteration != "RCL":
            # Optimizing the current iteration by filtering population items for each step that are already run previous in iterations
            # or filtering duplicated population items in the same iteration. Output of the filtered population will be updated, cached.
            # only unique population items will be run in parallel_population_pipeline_step_batch function

            (
                population,
                cached_population,
                cached_mapped_inputs,
            ) = optimize_current_iteration(
                self.task_id,
                population,
                self.fitted_population_log,
                step_id,
                iteration,
                self.mapped_inputs_previous_iterations,
                self.sandbox.uuid,
            )

        logger.debug(
            {
                "message": "Population step_id: {}".format(step_id),
                "data": population[step_id],
                "UUID": self.sandbox.uuid,
                "log_type": "PID",
                "task_id": self.task_id,
            }
        )

        if step_id == "tvo" and iteration != "RCL":
            kwargs = {"save_model_parameters": False}
        else:
            kwargs = {}

        if len(population[step_id]) == 0:
            population[step_id] = cached_population
            return (
                population,
                results,
                cached_mapped_inputs,
                failed_pipeline_indexes,
            )

        parallel_results = self.parallel_population_pipeline_step(
            func,
            step_index,
            population[step_id],
            self._team_id,
            self.project.uuid,
            self.pipeline_id,
            self._user.id,
            return_results=False,
            **kwargs,
        )

        if step_id == "selectorset":
            # this will be required for min_max scaling in optimize_current_iteration function
            if iteration == 0:
                cached_mapped_inputs = [
                    [parallel_results[0][0], mapped_inputs_item[1]]
                    for mapped_inputs_item in cached_mapped_inputs
                ]
                self.mapped_inputs_previous_iterations = cached_mapped_inputs

            else:
                self.mapped_inputs_previous_iterations = cached_mapped_inputs

        step_successful = False
        for index_pipeline, result in enumerate(parallel_results):
            if result[0]:
                step_successful = True
                if return_results:
                    results.append(self.get_data_cache(result[1]))
                else:
                    results.append({})
                mapped_results.append(result)
            else:
                logger.warn(
                    {
                        "message": "Error: {}".format(result[1]),
                        "data": {
                            "pipeline step": population[step_id][index_pipeline],
                            "population index": index_pipeline,
                            "step_id": step_id,
                        },
                        "UUID": self.sandbox.uuid,
                        "log_type": "PID",
                        "task_id": self.task_id,
                    }
                )

                # pipeline return error
                self.set_error_log(
                    index_pipeline,
                    population,
                    result[1],
                    population[step_id][0]["name"],
                )

                error_flag = True
                failed_pipeline_indexes.append(index_pipeline)

        if error_flag:
            population = self.remove_failed_populations(
                population, failed_pipeline_indexes
            )

        if not step_successful:
            raise Exception(
                {
                    "message": f"All populations for pipeline Step {step_id} failed at iteration {iteration}. See the errors for a detailed explantion",
                    "errors": [x.get("error_message") for x in self.error_log],
                }
            )

        # Concatnate with the unique population items and caches items to population size
        population[step_id] = population[step_id] + cached_population

        mapped_results = mapped_results + cached_mapped_inputs

        return population, results, mapped_results, failed_pipeline_indexes

    def remove_failed_populations(self, population, indexes):
        for index in indexes[::-1]:
            for key in population.keys():
                del population[key][index]

        return population

    def execute_custom_pipeline(self):
        # Execute the static part of the pipeline

        self.static_pipeline = [step for i, step in enumerate(self.pipeline)]

        execution_results, _ = self.execute(
            self.static_pipeline, caching=True, store_errors=False, part_of_automl=False
        )

        results_tvo = self.get_data_cache(
            self._cache_manager._cache["results"][
                f"pipeline_result.{self.pipeline_id}"
            ][0]["filename"]
        )

        fitted_population = []

        for key, model in results_tvo["configurations"]["0"]["models"].items():
            tmp_info = {}

            tmp_info["f1_score"] = model["metrics"]["validation"]["f1_score"]["average"]
            tmp_info["sensitivity"] = model["metrics"]["validation"]["sensitivity"][
                "average"
            ]
            tmp_info["positive_predictive_rate"] = model["metrics"]["validation"][
                "positive_predictive_rate"
            ]["average"]
            tmp_info["accuracy"] = model["metrics"]["validation"]["accuracy"]
            tmp_info["knowledgepack"] = model["KnowledgePackID"]
            tmp_info["classifiers_sram"] = model["model_size"]
            tmp_info["features"] = len(model["feature_statistics"]["validation"])
            tmp_info["fitness"] = 1
            tmp_info["name"] = key
            fitted_population.append(tmp_info)

        fitness_summary = self.write_the_internal_cache_variables(
            DataFrame(fitted_population), results_tvo
        )

        return results_tvo, fitness_summary

    def execute_the_static_part_of_the_pipeline(self):
        # Execute the static part of the pipeline
        if self.ga_steps:
            self.split = [step["type"] for step in self.pipeline].index(
                self.ga_steps[0]
            )
        else:
            self.split = [step["type"] for step in self.pipeline].index("tvo")

        self.static_pipeline = [
            step for i, step in enumerate(self.pipeline) if i < self.split
        ]

        # if data has multi-classes, run static part of the pipeline
        self.execute(
            self.static_pipeline, caching=True, store_errors=False, part_of_automl=True
        )


def optimize_current_iteration(
    task_id,
    population,
    fitted_population_log,
    step_id,
    iteration,
    mapped_inputs_previous_iteration,
    sandbox_uuid,
):
    original_population_size = len(population[step_id])

    cached_population = []
    cached_mapped_inputs = []

    unique_population_step_id = []

    if mapped_inputs_previous_iteration is None:
        number_of_vector = 0
    elif len(mapped_inputs_previous_iteration) == 0:
        # there is no optimization from the previous run
        number_of_vector = 0
    else:
        number_of_vector = mapped_inputs_previous_iteration[0][0]

    if step_id != "selectorset":
        population[step_id] = update_output_of_transforms(population[step_id])

    # filtering across generation
    if iteration != 0:
        if step_id == "selectorset":
            (
                unique_population_step_id,
                cached_population,
                cached_mapped_inputs,
            ) = create_cached_population_and_mapped_inputs_for_selectorset(
                population,
                step_id,
                number_of_vector,
                fitted_population_log,
            )

        else:
            (
                unique_population_step_id,
                cached_population,
                cached_mapped_inputs,
            ) = create_cached_population_and_mapped_inputs_for_transforms(
                population, step_id, number_of_vector, mapped_inputs_previous_iteration
            )

        population[step_id] = unique_population_step_id

    # filter in generation
    (
        unique_population_step_id,
        cached_population,
        cached_mapped_inputs,
    ) = filter_steps_from_population(
        population, step_id, cached_population, cached_mapped_inputs, number_of_vector
    )

    population[step_id] = unique_population_step_id

    logger.debug(
        {
            "message": "Iteration Number: {}. Poputlation step_id: {} is reduced from {} to {}".format(
                str(iteration),
                step_id,
                str(original_population_size),
                str(len(population[step_id])),
            ),
            "UUID": sandbox_uuid,
            "log_type": "PID",
            "task_id": task_id,
        }
    )

    return population, cached_population, cached_mapped_inputs


def update_output_of_transforms(population_transforms):
    logger.info(
        {
            "message": [x["inputs"]["input_data"] for x in population_transforms],
            "log_type": "datamanager",
        }
    )

    for i, temp_step in enumerate(population_transforms):
        temp_output = ".".join(
            temp_step["outputs"][0].split(".")[:2]
            + temp_step["inputs"]["input_data"].split(".")[2:4]
        )
        temp_list = temp_output.split(".")
        population_transforms[i]["outputs"] = [
            temp_output,
            ".".join(temp_list[:1] + ["features"] + temp_list[1:]),
        ]

    return population_transforms


def filter_steps_from_population(
    population, step_id, cached_population, cached_mapped_inputs, number_of_vector
):
    unique_step_items = {}
    unique_population_step_id = []

    for i, temp_step in enumerate(population[step_id]):
        if step_id == "selectorset":
            log_list = [
                j for j, v in unique_step_items.items() if v == temp_step["set"][-1]
            ]
        else:
            log_list = [
                j
                for j, v in unique_step_items.items()
                if v == temp_step["inputs"]["input_data"]
            ]

        if len(log_list) > 0:
            cached_population.append(population[step_id][log_list[0]])
            cached_mapped_inputs.append(
                [
                    number_of_vector,
                    population[step_id][log_list[0]]["outputs"][0] + ".csv.gz",
                ]
            )

        else:
            if step_id == "selectorset":
                unique_step_items[i] = temp_step["set"][-1]
            else:
                unique_step_items[i] = temp_step["inputs"]["input_data"]

            unique_population_step_id.append(temp_step)

    return unique_population_step_id, cached_population, cached_mapped_inputs


def filter_set_from_population_log(list_of_steps, temp_step):
    # reading the feature selection algorithms form pipeline_output_in_log
    pipeline_output_in_log = []
    for step_index in list_of_steps:
        if step_index["set"] == temp_step["set"]:
            pipeline_output_in_log = step_index["outputs"][0]
            break

    return pipeline_output_in_log


def create_cached_population_and_mapped_inputs_for_selectorset(
    population, step_id, number_of_vector, fitted_population_log
):
    cached_population = []
    cached_mapped_inputs = []

    list_of_steps = fitted_population_log[step_id].tolist()
    unique_population_step_id = deepcopy(population[step_id])

    for i, temp_step in enumerate(population[step_id]):
        pipeline_output_in_log = filter_set_from_population_log(
            list_of_steps, temp_step
        )

        # update_input_output
        if len(pipeline_output_in_log) > 0:
            (
                unique_population_step_id,
                cached_population,
                cached_mapped_inputs,
            ) = create_cached_population_and_cached_mapped_inputs(
                pipeline_output_in_log,
                unique_population_step_id,
                temp_step,
                cached_population,
                cached_mapped_inputs,
                number_of_vector,
            )

    return unique_population_step_id, cached_population, cached_mapped_inputs


def create_cached_population_and_mapped_inputs_for_transforms(
    population, step_id, number_of_vector, mapped_inputs_previous_iteration
):
    if mapped_inputs_previous_iteration:
        number_of_unique_population = len(population[step_id]) - len(
            mapped_inputs_previous_iteration
        )
    else:
        number_of_unique_population = len(population[step_id])

    unique_population_step_id = deepcopy(
        population[step_id][:number_of_unique_population]
    )
    cached_population = deepcopy(population[step_id][number_of_unique_population:])

    cached_mapped_inputs = []
    new_cached_population = []

    population_step_list = deepcopy(cached_population)

    for i, temp_step in enumerate(cached_population):
        temp_output = ".".join(
            temp_step["outputs"][0].split(".")[:2]
            + temp_step["inputs"]["input_data"].split(".")[2:4]
        )

        (
            population_step_list,
            new_cached_population,
            cached_mapped_inputs,
        ) = create_cached_population_and_cached_mapped_inputs(
            temp_output,
            population_step_list,
            temp_step,
            new_cached_population,
            cached_mapped_inputs,
            number_of_vector,
        )

        (
            new_cached_population[i],
            cached_mapped_inputs[i],
        ) = cached_population_unique_item_check(
            new_cached_population[i], unique_population_step_id, cached_mapped_inputs[i]
        )

    return unique_population_step_id, new_cached_population, cached_mapped_inputs


def cached_population_unique_item_check(
    temp_step, unique_population_step_id, cached_mapped_inputs_temp
):
    # if there is the same item in unique item list, set the same output

    for j, unique_step in enumerate(unique_population_step_id):
        if temp_step["inputs"]["input_data"] == unique_step["inputs"]["input_data"]:
            temp_step["outputs"] = unique_population_step_id[j]["outputs"]
            cached_mapped_inputs_temp[1] = (
                unique_population_step_id[j]["outputs"][0] + ".csv.gz"
            )
            return temp_step, cached_mapped_inputs_temp

    return temp_step, cached_mapped_inputs_temp


def create_cached_population_and_cached_mapped_inputs(
    pipeline_output_in_log,
    population_step_list,
    temp_step,
    cached_population,
    cached_mapped_inputs,
    number_of_vector,
):
    # if pipeline_output_in_log is exist, remove the item from the population
    population_step_list.remove(temp_step)
    temp_list = pipeline_output_in_log.split(".")

    temp_step["outputs"] = [
        pipeline_output_in_log,
        ".".join(temp_list[:1] + ["features"] + temp_list[1:]),
    ]

    # add cached items to cached_population list
    cached_population.append(temp_step)

    # add cached items to cached_mapped_inputs list
    cached_mapped_inputs.append([number_of_vector, pipeline_output_in_log + ".csv.gz"])

    return population_step_list, cached_population, cached_mapped_inputs
