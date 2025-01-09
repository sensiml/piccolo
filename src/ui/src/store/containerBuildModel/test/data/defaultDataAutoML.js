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

export default [
  {
    name: "Pipeline Settings",
    customName: "Pipeline Settings",
    data: {
      reset: true,
      disable_automl: false,
      "prediction_target(%)": { f1_score: 100 },
      hardware_target: { classifiers_sram: 32000 },
      selectorset: true,
      set_selectorset: [
        "Information Gain",
        "t-Test Feature Selector",
        "Univariate Selection",
        "Tree-based Selection",
      ],
      tvo: true,
      set_training_algorithm: [
        "Hierarchical Clustering with Neuron Optimization",
        "RBF with Neuron Allocation Optimization",
        "Random Forest",
        "xGBoost",
        "Train Fully Connected Neural Network",
      ],
      iterations: 2,
      allow_unknown: false,
      population_size: 40,
      single_model: true,
      hierarchical_multi_model: false,
    },
  },
  {
    name: "Query",
    customName: "CDK_ALL_TYPES",
    data: { name: "CDK_ALL_TYPES", use_session_preprocessor: true },
    options: { is_should_be_reviewed: false },
  },
  {
    name: "Segmenter",
    customName: "Windowing",
    data: {
      group_columns: ["segment_uuid", "Type", "Subject", "Punch"],
      window_size: 250,
      delta: 250,
      train_delta: 0,
      return_segment_index: false,
      transform: "Windowing",
    },
    options: {
      is_should_be_reviewed: true,
      message:
        "Windowing has been set as the default Segmenter. The default window size is set to 1 second of data for your project. Please review/update the parameters and then click the save button to confirm.",
    },
  },
  {
    name: "Feature Generator",
    customName: "Feature Generator",
    data: [
      {
        name: "Positive Zero Crossings",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
          threshold: 100,
        },
      },
      {
        name: "Interquartile Range",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "75th Percentile",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Variance",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Mean",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Kurtosis",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Negative Zero Crossings",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
          threshold: 100,
        },
      },
      { name: "Linear Regression Stats", params: { columns: ["GyroscopeX"] } },
      { name: "Linear Regression Stats", params: { columns: ["GyroscopeY"] } },
      { name: "Linear Regression Stats", params: { columns: ["GyroscopeZ"] } },
      { name: "Linear Regression Stats", params: { columns: ["AccelerometerX"] } },
      { name: "Linear Regression Stats", params: { columns: ["AccelerometerY"] } },
      { name: "Linear Regression Stats", params: { columns: ["AccelerometerZ"] } },
      {
        name: "Skewness",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Minimum",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Maximum",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Median",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Absolute Mean",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Zero Crossings",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
          threshold: 100,
        },
      },
      {
        name: "Standard Deviation",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "25th Percentile",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "100th Percentile",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Sum",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
      {
        name: "Absolute Sum",
        params: {
          columns: [
            "GyroscopeX",
            "GyroscopeY",
            "GyroscopeZ",
            "AccelerometerX",
            "AccelerometerY",
            "AccelerometerZ",
          ],
        },
      },
    ],
    options: {
      is_should_be_reviewed: true,
      message:
        "Feature Generators are used to extract information from the input sensor data. In this form you will be able to specify the types of feature generators you would like to use along with the inputs into the feature generators and any parameters the feature generators take. Some feature generators will produce a single value and some will produce multiple. Some can also take more than one sensor input. You can select up to 250 Feature generators as part of your pipeline. See our documentation for more information about the feature generators.",
    },
  },
  {
    name: "Feature Selector",
    customName: "Feature Selector",
    data: [
      { name: "Variance Threshold", params: { threshold: 0.15 } },
      { name: "Correlation Threshold", params: { threshold: 0.95 } },
    ],
  },
  {
    name: "Feature Quantization",
    customName: "Min Max Scale",
    data: {
      passthrough_columns: ["segment_uuid", "Type", "Subject", "SegmentID", "Punch"],
      min_bound: 0,
      max_bound: 255,
      pad: 0,
      feature_min_max_parameters: {},
      is_use_feature_min_max_defaults: false,
      feature_min_max_defaults: [-100, 100],
      transform: "Min Max Scale",
    },
  },
  {
    name: "Classifier",
    customName: "PME",
    data: {
      distance_mode: "L1",
      classification_mode: "KNN",
      max_aif: 400,
      min_aif: 25,
      num_channels: 1,
      reserved_patterns: 0,
      reinforcement_learning: false,
      transform: "PME",
    },
  },
  {
    name: "Training Algorithm",
    customName: "RBF with Neuron Allocation Optimization",
    data: {
      remove_unknown: false,
      number_of_iterations: 100,
      turbo: true,
      ranking_metric: "f1_score",
      number_of_neurons: 128,
      aggressive_neuron_creation: true,
      transform: "RBF with Neuron Allocation Optimization",
    },
  },
  {
    name: "Validation Method",
    customName: "Stratified Shuffle Split",
    data: {
      test_size: 0,
      validation_size: 0.2,
      number_of_folds: 1,
      transform: "Stratified Shuffle Split",
    },
  },
];
