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
  url: "https://dev.sensiml.cloud/project/0e03e0e5-61ce-4376-a4cc-0fe3bac84669/sandbox/18342bc8-43af-42a7-a5aa-d29fdce5354b/",
  uuid: "20fbe088-a1cd-4a58-86db-f0a36a270aef",
  name: "AutoML_05_23",
  pipeline: [
    {
      name: "dogcommand.csv",
      type: "featurefile",
      outputs: ["temp.raw"],
      data_columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
      label_column: "Label",
      group_columns: ["Label", "SegmentID"],
    },
    {
      name: "Windowing",
      type: "segmenter",
      inputs: {
        delta: 100,
        input_data: "temp.raw",
        train_delta: 0,
        window_size: 100,
        group_columns: ["Label"],
        return_segment_index: false,
      },
      outputs: ["temp.Windowing0"],
      feature_table: null,
    },
    {
      name: "Strip",
      type: "transform",
      inputs: {
        type: "mean",
        input_data: "temp.Windowing0",
        group_columns: ["Label", "SegmentID"],
        input_columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
      },
      outputs: ["temp.Strip0"],
      feature_table: null,
    },
    {
      set: [
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Absolute Sum",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "25th Percentile",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Zero Crossing Rate",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Average Energy",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Sum",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Mean Difference",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Median",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "100th Percentile",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Sigma Crossing Rate",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Skewness",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Second Sigma Crossing Rate",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Mean Crossing Rate",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Standard Deviation",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Interquartile Range",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "75th Percentile",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Absolute Mean",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Kurtosis",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Total Energy",
        },
        {
          inputs: {
            columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
          },
          function_name: "Mean",
        },
      ],
      name: "generator_set",
      type: "generatorset",
      inputs: {
        input_data: "temp.Strip0",
        group_columns: ["Label", "SegmentID"],
      },
      outputs: ["temp.featuregenerator", "temp.features.featuregenerator"],
    },
    {
      set: [],
      name: "selectorset",
      type: "selectorset",
      inputs: {
        input_data: "temp.featuregenerator.data_0.csv.gz",
        label_column: "Label",
        cost_function: "sum",
        feature_table: "temp.features.featuregenerator",
        remove_columns: [],
        number_of_features: 30,
        passthrough_columns: ["Label", "SegmentID"],
      },
      outputs: ["temp.featureselector", "temp.features.featureselector"],
      refinement: {},
    },
    {
      name: "Min Max Scale",
      type: "transform",
      inputs: {
        max_bound: 255,
        min_bound: 0,
        input_data: "temp.featureselector",
        passthrough_columns: ["Label", "SegmentID"],
        feature_min_max_parameters: {},
      },
      outputs: ["temp.scale", "temp.features.scale"],
      feature_table: "temp.features.featureselector",
    },
    {
      name: "tvo",
      type: "tvo",
      outputs: ["temp.tvo", "temp.features.tvo"],
      input_data: "temp.scale",
      optimizers: [],
      classifiers: [],
      label_column: "Label",
      feature_table: "temp.features.scale",
      ignore_columns: ["Label", "SegmentID"],
      validation_methods: [],
    },
  ],
  cache_enabled: true,
  device_config: {
    debug: false,
    budget: {},
    sram_size: null,
    test_data: "",
    application: "",
    build_flags: "",
    sample_rate: 100,
    kb_description: null,
    target_platform: 0,
  },
  created_at: "2021-05-23T22:05:14.469849Z",
  result_type: "auto",
  last_modified: "2021-05-23T22:30:06.020107Z",
  private: false,
  hyper_params: {
    seed: "Basic Features",
    params: {
      reset: true,
      iterations: 5,
      search_steps: ["tvo"],
      single_model: false,
      allow_unknown: false,
      disable_automl: true,
      hardware_target: {
        classifiers_sram: 312,
      },
      population_size: 119,
      set_selectorset: {
        "Information Gain": {},
      },
      "prediction_target(%)": {
        accuracy: 100,
      },
      set_training_algorithm: {
        "Hierarchical Clustering with Neuron Optimization": {},
      },
      hierarchical_multi_model: true,
    },
    data_columns: ["AccelerometerZ", "AccelerometerX", "AccelerometerY"],
    label_column: "Label",
    group_columns: ["SegmentID", "Label"],
  },
};
