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

const correctPPL = [
  {
    name: "Q1",
    use_session_preprocessor: false,
    type: "query",
    outputs: ["temp.raw"],
  },
  {
    name: "augmentation_set",
    type: "augmentationset",
    label_column: "Label",
    outputs: ["temp.augmentation_set0"],
    inputs: {
      label_column: "Label",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.raw",
    },
    set: [
      {
        function_name: "Random Crop",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          crop_size: 16000,
          target_labels: ["No", "Off", "On", "Yes"],
          overlap_factor: 1,
          selected_segments_size_limit: [16001, 100000],
        },
      },
    ],
  },
  {
    name: "augmentation_set",
    type: "augmentationset",
    label_column: "Label",
    outputs: ["temp.augmentation_set1"],
    inputs: {
      label_column: "Label",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.augmentation_set0",
    },
    set: [
      {
        function_name: "Random Crop",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          crop_size: 16000,
          target_labels: ["Unknown"],
          overlap_factor: 1.5,
          selected_segments_size_limit: [1, 100000],
        },
      },
    ],
  },
  {
    name: "augmentation_set",
    type: "augmentationset",
    label_column: "Label",
    outputs: ["temp.augmentation_set2"],
    inputs: {
      label_column: "Label",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.augmentation_set1",
    },
    set: [
      {
        function_name: "Time Shift",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          replace: false,
          fraction: 1,
          shift_range: [-1000, 1000],
          target_labels: ["No", "Off", "On", "Yes"],
          averaging_window_size: 100,
          selected_segments_size_limit: [1, 100000],
        },
      },
    ],
  },
  {
    name: "augmentation_set",
    type: "augmentationset",
    label_column: "Label",
    outputs: ["temp.augmentation_set3"],
    inputs: {
      label_column: "Label",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.augmentation_set2",
    },
    set: [
      {
        function_name: "Time Stretch",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          replace: false,
          fraction: 1,
          target_labels: ["No", "Off", "On", "Yes"],
          stretch_factor_range: [0.95, 1.05],
          selected_segments_size_limit: [1, 100000],
        },
      },
      {
        function_name: "Pitch Shift",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          replace: false,
          fraction: 1,
          sample_rate: 16000,
          shift_range: [-8, 8],
          input_columns: [],
          target_labels: ["No", "Off", "On", "Yes"],
          step_per_octave: 256,
          selected_segments_size_limit: [1, 100000],
        },
      },
    ],
  },
  {
    name: "augmentation_set",
    type: "augmentationset",
    label_column: "Label",
    outputs: ["temp.augmentation_set4"],
    inputs: {
      label_column: "Label",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.augmentation_set3",
    },
    set: [
      {
        function_name: "Scale Amplitude",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          replace: true,
          fraction: 3,
          scale_range: [0.5, 3],
          input_columns: [],
          target_labels: ["No", "Off", "On", "Yes"],
          selected_segments_size_limit: [1, 100000],
        },
      },
    ],
  },
  {
    name: "augmentation_set",
    type: "augmentationset",
    label_column: "Label",
    outputs: ["temp.augmentation_set5"],
    inputs: {
      label_column: "Label",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.augmentation_set4",
    },
    set: [
      {
        function_name: "Add Noise",
        inputs: {
          filter: {
            Set: ["Train"],
          },
          replace: true,
          fraction: 5,
          noise_types: ["pink", "white"],
          input_columns: [],
          target_labels: ["No", "Off", "On", "Yes"],
          background_scale_range: [50, 400],
          selected_segments_size_limit: [1, 100000],
        },
      },
    ],
  },
  {
    name: "Windowing",
    type: "segmenter",
    outputs: ["temp.Windowing0"],
    inputs: {
      delta: 320,
      train_delta: 0,
      window_size: 480,
      group_columns: ["segment_uuid", "Set", "Label"],
      return_segment_index: false,
      input_data: "temp.augmentation_set5",
    },
  },
  {
    name: "Segment Energy Threshold Filter",
    type: "transform",
    outputs: ["temp.Segment_Energy_Threshold_Filter0"],
    inputs: {
      delay: 35,
      backoff: 0,
      threshold: 1000,
      input_column: "channel_0",
      disable_train: true,
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      input_data: "temp.Windowing0",
    },
  },
  {
    name: "generator_set",
    type: "generatorset",
    outputs: ["temp.generator_set0", "temp.features.generator_set0"],
    inputs: {
      input_data: "temp.Segment_Energy_Threshold_Filter0",
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
    },
    set: [
      {
        function_name: "MFCC",
        inputs: {
          columns: ["channel_0"],
          sample_rate: 16000,
          cepstra_count: 23,
        },
      },
    ],
  },
  {
    name: "Min Max Scale",
    type: "transform",
    outputs: ["temp.Min_Max_Scale0", "temp.features.Min_Max_Scale0"],
    inputs: {
      pad: 0,
      max_bound: 255,
      min_bound: 0,
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      feature_min_max_defaults: {
        minimum: 200000,
        maximum: -200000,
      },
      feature_min_max_parameters: {},
      input_data: "temp.generator_set0",
    },
    feature_table: "temp.features.generator_set0",
  },
  {
    name: "Feature Cascade",
    type: "transform",
    outputs: ["temp.Feature_Cascade0", "temp.features.Feature_Cascade0"],
    inputs: {
      slide: false,
      num_cascades: 49,
      group_columns: ["segment_uuid", "Set", "Label", "SegmentID"],
      training_delta: 49,
      training_slide: true,
      input_data: "temp.Min_Max_Scale0",
    },
    feature_table: "temp.features.Min_Max_Scale0",
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
      passthrough_columns: ["segment_uuid", "Set", "Label", "SegmentID", "CascadeID"],
      feature_table: "temp.features.Feature_Cascade0",
      input_data: "temp.Feature_Cascade0",
    },
    set: [
      {
        function_name: "Information Gain",
        inputs: {
          feature_number: 2,
        },
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
    ignore_columns: ["segment_uuid", "Set", "SegmentID", "CascadeID"],
    input_data: "temp.selector_set0",
    validation_methods: [
      {
        name: "Split by Metadata Value",
        inputs: {
          metadata_name: "Set",
          training_values: ["Train"],
          validation_values: ["Validate"],
        },
      },
    ],
    classifiers: [
      {
        name: "TensorFlow Lite for Microcontrollers",
        inputs: {},
      },
    ],
    optimizers: [
      {
        name: "Transfer Learning",
        inputs: {
          epochs: 25,
          metrics: "accuracy",
          drop_out: 0.1,
          threshold: 0.6,
          base_model: "06364704-6a2e-11ed-a1eb-0242ac120002",
          batch_size: 32,
          input_type: "int8",
          dense_layers: [],
          learning_rate: 0.001,
          loss_function: "categorical_crossentropy",
          estimator_type: "classification",
          final_activation: "softmax",
          random_time_mask: true,
          random_bias_noise: true,
          batch_normalization: true,
          random_sparse_noise: true,
          training_size_limit: 1000,
          tensorflow_optimizer: "adam",
          random_frequency_mask: true,
          validation_size_limit: 500,
          auxiliary_augmentation: true,
          early_stopping_patience: 2,
          early_stopping_threshold: 0.9,
        },
      },
    ],
  },
];

export default correctPPL;
