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
  uuid: "3d2949e4-7744-4494-a367-b70ce89dc7a1",
  name: "Test",
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
        input_columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        input_data: "temp.raw",
      },
    },
    {
      name: "Magnitude",
      type: "transform",
      outputs: ["temp.Magnitude1"],
      inputs: {
        input_columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ", "Magnitude_ST_0000"],
        input_data: "temp.Magnitude0",
      },
    },
    {
      name: "Windowing",
      type: "segmenter",
      outputs: ["temp.Windowing0"],
      inputs: {
        delta: 105,
        train_delta: 0,
        window_size: 105,
        group_columns: ["segment_uuid", "Label"],
        return_segment_index: false,
        input_data: "temp.Magnitude1",
      },
    },
    {
      name: "Strip",
      type: "transform",
      outputs: ["temp.Strip0"],
      inputs: {
        input_columns: [
          "AccelerometerX",
          "AccelerometerY",
          "AccelerometerZ",
          "Magnitude_ST_0000",
          "Magnitude_ST_0001",
        ],
        type: "mean",
        group_columns: ["segment_uuid", "Label", "SegmentID"],
        input_data: "temp.Windowing0",
      },
    },
    {
      name: "generator_set",
      type: "generatorset",
      outputs: ["temp.generator_set0", "temp.features.generator_set0"],
      inputs: {
        input_data: "temp.Strip0",
        group_columns: ["segment_uuid", "Label", "SegmentID"],
      },
      set: [
        {
          function_name: "Average Energy",
          inputs: {
            columns: [
              "AccelerometerX",
              "AccelerometerY",
              "AccelerometerZ",
              "Magnitude_ST_0000",
              "Magnitude_ST_0001",
            ],
          },
        },
        {
          function_name: "Downsample",
          inputs: {
            columns: ["AccelerometerX"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample",
          inputs: {
            columns: ["AccelerometerY"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample",
          inputs: {
            columns: ["AccelerometerZ"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample",
          inputs: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample",
          inputs: {
            columns: ["Magnitude_ST_0001"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample Average with Normalization",
          inputs: {
            columns: ["AccelerometerX"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample Average with Normalization",
          inputs: {
            columns: ["AccelerometerY"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample Average with Normalization",
          inputs: {
            columns: ["AccelerometerZ"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample Average with Normalization",
          inputs: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
        },
        {
          function_name: "Downsample Average with Normalization",
          inputs: {
            columns: ["Magnitude_ST_0001"],
            new_length: 12,
          },
        },
      ],
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
        passthrough_columns: ["segment_uuid", "Label", "SegmentID"],
        feature_table: "temp.features.generator_set0",
        input_data: "temp.generator_set0",
      },
      set: [
        {
          function_name: "Variance Threshold",
          inputs: {
            threshold: 0.1,
          },
        },
        {
          function_name: "Correlation Threshold",
          inputs: {
            threshold: 0.95,
          },
        },
      ],
    },
    {
      name: "Isolation Forest Filtering",
      type: "sampler",
      outputs: ["temp.Isolation_Forest_Filtering0", "temp.features.Isolation_Forest_Filtering0"],
      inputs: {
        label_column: "Label",
        assign_unknown: false,
        filtering_label: ["Vertical", "Stationary", "Horizontal"],
        outliers_fraction: 0.05,
        input_data: "temp.selector_set0",
      },
      feature_table: "temp.features.selector_set0",
    },
    {
      name: "Min Max Scale",
      type: "transform",
      outputs: ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
      inputs: {
        pad: 0,
        max_bound: 255,
        min_bound: 0,
        passthrough_columns: ["segment_uuid", "Label", "SegmentID"],
        feature_min_max_defaults: null,
        feature_min_max_parameters: {},
        input_data: "temp.Isolation_Forest_Filtering0",
      },
      feature_table: "temp.features.Isolation_Forest_Filtering0",
    },
    {
      name: "tvo",
      type: "tvo",
      outputs: ["temp.tvo0", "temp.features.tvo0"],
      feature_table: "temp.features.Min_Max_Scale0",
      validation_seed: 0,
      label_column: "Label",
      ignore_columns: ["segment_uuid", "SegmentID"],
      input_data: "temp.Min_Max_Scale0",
      validation_methods: [
        {
          name: "Stratified Shuffle Split",
          inputs: {
            test_size: 0,
            number_of_folds: 1,
            validation_size: 0.2,
          },
        },
      ],
      classifiers: [
        {
          name: "Boosted Tree Ensemble",
          inputs: {},
        },
      ],
      optimizers: [
        {
          name: "RBF with Neuron Allocation Optimization",
          inputs: {
            turbo: true,
            ranking_metric: "f1_score",
            remove_unknown: false,
            number_of_neurons: 128,
            number_of_iterations: 100,
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
  created_at: "2022-04-25T23:15:48.429371Z",
  result_type: "",
  last_modified: "2022-04-25T23:15:48.461547Z",
  active: false,
  hyper_params: {
    seed: "Custom",
    params: {
      reset: true,
      set_training_algorithm: {
        xGBoost: {},
        "Random Forest": {},
        "RBF with Neuron Allocation Optimization": {},
        "Hierarchical Clustering with Neuron Optimization": {},
      },
      set_selectorset: {
        "Information Gain": {},
        "Tree-based Selection": {},
        "Univariate Selection": {},
        "t-Test Feature Selector": {},
      },
      disable_automl: false,
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
      search_steps: ["tvo"],
    },
  },
  cpu_clock_time: 0,
};
