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
  selectedPipeline: '20fbe088-a1cd-4a58-86db-f0a36a270aef',
  pipelineList: {
    data: [
      {
        url: 'https://dev.sensiml.cloud/project/e97e98dc-2e08-4f62-9849-4765f8990f26/sandbox/d0b30e47-8eaa-4ff9-8dca-efd191cc82f9/',
        uuid: '20fbe088-a1cd-4a58-86db-f0a36a270aef',
        name: 'test',
        pipeline: [
          {
            name: 'CDK_ALL_TYPES',
            type: 'query',
            outputs: [
              'temp.raw'
            ]
          },
          {
            name: 'Magnitude',
            type: 'transform',
            inputs: {
              input_data: 'temp.raw',
              input_columns: [
                'GyroscopeX',
                'GyroscopeY',
                'GyroscopeZ'
              ]
            },
            outputs: [
              'temp.Preprocess0'
            ],
            feature_table: null
          },
          {
            set: [
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Absolute Sum'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: '25th Percentile'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Zero Crossing Rate'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Average Energy'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Sum'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Mean Difference'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Median'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: '100th Percentile'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Sigma Crossing Rate'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Skewness'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Second Sigma Crossing Rate'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Mean Crossing Rate'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Standard Deviation'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Interquartile Range'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: '75th Percentile'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Absolute Mean'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Kurtosis'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Total Energy'
              },
              {
                inputs: {
                  columns: [
                    'GyroscopeX',
                    'GyroscopeY',
                    'GyroscopeZ',
                    'AccelerometerX',
                    'AccelerometerY',
                    'AccelerometerZ'
                  ]
                },
                function_name: 'Mean'
              }
            ],
            name: 'generator_set',
            type: 'generatorset',
            inputs: {
              input_data: 'temp.Preprocess0',
              group_columns: [
                'segment_uuid',
                'Type',
                'Subject',
                'Punch',
                'SegmentID'
              ]
            },
            outputs: [
              'temp.featuregenerator',
              'temp.features.featuregenerator'
            ]
          },
          {
            set: [],
            name: 'selectorset',
            type: 'selectorset',
            inputs: {
              input_data: 'temp.featuregenerator',
              label_column: 'Punch',
              cost_function: 'sum',
              feature_table: 'temp.features.featuregenerator',
              remove_columns: [],
              number_of_features: 30,
              passthrough_columns: [
                'segment_uuid',
                'Type',
                'Subject',
                'Punch',
                'SegmentID'
              ]
            },
            outputs: [
              'temp.featureselector',
              'temp.features.featureselector'
            ],
            refinement: {}
          },
          {
            name: 'Min Max Scale',
            type: 'transform',
            inputs: {
              max_bound: 255,
              min_bound: 0,
              input_data: 'temp.featureselector',
              passthrough_columns: [
                'segment_uuid',
                'Type',
                'Subject',
                'Punch',
                'SegmentID'
              ],
              feature_min_max_parameters: {}
            },
            outputs: [
              'temp.scale',
              'temp.features.scale'
            ],
            feature_table: 'temp.features.featureselector'
          },
          {
            name: 'tvo',
            type: 'tvo',
            outputs: [
              'temp.tvo',
              'temp.features.tvo'
            ],
            input_data: 'temp.scale',
            optimizers: [],
            classifiers: [],
            label_column: 'Punch',
            feature_table: 'temp.features.scale',
            ignore_columns: [
              'segment_uuid',
              'Type',
              'Subject',
              'Punch',
              'SegmentID'
            ],
            validation_methods: []
          }
        ],
        cache_enabled: true,
        device_config: {
          debug: 'False',
          budget: {},
          sram_size: '',
          test_data: '',
          application: '',
          build_flags: '',
          sample_rate: 100,
          kb_description: '',
          target_platform: 0
        },
        created_at: '2020-10-05T23:15:26.280614Z',
        result_type: 'auto',
        last_modified: '2021-04-27T17:22:03.781002Z',
        'private': false,
        hyper_params: {
          seed: 'Basic Features',
          params: {
            reset: true,
            magnitude: false,
            segmenter: 'Query Segments',
            iterations: 4,
            windowSize: 1024,
            data_columns: [
              'GyroscopeX',
              'GyroscopeY',
              'GyroscopeZ',
              'AccelerometerX',
              'AccelerometerY',
              'AccelerometerZ'
            ],
            label_column: 'Punch',
            search_steps: [
              'selectorset',
              'tvo'
            ],
            single_model: true,
            allow_unknown: false,
            balanced_data: false,
            group_columns: [
              'SegmentID',
              'Punch',
              'Subject',
              'Type',
              'segment_uuid'
            ],
            mutation_rate: 0.1,
            survivor_rate: 0.5,
            combine_labels: null,
            outlier_filter: false,
            demean_segments: false,
            hardware_target: {
              classifiers_sram: 32000
            },
            population_size: 100,
            recreation_rate: 0.2,
            validation_method: {
              name: 'Stratified K-Fold Cross-Validation',
              inputs: {
                test_size: 0,
                metadata_name: 'segment_uuid',
                number_of_folds: 5,
                validation_size: 0.2
              }
            },
            'prediction_target(%)': {
              accuracy: 100
            },
            hierarchical_multi_model: false,
            magnitudeColumnsOfInterest: []
          }
        }
      },
    ],
    isFetching: false
  }
}