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

import { AUTOML_STEP } from "store/autoML/const";

export default {
  pipelineSettings: {
    ...AUTOML_STEP,
    data: {
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
      selectorset: true,
      tvo: true,
    },
    options: {},
  },
  pipeline: [
    {
      name: "Query",
      customName: "TEST_BASE_QUERY_SAME_SENSORS",
      data: {
        name: "TEST_BASE_QUERY_SAME_SENSORS",
        use_session_preprocessor: true,
      },
      options: {
        descriptionParameters: {
          name: "TEST_BASE_QUERY_SAME_SENSORS",
          label_column: "Label",
          columns: ["AccX", "AccY", "AccZ"],
          metadata_columns: ["segment_uuid"],
          session: "",
          uuid: "1",
        },
      },
    },
    {
      name: "Sensor Transform",
      customName: "Magnitude",
      data: {
        input_columns: ["AccX", "AccY", "AccZ"],
        input_data: "temp.raw",
        transform: "Magnitude",
      },
      options: {},
    },
    {
      name: "Segmenter",
      customName: "Windowing",
      data: {
        window_size: 105,
        delta: 105,
        train_delta: 0,
        return_segment_index: false,
        group_columns: ["segment_uuid", "SegmentID", "Label"],
        input_data: "temp.Magnitude0",
        transform: "Windowing",
      },
      options: {},
    },
    {
      name: "Segment Transform",
      customName: "Strip",
      data: {
        input_columns: ["AccX", "AccY", "AccZ", "Magnitude_ST_0000"],
        type: "mean",
        group_columns: ["segment_uuid", "SegmentID", "Label"],
        input_data: "temp.Windowing0",
        transform: "Strip",
      },
      options: {},
    },
    {
      name: "Feature Generator",
      customName: "Feature Generator",
      data: [
        {
          name: "Downsample",
          params: {
            columns: ["AccY"],
            new_length: 12,
          },
        },
        {
          name: "Downsample",
          params: {
            columns: ["AccZ"],
            new_length: 12,
          },
        },
        {
          name: "Downsample",
          params: {
            columns: ["AccX"],
            new_length: 12,
          },
        },
        {
          name: "Downsample",
          params: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Average with Normalization",
          params: {
            columns: ["AccY"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Average with Normalization",
          params: {
            columns: ["AccZ"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Average with Normalization",
          params: {
            columns: ["AccX"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Average with Normalization",
          params: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Max With Normaliztion",
          params: {
            columns: ["AccY"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Max With Normaliztion",
          params: {
            columns: ["AccZ"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Max With Normaliztion",
          params: {
            columns: ["AccX"],
            new_length: 12,
          },
        },
        {
          name: "Downsample Max With Normaliztion",
          params: {
            columns: ["Magnitude_ST_0000"],
            new_length: 12,
          },
        },
      ],
    },
    {
      name: "Outlier Filter",
      customName: "Isolation Forest Filtering",
      data: {
        label_column: "Label",
        filtering_label: ["Jab", "Hook", "Cross"],
        outliers_fraction: 0.05,
        assign_unknown: false,
        input_data: "temp.generator_set0",
        transform: "Isolation Forest Filtering",
      },
      options: {
        is_should_be_reviewed: true,
        message: "Review the values for the parameter: Filtering Label",
      },
    },
    {
      name: "Feature Quantization",
      customName: "Min Max Scale",
      data: {
        passthrough_columns: ["segment_uuid", "SegmentID", "Label"],
        min_bound: 0,
        max_bound: 255,
        pad: 0,
        feature_min_max_parameters: {},
        feature_min_max_defaults: [],
        input_data: "temp.Isolation_Forest_Filtering0",
        transform: "Min Max Scale",
      },
      options: {},
    },
    {
      name: "Feature Selector",
      customName: "Feature Selector",
      data: [
        {
          name: "Variance Threshold",
          params: {
            threshold: 0.01,
          },
        },
        {
          name: "Correlation Threshold",
          params: {
            threshold: 0.95,
          },
        },
        {
          name: "Recursive Feature Elimination",
          params: {
            method: "Log R",
            number_of_features: 10,
          },
        },
        {
          name: "Tree-based Selection",
          params: {
            number_of_features: 10,
          },
        },
        {
          name: "Information Gain",
          params: {
            feature_number: 2,
          },
        },
      ],
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
      options: {},
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
      options: {},
    },
    {
      name: "Validation",
      customName: "Stratified Shuffle Split",
      data: {
        test_size: 0,
        validation_size: 0.2,
        number_of_folds: 1,
        transform: "Stratified Shuffle Split",
      },
      options: {},
    },
  ],
};
