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
    name: "Input Query",
    customName: "Q1",
    nextSteps: [
      "Sensor Transform",
      "Sensor Filter",
      "Segmenter",
      "Sampling Filter",
      "Augmentation",
    ],
    mandatory: true,
    type: "Query",
    subtype: ["Query"],
    transformFilter: [
      {
        Type: "Query",
        Subtype: "Query",
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: 1,
    set: false,
    id: "102bd4ff-19f0-4598-b1b8-052944d49055",
    data: {
      name: "Q1",
      use_session_preprocessor: true,
    },
    options: {
      descriptionParameters: {
        name: "Q1",
        label_column: "Label",
        columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
        metadata_columns: ["segment_uuid"],
        session: "My Training Session",
        cacheStatus: "CACHED",
        uuid: "c4f3e6f6-0365-4cd6-9734-20e58929be1e",
      },
    },
  },
  {
    name: "Sensor Transform",
    customName: "Magnitude",
    nextSteps: ["Parent"],
    mandatory: false,
    type: "Transform",
    subtype: ["Sensor"],
    transformFilter: [
      {
        Type: "Transform",
        Subtype: "Sensor",
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: null,
    set: false,
    id: "b680f8ee-e127-4295-a2b5-b55e91b2c756",
    data: {
      input_data: "temp.raw",
      input_columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ"],
      transform: "Magnitude",
    },
    options: {},
  },
  {
    name: "Sensor Transform",
    customName: "Magnitude",
    nextSteps: ["Parent"],
    mandatory: false,
    type: "Transform",
    subtype: ["Sensor"],
    transformFilter: [
      {
        Type: "Transform",
        Subtype: "Sensor",
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: null,
    set: false,
    id: "9f6259b8-4b22-4cdf-804e-b71617973eb5",
    data: {
      input_data: "temp.Magnitude0",
      input_columns: ["AccelerometerX", "AccelerometerY", "AccelerometerZ", "Magnitude_ST_0000"],
      transform: "Magnitude",
    },
    options: {},
  },
  {
    name: "Segmenter",
    customName: "Windowing",
    nextSteps: [
      "Segment Transform",
      "Segment Filter",
      "Augmentation",
      "Sampling Filter",
      "Feature Generator",
    ],
    mandatory: true,
    type: "Segmenter",
    subtype: [],
    transformFilter: [
      {
        Type: "Segmenter",
        Subtype: null,
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: 1,
    set: false,
    id: "5b4f3b64-bbb9-470d-be01-c5181ea37e0b",
    data: {
      delta: 105,
      input_data: "temp.Magnitude1",
      train_delta: 0,
      window_size: 105,
      group_columns: ["segment_uuid", "Label"],
      return_segment_index: false,
      transform: "Windowing",
    },
    options: {},
  },
  {
    name: "Segment Transform",
    customName: "Strip",
    nextSteps: ["Parent"],
    mandatory: false,
    type: "Transform",
    subtype: ["Segment"],
    transformFilter: [
      {
        Type: "Transform",
        Subtype: "Segment",
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: null,
    set: false,
    id: "f0be078b-19c5-44a9-8d12-4042773e920f",
    data: {
      type: "mean",
      input_data: "temp.Windowing0",
      group_columns: ["segment_uuid", "Label", "SegmentID"],
      input_columns: [
        "AccelerometerX",
        "AccelerometerY",
        "AccelerometerZ",
        "Magnitude_ST_0000",
        "Magnitude_ST_0001",
      ],
      transform: "Strip",
    },
    options: {},
  },
  {
    name: "Feature Generator",
    customName: "Feature Generator",
    nextSteps: [
      "Data Balancing",
      "Feature Selector",
      "Feature Transform",
      "Outlier Filter",
      "Feature Quantization",
    ],
    mandatory: true,
    type: "Feature Generator",
    subtype: [],
    transformFilter: [
      {
        Type: "Feature Generator",
        Subtype: null,
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: 1,
    set: true,
    id: "c1411d7c-17bf-4926-a9f6-9d57cc2ef5e5",
    data: [
      {
        name: "Average Energy",
        params: {
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
        name: "Downsample",
        params: {
          columns: ["AccelerometerX"],
          new_length: 12,
        },
      },
      {
        name: "Downsample",
        params: {
          columns: ["AccelerometerY"],
          new_length: 12,
        },
      },
      {
        name: "Downsample",
        params: {
          columns: ["AccelerometerZ"],
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
        name: "Downsample",
        params: {
          columns: ["Magnitude_ST_0001"],
          new_length: 12,
        },
      },
      {
        name: "Downsample Average with Normalization",
        params: {
          columns: ["AccelerometerX"],
          new_length: 12,
        },
      },
      {
        name: "Downsample Average with Normalization",
        params: {
          columns: ["AccelerometerY"],
          new_length: 12,
        },
      },
      {
        name: "Downsample Average with Normalization",
        params: {
          columns: ["AccelerometerZ"],
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
        name: "Downsample Average with Normalization",
        params: {
          columns: ["Magnitude_ST_0001"],
          new_length: 12,
        },
      },
    ],
    options: {},
  },
  {
    name: "Feature Selector",
    customName: "Feature Selector",
    nextSteps: ["Parent"],
    mandatory: false,
    type: "Feature Selector",
    subtype: [],
    transformFilter: [
      {
        Type: "Feature Selector",
        Subtype: null,
      },
    ],
    transformList: [],
    excludeTransform: ["Custom Feature Selection", "Custom Feature Selection By Index"],
    limit: 1,
    set: true,
    id: "bb88fefd-90f0-46c9-8501-9e099a7efa04",
    data: [
      {
        name: "Variance Threshold",
        params: {
          threshold: 0.1,
        },
      },
      {
        name: "Correlation Threshold",
        params: {
          threshold: 0.95,
        },
      },
    ],
    options: {},
  },
  {
    name: "Outlier Filter",
    customName: "Isolation Forest Filtering",
    nextSteps: ["Parent"],
    mandatory: false,
    type: "Sampler",
    subtype: ["Outlier Filter"],
    transformFilter: [
      {
        Type: "Sampler",
        Subtype: "Outlier Filter",
      },
    ],
    transformList: [],
    excludeTransform: [],
    limit: null,
    set: false,
    id: "ceab1eea-0cb6-4f46-bb09-15fae80381a8",
    data: {
      input_data: "temp.selector_set0",
      label_column: "Label",
      assign_unknown: false,
      filtering_label: ["Vertical", "Stationary", "Horizontal"],
      outliers_fraction: 0.05,
      transform: "Isolation Forest Filtering",
    },
    options: {},
  },
  {
    name: "Feature Quantization",
    customName: "Min Max Scale",
    nextSteps: [
      "Data Balancing",
      "Feature Selector",
      "Feature Transform",
      "Outlier Filter",
      "Training Algorithm",
      "Feature Grouping",
    ],
    mandatory: true,
    type: "",
    subtype: [],
    transformFilter: [],
    transformList: ["Min Max Scale"],
    excludeTransform: [],
    limit: 1,
    set: false,
    id: "0f956d68-6317-4da4-a9a8-900f980b987d",
    data: {
      pad: 0,
      max_bound: 255,
      min_bound: 0,
      input_data: "temp.Isolation_Forest_Filtering0",
      passthrough_columns: ["segment_uuid", "Label", "SegmentID"],
      feature_min_max_defaults: [],
      feature_min_max_parameters: {},
      transform: "Min Max Scale",
    },
    options: {},
  },
  {
    name: "Classifier",
    customName: "Boosted Tree Ensemble",
    nextSteps: ["Training Algorithm"],
    mandatory: true,
    type: "Classifier",
    subtype: [],
    transformFilter: [
      {
        Type: "Classifier",
        Subtype: null,
      },
    ],
    transformList: [],
    excludeTransform: ["TF Micro"],
    limit: 1,
    set: false,
    id: "256e91ae-1733-4864-a3f2-4c0573bca104",
    data: {
      transform: "Boosted Tree Ensemble",
    },
    options: {},
  },
  {
    name: "Training Algorithm",
    customName: "RBF with Neuron Allocation Optimization",
    nextSteps: ["Validation"],
    mandatory: true,
    type: "Training Algorithm",
    subtype: [],
    transformFilter: [
      {
        Type: "Training Algorithm",
        Subtype: null,
      },
    ],
    transformList: [],
    excludeTransform: [
      "Load Model PME",
      "Load Model TF Micro",
      "Load Model TensorFlow Lite for Microcontrollers",
      "Load Neuron Array",
    ],
    limit: 1,
    set: false,
    id: "b0263006-2bfa-489c-85e8-46bf4761786c",
    data: {
      turbo: true,
      ranking_metric: "f1_score",
      remove_unknown: false,
      number_of_neurons: 128,
      number_of_iterations: 100,
      aggressive_neuron_creation: true,
      transform: "RBF with Neuron Allocation Optimization",
    },
    options: {},
  },
  {
    name: "Validation",
    customName: "Stratified Shuffle Split",
    nextSteps: [],
    mandatory: true,
    type: "Validation Method",
    subtype: [],
    transformFilter: [
      {
        Type: "Validation Method",
        Subtype: null,
      },
    ],
    transformList: [],
    excludeTransform: ["Leave-One-Subject-Out", "Set Sample Validation", "Split by Metadata Value"],
    limit: 1,
    set: false,
    id: "e7b57e3e-234e-42ba-b228-d4a7404c1893",
    data: {
      test_size: 0,
      number_of_folds: 1,
      validation_size: 0.2,
      transform: "Stratified Shuffle Split",
    },
    options: {},
  },
];
