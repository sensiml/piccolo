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
  pipelineStepData: {
    "20fbe088-a1cd-4a58-86db-f0a36a270aef": [
      {
        index: 0,
        name: "Input Query",
        customName: "CDK_ALL_TYPES",
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
        id: "1",
        data: {
          name: "CDK_ALL_TYPES",
        },
      },
      {
        index: 1,
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
        id: "5",
        data: {
          transform: "Windowing",
          group_columns: ["segment_uuid", "Type", "Subject"],
          window_size: 250,
          delta: 250,
          return_segment_index: true,
          train_delta: 12,
        },
      },
      {
        index: 2,
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
        id: "9",
        data: [
          {
            name: "Global Peak to Peak of Low Frequency",
            params: {
              smoothing_factor: 5,
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Global Peak to Peak of High Frequency",
            params: {
              smoothing_factor: 5,
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Max Peak to Peak of first half of High Frequency",
            params: {
              smoothing_factor: 5,
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Global Peak to Peak",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Global Min Max Sum",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Mean Difference",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Mean Crossing Rate",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Zero Crossing Rate",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Sigma Crossing Rate",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Second Sigma Crossing Rate",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Threshold Crossing Rate",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              threshold: 0,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Threshold With Offset Crossing Rate",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              threshold: 0,
              offset: 0,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "MFCC",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              cepstra_count: 23,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Dominant Frequency",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Spectral Entropy",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Chromagram",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              cepstra_count: 23,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Peak Frequencies",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_type: "hanning",
              num_peaks: 2,
              min_frequency: 0,
              max_frequency: 1000,
              threshold: 0.2,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Constant Q Chromagram",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              cepstra_count: 23,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Root Mean Square",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              window_size: 400,
              delta: 12,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Spectral Centroid",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Spectral Bandwidth",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              p: 12,
              window_size: 400,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Spectral Contrast",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              number_of_bands: 5,
              frq_min: 200,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Spectral Flatness",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              window_size: 400,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Spectral Rolloff",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              roll_percent: 0.85,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Nth Order Polynomial",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              order: 12,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Tonnetz",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              margin: 12,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Zero Crossing Rate Audio",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              window_size: 400,
              delta: 12,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "VolumeDB",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              window_size: 400,
              delta: 12,
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "MFCCLib",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              cepstra_count: 23,
              window_size: 400,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Onset Strength",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Tempogram",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              window_size: 400,
              cepstra_count: 23,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
          {
            name: "Chroma Energy Normalized",
            params: {
              columns: [
                "GyroscopeX",
                "GyroscopeY",
                "GyroscopeZ",
                "AccelerometerX",
                "AccelerometerY",
                "AccelerometerZ",
              ],
              sample_rate: 16000,
              cepstra_count: 23,
              computation_source: "waveform",
              group_columns: ["segment_uuid", "Type", "Subject"],
            },
          },
        ],
      },
      {
        index: 3,
        name: "Feature Quantization",
        customName: "Min Max Scale",
        nextSteps: [
          "Data Balancing",
          "Feature Selector",
          "Feature Transform",
          "Outlier Filter",
          "Training Algorithm",
        ],
        mandatory: true,
        type: "",
        subtype: [],
        transformFilter: [],
        transformList: ["Min Max Scale"],
        excludeTransform: [],
        limit: 1,
        set: false,
        id: "14",
        data: {
          transform: "Min Max Scale",
          passthrough_columns: ["segment_uuid", "Type", "Subject"],
          max_bound: 255,
          feature_min_max_parameters: {},
          feature_min_max_defaults: [-100, 100],
          min_bound: 3323,
          pad: 12,
        },
      },
      {
        index: 4,
        name: "Classifier",
        customName: "NN 1-layer",
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
        id: "16",
        data: {
          transform: "NN 1-layer",
          num_hidden_layer: 32,
          online_learning: false,
        },
      },
      {
        index: 5,
        name: "Training Algorithm",
        customName: "NN 1-layer Optimizer",
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
        excludeTransform: ["Load Model PME", "Load Model TF Micro", "Load Neuron Array"],
        limit: 1,
        set: false,
        id: "17",
        data: {
          transform: "NN 1-layer Optimizer",
          iterations: 100,
          learning_rate: 0.01,
        },
      },
      {
        index: 6,
        name: "Validation",
        customName: "Stratified K-Fold Cross-Validation",
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
        excludeTransform: [],
        limit: 1,
        set: false,
        id: "18",
        data: {
          transform: "Stratified K-Fold Cross-Validation",
          number_of_folds: 3,
          test_size: 0,
          shuffle: false,
        },
      },
    ],
  },
};
