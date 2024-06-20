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

import pytest

from pandas import DataFrame
from copy import deepcopy

from engine.automationengine_mixin.run_pipeline_population_mixin import (
    create_cached_population_and_cached_mapped_inputs,
    create_cached_population_and_mapped_inputs_for_transforms,
    filter_set_from_population_log,
    filter_steps_from_population,
    optimize_current_iteration,
    update_output_of_transforms,
    create_cached_population_and_mapped_inputs_for_selectorset,
)

pytestmark = pytest.mark.django_db


class TestRunPipelinePopulation:
    def setup_class(self):
        self.static_feature_selectors = [
            {"function_name": "Variance Threshold", "inputs": {"threshold": 0.1}},
            {"function_name": "Correlation Threshold", "inputs": {"threshold": 0.95}},
        ]

    def test_filter_steps_from_population(self):

        orj_population = {
            "selectorset": [
                {
                    "set": [
                        {
                            "inputs": {"feature_number": 8},
                            "function_name": "t-Test Feature Selector",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.0",
                        "temp.features.featureselector.0.0",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"number_of_features": 8},
                            "function_name": "Tree-based Selection",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.1",
                        "temp.features.featureselector.0.1",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"number_of_features": 16},
                            "function_name": "Tree-based Selection",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.2",
                        "temp.features.featureselector.0.2",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"feature_number": 8},
                            "function_name": "Information Gain",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.3",
                        "temp.features.featureselector.0.3",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"feature_number": 2},
                            "function_name": "Information Gain",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.4",
                        "temp.features.featureselector.0.4",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"feature_number": 1},
                            "function_name": "Information Gain",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.5",
                        "temp.features.featureselector.0.5",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"feature_number": 8},
                            "function_name": "t-Test Feature Selector",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.6",
                        "temp.features.featureselector.0.6",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"number_of_features": 8},
                            "function_name": "Tree-based Selection",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.7",
                        "temp.features.featureselector.0.7",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"number_of_features": 16},
                            "function_name": "Tree-based Selection",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.8",
                        "temp.features.featureselector.0.8",
                    ],
                },
                {
                    "set": [
                        {
                            "inputs": {"feature_number": 12},
                            "function_name": "Information Gain",
                        }
                    ],
                    "outputs": [
                        "temp.featureselector.0.9",
                        "temp.features.featureselector.0.9",
                    ],
                },
            ]
        }

        step_id = "selectorset"
        cached_population = []
        cached_mapped_inputs = []
        number_of_vector = 0

        (
            unique_population,
            cached_population,
            cached_mapped_inputs,
        ) = filter_steps_from_population(
            orj_population,
            step_id,
            cached_population,
            cached_mapped_inputs,
            number_of_vector,
        )

        assert len(unique_population) == 7
        assert len(cached_population) == 3
        assert cached_mapped_inputs == [
            [0, "temp.featureselector.0.0.csv.gz"],
            [0, "temp.featureselector.0.1.csv.gz"],
            [0, "temp.featureselector.0.2.csv.gz"],
        ]

        for i, _ in enumerate(orj_population["selectorset"]):
            orj_population["selectorset"][i]["set"] = (
                self.static_feature_selectors + orj_population["selectorset"][i]["set"]
            )

        step_id = "selectorset"
        cached_population = []
        cached_mapped_inputs = []
        number_of_vector = 0

        (
            unique_population,
            cached_population,
            cached_mapped_inputs,
        ) = filter_steps_from_population(
            orj_population,
            step_id,
            cached_population,
            cached_mapped_inputs,
            number_of_vector,
        )

        assert len(unique_population) == 7
        assert len(cached_population) == 3
        assert cached_mapped_inputs == [
            [0, "temp.featureselector.0.0.csv.gz"],
            [0, "temp.featureselector.0.1.csv.gz"],
            [0, "temp.featureselector.0.2.csv.gz"],
        ]

    def test_filter_set_from_population_log(self):

        list_of_steps = [
            {
                "set": [
                    {
                        "inputs": {"feature_number": 1},
                        "function_name": "Information Gain",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.5",
                    "temp.features.featureselector.0.5",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"number_of_features": 8},
                        "function_name": "Tree-based Selection",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.1",
                    "temp.features.featureselector.0.1",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 8},
                        "function_name": "Information Gain",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.3",
                    "temp.features.featureselector.0.3",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 8},
                        "function_name": "t-Test Feature Selector",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.0",
                    "temp.features.featureselector.0.0",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "Information Gain",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.9",
                    "temp.features.featureselector.0.9",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"number_of_features": 2},
                        "function_name": "Tree-based Selection",
                    }
                ],
                "outputs": ["temp.featureselector", "temp.features.featureselector"],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "t-Test Feature Selector",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.1",
                    "temp.features.featureselector.0.1",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"number_of_features": 9},
                        "function_name": "Tree-based Selection",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.1",
                    "temp.features.featureselector.0.1",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "Information Gain",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.9",
                    "temp.features.featureselector.0.9",
                ],
            },
            {
                "set": [
                    {
                        "inputs": {"feature_number": 8},
                        "function_name": "t-Test Feature Selector",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.0",
                    "temp.features.featureselector.0.0",
                ],
            },
        ]

        temp_step = {
            "set": [
                {
                    "inputs": {"number_of_features": 2},
                    "function_name": "Tree-based Selection",
                }
            ],
            "outputs": [
                "temp.featureselector.1.0",
                "temp.features.featureselector.1.0",
            ],
        }

        pipeline_output_in_log = filter_set_from_population_log(
            list_of_steps, temp_step
        )

        assert "temp.featureselector" == pipeline_output_in_log

        temp_step = {
            "set": [
                {
                    "inputs": {"feature_number": 12},
                    "function_name": "t-Test Feature Selector",
                }
            ],
            "outputs": [
                "temp.featureselector.1.1",
                "temp.features.featureselector.1.1",
            ],
        }

        pipeline_output_in_log = filter_set_from_population_log(
            list_of_steps, temp_step
        )

        assert "temp.featureselector.0.1" == pipeline_output_in_log

    def test_create_cached_population_and_cached_mapped_inputs(self):
        pipeline_output_in_log = "temp.featureselector.0.0"
        unique_population_step_id = [
            # this will be removed and output will be set to ['temp.featureselector.0.0', 'temp.features.featureselector.0.0']
            {
                "set": [
                    {
                        "inputs": {"number_of_features": 2},
                        "function_name": "Tree-based Selection",
                    }
                ],
                "outputs": [
                    "temp.featureselector.1.0",
                    "temp.features.featureselector.1.0",
                ],
            },
            # this is a unique item
            {
                "set": [
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "t-Test Feature Selector",
                    }
                ],
                "outputs": [
                    "temp.featureselector.1.1",
                    "temp.features.featureselector.1.1",
                ],
            },
        ]

        temp_step = {
            "set": [
                {
                    "inputs": {"number_of_features": 2},
                    "function_name": "Tree-based Selection",
                }
            ],
            "outputs": [
                "temp.featureselector.1.0",
                "temp.features.featureselector.1.0",
            ],
        }

        new_population = []
        new_mapped_inputs = []
        log_mapped_inputs_previous_iteration = [
            [997, "temp.featureselector.0.0.csv.gz"],
            [997, "temp.featureselector.0.1.csv.gz"],
        ]

        (
            unique_population_step_id,
            cached_population,
            cached_mapped_inputs,
        ) = create_cached_population_and_cached_mapped_inputs(
            pipeline_output_in_log,
            unique_population_step_id,
            temp_step,
            new_population,
            new_mapped_inputs,
            log_mapped_inputs_previous_iteration[0][0],
        )

        expected_unique_population_step_id = [
            {
                "set": [
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "t-Test Feature Selector",
                    }
                ],
                "outputs": [
                    "temp.featureselector.1.1",
                    "temp.features.featureselector.1.1",
                ],
            }
        ]
        assert unique_population_step_id == expected_unique_population_step_id

        expected_cached_population = [
            {
                "set": [
                    {
                        "inputs": {"number_of_features": 2},
                        "function_name": "Tree-based Selection",
                    }
                ],
                "outputs": [
                    "temp.featureselector.0.0",
                    "temp.features.featureselector.0.0",
                ],
            }
        ]
        assert cached_population == expected_cached_population

        expected_cached_mapped_inputs = [[997, "temp.featureselector.0.0.csv.gz"]]
        assert cached_mapped_inputs == expected_cached_mapped_inputs

    def test_create_cached_population_and_mapped_inputs_for_transforms(self):

        population = {}
        population["Min Max Scale"] = [
            {
                "inputs": {"input_data": "temp.featureselector.1.0.csv.gz"},
                "outputs": ["temp.scale.1.0", "temp.features.scale.1.0"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.1.4.csv.gz"},
                "outputs": ["temp.scale.1.1", "temp.features.scale.1.1"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.1.9.csv.gz"},
                "outputs": ["temp.scale.1.2", "temp.features.scale.1.2"],
            },
            # will be cached and updated
            {
                "inputs": {"input_data": "temp.featureselector.0.5.csv.gz"},
                "outputs": ["temp.scale.1.3", "temp.features.scale.1.3"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.1.csv.gz"},
                "outputs": ["temp.scale.1.4", "temp.features.scale.1.4"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.15.csv.gz"},
                "outputs": ["temp.scale.1.5", "temp.features.scale.1.5"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.24.csv.gz"},
                "outputs": ["temp.scale.1.6", "temp.features.scale.1.6"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.1.csv.gz"},
                "outputs": ["temp.scale.1.7", "temp.features.scale.1.7"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.5.csv.gz"},
                "outputs": ["temp.scale.1.8", "temp.features.scale.1.8"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.1.csv.gz"},
                "outputs": ["temp.scale.1.9", "temp.features.scale.1.9"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.1.0.csv.gz"},
                "outputs": ["temp.scale.1.10", "temp.features.scale.1.10"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.1.0.csv.gz"},
                "outputs": ["temp.scale.1.11", "temp.features.scale.1.11"],
            },
        ]

        step_id = "Min Max Scale"
        number_of_vector = 99
        mapped_inputs_previous_iteration = [[], [], [], [], [], [], [], [], []]

        (
            unique_population_step_id,
            cached_population,
            cached_mapped_inputs,
        ) = create_cached_population_and_mapped_inputs_for_transforms(
            population, step_id, number_of_vector, mapped_inputs_previous_iteration
        )

        assert unique_population_step_id == population[step_id][:3]

        expected_cached_population_outputs = [
            ["temp.scale.0.5", "temp.features.scale.0.5"],
            ["temp.scale.0.1", "temp.features.scale.0.1"],
            ["temp.scale.0.15", "temp.features.scale.0.15"],
            ["temp.scale.0.24", "temp.features.scale.0.24"],
            ["temp.scale.0.1", "temp.features.scale.0.1"],
            ["temp.scale.0.5", "temp.features.scale.0.5"],
            ["temp.scale.0.1", "temp.features.scale.0.1"],
            ["temp.scale.1.0", "temp.features.scale.1.0"],
            ["temp.scale.1.0", "temp.features.scale.1.0"],
        ]

        assert [
            i["outputs"] for i in cached_population
        ] == expected_cached_population_outputs

        expected_cached_mapped_inputs = [
            [99, "temp.scale.0.5.csv.gz"],
            [99, "temp.scale.0.1.csv.gz"],
            [99, "temp.scale.0.15.csv.gz"],
            [99, "temp.scale.0.24.csv.gz"],
            [99, "temp.scale.0.1.csv.gz"],
            [99, "temp.scale.0.5.csv.gz"],
            [99, "temp.scale.0.1.csv.gz"],
            [99, "temp.scale.1.0.csv.gz"],
            [99, "temp.scale.1.0.csv.gz"],
        ]

        assert cached_mapped_inputs == expected_cached_mapped_inputs

        population = {}
        population["Min Max Scale"] = [
            # unique steps
            {
                "inputs": {"input_data": "temp.featureselector.1.2.csv.gz"},
                "outputs": ["temp.scale.1.0", "temp.features.scale.1.0"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.1.3.csv.gz"},
                "outputs": ["temp.scale.1.1", "temp.features.scale.1.1"],
            },
            # cached steps
            {
                "inputs": {"input_data": "temp.featureselector.0.17.csv.gz"},
                "outputs": ["temp.scale.1.2", "temp.features.scale.1.2"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.3.csv.gz"},
                "outputs": ["temp.scale.1.3", "temp.features.scale.1.3"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.29.csv.gz"},
                "outputs": ["temp.scale.1.4", "temp.features.scale.1.4"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.0.csv.gz"},
                "outputs": ["temp.scale.1.5", "temp.features.scale.1.5"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.3.csv.gz"},
                "outputs": ["temp.scale.1.6", "temp.features.scale.1.6"],
            },
            # this item has the same input_data in unique set, it will be set to one in unique set
            {
                "inputs": {"input_data": "temp.featureselector.1.2.csv.gz"},
                "outputs": ["temp.scale.1.7", "temp.features.scale.1.7"],
            },
        ]

        step_id = "Min Max Scale"
        number_of_vector = 99
        mapped_inputs_previous_iteration = [[], [], [], [], [], []]

        (
            unique_population_step_id,
            cached_population,
            cached_mapped_inputs,
        ) = create_cached_population_and_mapped_inputs_for_transforms(
            population, step_id, number_of_vector, mapped_inputs_previous_iteration
        )

        assert unique_population_step_id == population[step_id][:2]

        expected_cached_population_outputs = [
            ["temp.scale.0.17", "temp.features.scale.0.17"],
            ["temp.scale.0.3", "temp.features.scale.0.3"],
            ["temp.scale.0.29", "temp.features.scale.0.29"],
            ["temp.scale.0.0", "temp.features.scale.0.0"],
            ["temp.scale.0.3", "temp.features.scale.0.3"],
            ["temp.scale.1.0", "temp.features.scale.1.0"],
        ]

        assert [
            i["outputs"] for i in cached_population
        ] == expected_cached_population_outputs

        expected_cached_mapped_inputs = [
            [99, "temp.scale.0.17.csv.gz"],
            [99, "temp.scale.0.3.csv.gz"],
            [99, "temp.scale.0.29.csv.gz"],
            [99, "temp.scale.0.0.csv.gz"],
            [99, "temp.scale.0.3.csv.gz"],
            [99, "temp.scale.1.0.csv.gz"],
        ]

        assert cached_mapped_inputs == expected_cached_mapped_inputs

    def test_update_output_of_transforms(self):

        step_id = "Min Max Scale"
        population = {}
        population[step_id] = [
            {
                "inputs": {"input_data": "temp.featureselector.0.0.csv.gz"},
                "outputs": ["temp.scale.0.0", "temp.features.scale.0.0"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.1.csv.gz"},
                "outputs": ["temp.scale.0.1", "temp.features.scale.0.1"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.2.csv.gz"},
                "outputs": ["temp.scale.0.2", "temp.features.scale.0.2"],
            },
            # will be updated
            {
                "inputs": {"input_data": "temp.featureselector.0.4.csv.gz"},
                "outputs": ["temp.scale.0.3", "temp.features.scale.0.3"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.5.csv.gz"},
                "outputs": ["temp.scale.0.4", "temp.features.scale.0.4"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.7.csv.gz"},
                "outputs": ["temp.scale.0.5", "temp.features.scale.0.5"],
            },
            {
                "inputs": {"input_data": "temp.featureselector.0.9.csv.gz"},
                "outputs": ["temp.scale.0.6", "temp.features.scale.0.6"],
            },
            # cached
            {
                "inputs": {"input_data": "temp.featureselector.0.5.csv.gz"},
                "outputs": ["temp.scale.0.6", "temp.features.scale.0.7"],
            },
        ]

        results = update_output_of_transforms(population[step_id])

        expected_results = [
            ["temp.scale.0.0", "temp.features.scale.0.0"],
            ["temp.scale.0.1", "temp.features.scale.0.1"],
            ["temp.scale.0.2", "temp.features.scale.0.2"],
            ["temp.scale.0.4", "temp.features.scale.0.4"],
            ["temp.scale.0.5", "temp.features.scale.0.5"],
            ["temp.scale.0.7", "temp.features.scale.0.7"],
            ["temp.scale.0.9", "temp.features.scale.0.9"],
            ["temp.scale.0.5", "temp.features.scale.0.5"],
        ]

        assert [i["outputs"] for i in results] == expected_results

    def test_create_cached_population_and_mapped_inputs_for_selectorset(self):

        number_of_vector = 62
        step_id = "selectorset"
        population = {}
        population[step_id] = [
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"number_of_features": 32},
                        "function_name": "Univariate Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.1.0",
                    "temp.features.featureselector.1.0",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"feature_number": 4},
                        "function_name": "Information Gain",
                    },
                ],
                "outputs": [
                    "temp.featureselector.1.1",
                    "temp.features.featureselector.1.1",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"number_of_features": 16},
                        "function_name": "Univariate Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.1.2",
                    "temp.features.featureselector.1.2",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"number_of_features": 8},
                        "function_name": "Univariate Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.1.3",
                    "temp.features.featureselector.1.3",
                ],
            },
        ]

        fitted_population_log = DataFrame(
            [
                {
                    "selectorset": {
                        "set": [
                            {
                                "function_name": "Variance Threshold",
                                "inputs": {"threshold": 0.1},
                            },
                            {
                                "function_name": "Correlation Threshold",
                                "inputs": {"threshold": 0.95},
                            },
                            {
                                "inputs": {"number_of_features": 8},
                                "function_name": "Univariate Selection",
                            },
                        ],
                        "outputs": [
                            "temp.featureselector.0.0",
                            "temp.features.featureselector.0.0",
                        ],
                    }
                },
                {
                    "selectorset": {
                        "set": [
                            {
                                "function_name": "Variance Threshold",
                                "inputs": {"threshold": 0.1},
                            },
                            {
                                "function_name": "Correlation Threshold",
                                "inputs": {"threshold": 0.95},
                            },
                            {
                                "inputs": {"feature_number": 4},
                                "function_name": "Information Gain",
                            },
                        ],
                        "outputs": [
                            "temp.featureselector.0.2",
                            "temp.features.featureselector.0.2",
                        ],
                    }
                },
            ]
        )

        (
            unique_population_step_id,
            cached_population,
            cached_mapped_inputs,
        ) = create_cached_population_and_mapped_inputs_for_selectorset(
            population, step_id, number_of_vector, fitted_population_log
        )

        assert len(cached_population) == 2
        assert [i["set"][-1] for i in cached_population] == [
            {"inputs": {"feature_number": 4}, "function_name": "Information Gain"},
            {
                "inputs": {"number_of_features": 8},
                "function_name": "Univariate Selection",
            },
        ]

        assert len(unique_population_step_id) == 2
        assert [i["set"][-1] for i in unique_population_step_id] == [
            {
                "inputs": {"number_of_features": 32},
                "function_name": "Univariate Selection",
            },
            {
                "inputs": {"number_of_features": 16},
                "function_name": "Univariate Selection",
            },
        ]

        assert cached_mapped_inputs == [
            [62, "temp.featureselector.0.2.csv.gz"],
            [62, "temp.featureselector.0.0.csv.gz"],
        ]

    def test_optimize_current_iteration(self):

        fitted_population_log = None
        step_id = "selectorset"
        iteration = 0
        mapped_inputs_previous_iteration = None
        population = {}

        population[step_id] = [
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"feature_number": 12},
                        "function_name": "t-Test Feature Selector",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.0",
                    "temp.features.featureselector.0.0",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"number_of_features": 8},
                        "function_name": "Tree-based Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.1",
                    "temp.features.featureselector.0.1",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"number_of_features": 8},
                        "function_name": "Tree-based Selection",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.2",
                    "temp.features.featureselector.0.2",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"feature_number": 2},
                        "function_name": "Information Gain",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.3",
                    "temp.features.featureselector.0.3",
                ],
            },
            {
                "set": [
                    {
                        "function_name": "Variance Threshold",
                        "inputs": {"threshold": 0.1},
                    },
                    {
                        "function_name": "Correlation Threshold",
                        "inputs": {"threshold": 0.95},
                    },
                    {
                        "inputs": {"feature_number": 2},
                        "function_name": "Information Gain",
                    },
                ],
                "outputs": [
                    "temp.featureselector.0.4",
                    "temp.features.featureselector.0.4",
                ],
            },
        ]

        (
            results_population,
            results_cached_population,
            results_cached_mapped_inputs,
        ) = optimize_current_iteration(
            None,
            deepcopy(population),
            fitted_population_log,
            step_id,
            iteration,
            mapped_inputs_previous_iteration,
            "123",
        )

        assert len(results_population[step_id]) == 3
        assert len(results_cached_population) == 2
        assert results_cached_mapped_inputs == [
            [0, "temp.featureselector.0.1.csv.gz"],
            [0, "temp.featureselector.0.3.csv.gz"],
        ]

        fitted_population_log = DataFrame(
            [
                {
                    "selectorset": {
                        "set": [
                            {
                                "function_name": "Variance Threshold",
                                "inputs": {"threshold": 0.1},
                            },
                            {
                                "function_name": "Correlation Threshold",
                                "inputs": {"threshold": 0.95},
                            },
                            {
                                "inputs": {"feature_number": 12},
                                "function_name": "t-Test Feature Selector",
                            },
                        ],
                        "outputs": [
                            "temp.featureselector.0.0",
                            "temp.features.featureselector.0.0",
                        ],
                    }
                },
                {
                    "selectorset": {
                        "set": [
                            {
                                "function_name": "Variance Threshold",
                                "inputs": {"threshold": 0.1},
                            },
                            {
                                "function_name": "Correlation Threshold",
                                "inputs": {"threshold": 0.95},
                            },
                            {
                                "inputs": {"number_of_features": 8},
                                "function_name": "Tree-based Selection",
                            },
                        ],
                        "outputs": [
                            "temp.featureselector.0.2",
                            "temp.features.featureselector.0.2",
                        ],
                    }
                },
            ]
        )

        mapped_inputs_previous_iteration = [
            [99, "temp.featureselector.0.1.csv.gz"],
            [99, "temp.featureselector.0.3.csv.gz"],
        ]

        iteration = 1

        (
            results_population,
            results_cached_population,
            results_cached_mapped_inputs,
        ) = optimize_current_iteration(
            None,
            population,
            fitted_population_log,
            step_id,
            iteration,
            mapped_inputs_previous_iteration,
            "123",
        )

        assert len(results_population[step_id]) == 1
        assert len(results_cached_population) == 4
        assert results_cached_mapped_inputs == [
            [99, "temp.featureselector.0.0.csv.gz"],
            [99, "temp.featureselector.0.2.csv.gz"],
            [99, "temp.featureselector.0.2.csv.gz"],
            [99, "temp.featureselector.0.3.csv.gz"],
        ]
