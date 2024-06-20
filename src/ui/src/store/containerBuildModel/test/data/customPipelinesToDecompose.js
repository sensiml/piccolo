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
  url: 'https://dev.sensiml.cloud/project/e87a3db8-95ad-4966-80ec-f51dbbdd4921/sandbox/f43cf6b4-86f8-40f4-8248-12a181355eaf/',
  uuid: '20fbe088-a1cd-4a58-86db-f0a36a270aef',
  name: 'Pipeline_05_23',
  pipeline: [
    {
      name: 'QueryAllSegment',
      type: 'query',
      outputs: [
        'temp.raw'
      ]
    },
    {
      name: 'Sensor Absolute Average',
      type: 'transform',
      inputs: {
        input_data: 'temp.raw',
        input_columns: [
          'AccelerometerX',
          'AccelerometerY',
          'AccelerometerZ'
        ]
      },
      outputs: [
        'temp.Sensor_Absolute_Average0'
      ],
      feature_table: null
    },
    {
      name: 'Magnitude',
      type: 'transform',
      inputs: {
        input_data: 'temp.Sensor_Absolute_Average0',
        input_columns: [
          'AccelerometerX',
          'AccelerometerY',
          'AccelerometerZ'
        ]
      },
      outputs: [
        'temp.Magnitude0'
      ],
      feature_table: null
    },
    {
      name: 'Streaming Downsample',
      type: 'transform',
      inputs: {
        input_data: 'temp.Magnitude0',
        filter_length: 1,
        group_columns: [
          'Subject',
          'Device'
        ],
        input_columns: [
          'AccelerometerX',
          'AccelerometerY',
          'AccelerometerZ'
        ]
      },
      outputs: [
        'temp.Streaming_Downsample0'
      ],
      feature_table: null
    },
    {
      name: 'Windowing',
      type: 'segmenter',
      inputs: {
        delta: 5,
        input_data: 'temp.Streaming_Downsample0',
        train_delta: 0,
        window_size: 5,
        group_columns: [
          'Device',
          'Gesture',
          'Subject',
          'capture_uuid',
          'segment_uuid'
        ],
        return_segment_index: false
      },
      outputs: [
        'temp.Windowing0'
      ],
      feature_table: null
    },
    {
      set: [
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: 'Absolute Sum'
        },
        {
          inputs: {
            columns: [
              'AccelerometerY'
            ]
          },
          function_name: 'Absolute Sum'
        },
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: 'Standard Deviation'
        },
        {
          inputs: {
            columns: [
              'GyroscopeX'
            ]
          },
          function_name: 'Standard Deviation'
        },
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: 'Interquartile Range'
        },
        {
          inputs: {
            columns: [
              'AccelerometerY'
            ]
          },
          function_name: 'Interquartile Range'
        },
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: '25th Percentile'
        },
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: 'Maximum'
        },
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: '75th Percentile'
        },
        {
          inputs: {
            columns: [
              'GyroscopeX'
            ]
          },
          function_name: '75th Percentile'
        },
        {
          inputs: {
            columns: [
              'AccelerometerX'
            ]
          },
          function_name: 'Absolute Mean'
        },
        {
          inputs: {
            columns: [
              'AccelerometerY'
            ]
          },
          function_name: 'Absolute Mean'
        },
        {
          inputs: {
            columns: [
              'GyroscopeZ'
            ]
          },
          function_name: 'Kurtosis'
        }
      ],
      name: 'generator_set',
      type: 'generatorset',
      inputs: {
        input_data: 'temp.Windowing0',
        group_columns: [
          'Device',
          'Gesture',
          'SegmentID',
          'Subject',
          'capture_uuid',
          'segment_uuid'
        ]
      },
      outputs: [
        'temp.generator_set0',
        'temp.features.generator_set0'
      ]
    },
    {
      set: [
        {
          inputs: {
            threshold: 0.01,
            Minimum_variance: 5
          },
          function_name: 'Variance Threshold'
        }
      ],
      name: 'selector_set',
      type: 'selectorset',
      inputs: {
        input_data: 'temp.generator_set0',
        label_column: 'Gesture',
        cost_function: 'sum',
        feature_table: 'temp.features.generator_set0',
        remove_columns: [],
        number_of_features: 10,
        passthrough_columns: [
          'Device',
          'Gesture',
          'SegmentID',
          'Subject',
          'capture_uuid',
          'segment_uuid'
        ]
      },
      outputs: [
        'temp.selector_set0',
        'temp.features.selector_set0'
      ],
      refinement: {}
    },
    {
      name: 'tvo',
      type: 'tvo',
      outputs: [
        'temp.tvo0',
        'temp.features.tvo0'
      ],
      input_data: 'temp.selector_set0',
      optimizers: [
        {
          name: 'Hierarchical Clustering with Neuron Optimization',
          inputs: {
            flip: 1,
            aif_method: 'max',
            singleton_aif: 0,
            cluster_method: 'kmeans',
            linkage_method: 'average',
            number_of_neurons: 5,
            centroid_calculation: 'robust',
            max_number_of_weak_vector: 1,
            min_number_of_dominant_vector: 3
          }
        }
      ],
      classifiers: [
        {
          name: 'PME',
          inputs: {
            max_aif: 16384,
            min_aif: 2,
            num_channels: 1,
            distance_mode: 'L1',
            reserved_patterns: 0,
            classification_mode: 'RBF',
            reinforcement_learning: false
          }
        }
      ],
      label_column: 'Gesture',
      feature_table: 'temp.features.selector_set0',
      ignore_columns: [
        'Device',
        'segment_uuid',
        'capture_uuid',
        'SegmentID',
        'Subject'
      ],
      validation_seed: 2,
      validation_methods: [
        {
          name: 'Stratified K-Fold Cross-Validation',
          inputs: {
            shuffle: false,
            test_size: 0,
            number_of_folds: 3
          }
        }
      ]
    }
  ],
  cache_enabled: true,
  device_config: {
    debug: false,
    budget: {},
    sram_size: null,
    test_data: '',
    application: '',
    build_flags: '',
    sample_rate: 100,
    kb_description: null,
    target_platform: 0
  },
  created_at: '2021-05-24T01:51:02.936065Z',
  result_type: 'pipeline',
  last_modified: '2021-05-24T16:24:07.722125Z',
  'private': false,
  hyper_params: null
};