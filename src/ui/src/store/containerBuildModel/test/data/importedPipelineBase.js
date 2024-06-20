/*
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
*/

export default {
  uuid: "f541a185-b9f3-4544-b052-ff63eeb40b4b",
  name: "NewTestPPL",
  pipeline: [
    {
      name: "Q1",
      use_session_preprocessor: true,
      type: "query",
      outputs: ["temp.raw"],
    },
    {
      name: "Magnitude",
      type: "transform",
      outputs: ["temp.Magnitude0"],
      inputs: {
        input_columns: ["AccX", "AccY", "AccZ"],
        input_data: "temp.raw",
      },
    },
    {
      name: "Windowing",
      type: "segmenter",
      outputs: ["temp.Windowing0"],
      inputs: {
        window_size: 105,
        delta: 105,
        train_delta: 0,
        return_segment_index: false,
        group_columns: ["segment_uuid", "Subject", "Label"],
        input_data: "temp.Magnitude0",
      },
    },
    {
      name: "Strip",
      type: "transform",
      outputs: ["temp.Strip0"],
      inputs: {
        input_columns: ["AccX", "AccY", "AccZ", "Magnitude_ST_0000"],
        type: "mean",
        group_columns: ["segment_uuid", "Subject", "Label", "SegmentID"],
        input_data: "temp.Windowing0",
      },
    },
    {
      set: [
        {
          inputs: {
            columns: ["AccY"],
            new_length: 12,
          },
          function_name: "Downsample",
        },
        {
          inputs: {
            columns: ["AccZ"],
            new_length: 12,
          },
          function_name: "Downsample",
        },
        {
          inputs: {
            columns: ["AccX"],
            new_length: 12,
          },
          function_name: "Downsample",
        },
        {
          inputs: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
          function_name: "Downsample",
        },
        {
          inputs: {
            columns: ["AccY"],
            new_length: 12,
          },
          function_name: "Downsample Average with Normalization",
        },
        {
          inputs: {
            columns: ["AccZ"],
            new_length: 12,
          },
          function_name: "Downsample Average with Normalization",
        },
        {
          inputs: {
            columns: ["AccX"],
            new_length: 12,
          },
          function_name: "Downsample Average with Normalization",
        },
        {
          inputs: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
          function_name: "Downsample Average with Normalization",
        },
        {
          inputs: {
            columns: ["AccY"],
            new_length: 12,
          },
          function_name: "Downsample Max With Normaliztion",
        },
        {
          inputs: {
            columns: ["AccZ"],
            new_length: 12,
          },
          function_name: "Downsample Max With Normaliztion",
        },
        {
          inputs: {
            columns: ["AccX"],
            new_length: 12,
          },
          function_name: "Downsample Max With Normaliztion",
        },
        {
          inputs: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
          function_name: "Downsample Max With Normaliztion",
        },
      ],
      name: "generator_set",
      type: "generatorset",
      inputs: {
        input_data: "temp.Strip0",
        group_columns: ["segment_uuid", "Subject", "Label", "SegmentID"],
      },
      outputs: ["temp.generator_set0", "temp.features.generator_set0"],
    },
    {
      name: "Isolation Forest Filtering",
      type: "sampler",
      outputs: ["temp.Isolation_Forest_Filtering0", "temp.features.Isolation_Forest_Filtering0"],
      inputs: {
        label_column: "Label",
        filtering_label: ["Stationary", "Horizontal", "Vertical"],
        outliers_fraction: 0.05,
        assign_unknown: false,
        input_data: "temp.generator_set0",
      },
      feature_table: "temp.features.generator_set0",
    },
    {
      name: "Min Max Scale",
      type: "transform",
      outputs: ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
      inputs: {
        passthrough_columns: ["segment_uuid", "Subject", "Label", "SegmentID"],
        min_bound: 0,
        max_bound: 255,
        pad: 0,
        feature_min_max_parameters: {},
        feature_min_max_defaults: null,
        input_data: "temp.Isolation_Forest_Filtering0",
      },
      feature_table: "temp.features.Isolation_Forest_Filtering0",
    },
    {
      name: "selector_set",
      type: "selectorset",
      outputs: ["temp.selector_set0", "temp.features.selector_set0"],
      refinement: {},
      inputs: {
        number_of_features: 10,
        remove_columns: [],
        cost_function: "sum",
        label_column: "Label",
        passthrough_columns: ["segment_uuid", "Subject", "Label", "SegmentID"],
        feature_table: "temp.features.Min_Max_Scale0",
        input_data: "temp.Min_Max_Scale0",
      },
      set: [
        {
          function_name: "Variance Threshold",
          inputs: { threshold: 0.01 },
        },
        {
          function_name: "Correlation Threshold",
          inputs: { threshold: 0.95 },
        },
        {
          function_name: "Recursive Feature Elimination",
          inputs: { method: "Log R", number_of_features: 10 },
        },
        {
          function_name: "Tree-based Selection",
          inputs: { number_of_features: 10 },
        },
        {
          function_name: "Information Gain",
          inputs: { feature_number: 2 },
        },
      ],
    },
    {
      name: "tvo",
      type: "tvo",
      outputs: ["temp.tvo0", "temp.features.tvo0"],
      feature_table: "temp.features.selector_set0",
      validation_seed: 0,
      label_column: "Label",
      ignore_columns: ["segment_uuid", "Subject", "SegmentID"],
      input_data: "temp.selector_set0",
      validation_methods: [
        {
          name: "Stratified Shuffle Split",
          inputs: {
            test_size: 0,
            validation_size: 0.2,
            number_of_folds: 1,
          },
        },
      ],
      classifiers: [
        {
          name: "PME",
          inputs: {
            distance_mode: "L1",
            classification_mode: "KNN",
            max_aif: 400,
            min_aif: 25,
            num_channels: 1,
            reserved_patterns: 0,
            reinforcement_learning: false,
          },
        },
      ],
      optimizers: [
        {
          name: "RBF with Neuron Allocation Optimization",
          inputs: {
            remove_unknown: false,
            number_of_iterations: 100,
            turbo: true,
            ranking_metric: "f1_score",
            number_of_neurons: 128,
            aggressive_neuron_creation: true,
          },
        },
      ],
    },
  ],
  cache_enabled: true,
  cache: null,
  device_config: {
    debug: "False",
    budget: {},
    sram_size: "",
    test_data: "",
    application: "",
    build_flags: "",
    sample_rate: 100,
    kb_description: "",
    target_platform: 0,
  },
  created_at: "2022-02-09T04:13:54.306353Z",
  result_type: "",
  last_modified: "2022-02-09T04:13:54.341435Z",
  active: false,
  hyper_params: {
    seed: "Custom",
    params: {
      reset: true,
      set_training_algorithm: {
        "Hierarchical Clustering with Neuron Optimization": {},
        "RBF with Neuron Allocation Optimization": {},
        "Random Forest": {},
        xGBoost: {},
      },
      set_selectorset: {
        "Information Gain": {},
        "t-Test Feature Selector": {},
        "Univariate Selection": {},
        "Tree-based Selection": {},
      },
      disable_automl: true,
      "prediction_target(%)": {
        f1_score: 100,
      },
      hardware_target: {
        classifiers_sram: 32000,
      },
      iterations: 2,
      population_size: 40,
      allow_unknown: false,
      single_model: true,
      hierarchical_multi_model: false,
      search_steps: ["tvo", "selectorset"],
    },
  },
  cpu_clock_time: 0,
};
