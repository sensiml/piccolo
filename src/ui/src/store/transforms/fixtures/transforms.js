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
    uuid: "4f2f95e9-e7e5-4cc9-9272-03721b529e76",
    name: "Positive Zero Crossings",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "numeric",
        range: [-32767, 32766],
        c_param: 0,
        default: 100,
        description: "value in addition to mean which must be crossed to count as a crossing",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the number of times the selected input crosses the mean+threshold and mean-threshold values with a positive slope. The threshold value is specified by the user.\n    crossing the mean value when the threshold is 0 only counts as a single crossing.\n\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n        threshold: value in addition to mean which must be crossed to count as a crossing\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "edf25974-e583-408b-9de0-df8c8859fd05",
    name: "Pre-emphasis Filter",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_column",
        type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "alpha",
        type: "float",
        range: [0.1, 1],
        c_param: 0,
        default: 0.97,
      },
      {
        name: "prior",
        type: "int",
        range: [-32768, 32767],
        c_param: 1,
        default: 0,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      'Performs a pre-emphasis filter on the input columns and modifies the sensor\n    streams in place. This is a first-order Fir filter that performs a weighted\n    average of each sample with the previous sample.\n\n    Args:\n        input_column (str): sensor stream to apply pre_emphasis filter against\n        alpha (float): pre-emphasis factor (weight given to the previous sample)\n        prior (int): the value of the previous sample, default is 0\n\n    Returns:\n        input data after having been passed through a pre-emphasis filter\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n        >>> client.pipeline.set_input_data(\'test_data\', df, force=True)\n\n        >>> client.pipeline.add_transform("Pre-emphasis Filter",\n                           params={"input_column": \'accelx\',\n                                "alpha": 0.97,\n                                "prior": 2})\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                       Class  Rep Subject  accelx  accely  accelz\n                0   Crawling    1     s01     187     569    4019\n                1   Crawling    1     s01      -5     594    4051\n                2   Crawling    1     s01      -7     638    4049\n                3   Crawling    1     s01       8     678    4053\n                4   Crawling    1     s01      21     708    4051\n                5   Crawling    1     s01      24     733    4028\n                6   Crawling    1     s01      26     733    3988\n                7   Crawling    1     s01      27     696    3947\n                8   Crawling    1     s01      20     677    3943\n                9   Crawling    1     s01      12     695    3988\n                10  Crawling    1     s01    -257    2558    4609\n                11   Running    1     s01     -23   -3971     843\n                12   Running    1     s01      -3   -3982     836\n                13   Running    1     s01       1   -3973     832\n                14   Running    1     s01       0   -3973     834\n                15   Running    1     s01      -5   -3978     844\n                16   Running    1     s01      -3   -3993     842\n                17   Running    1     s01      -7   -3984     821\n                18   Running    1     s01      -1   -3966     813\n                19   Running    1     s01      -2   -3971     826\n                20   Running    1     s01       1   -3988     827\n                21   Running    1     s01       1   -3984     843\n\n\n    ',
    type: "Transform",
    subtype: "Segment",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "d1b6b0c9-c935-42fb-8349-1737192f9c62",
    name: "Pad Segment",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
      },
      {
        name: "sequence_length",
        type: "int",
      },
      {
        name: "noise",
        type: "int",
        default: 0,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Pad a segment so that its length is equal to a specific sequence length\n\n    Args:\n        input_data (DataFrame): input DataFrame\n        group_columns (str): The column to group by against (should 283 SegmentID)\n        sequence_length (int): Specifies the size of the minimum class to use, if None we will use\n         the min class size. If size is greater than min class size we use min class size (default: None)\n        noise_level (int): max amount of noise to add to augmentation\n    Returns:\n        DataFrame containing padded segments\n\n    ",
    type: "Sampler",
    subtype: "Segment",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "809affe8-ab74-4911-b5e3-cc203f194eef",
    name: "Set Sample Validation",
    input_contract: [
      {
        name: "set_mean",
        type: "list",
        default: [],
      },
      {
        name: "set_stdev",
        type: "list",
        default: [],
      },
      {
        name: "mean_limit",
        type: "list",
        default: [],
      },
      {
        name: "stdev_limit",
        type: "list",
        default: [],
      },
      {
        name: "retries",
        type: "int",
        range: [1, 25],
        default: 5,
      },
      {
        name: "samples_per_class",
        type: "dict",
        default: {},
      },
      {
        name: "validation_samples_per_class",
        type: "dict",
        default: {},
      },
      {
        name: "norm",
        type: "str",
        default: "L1",
        options: [
          {
            name: "L1",
          },
          {
            name: "Lsup",
          },
        ],
      },
      {
        name: "optimize_mean_std",
        type: "str",
        default: "both",
        options: [
          {
            name: "both",
          },
          {
            name: "mean",
          },
        ],
      },
      {
        name: "binary_class1",
        type: "str",
      },
    ],
    output_contract: [],
    description:
      "\n    A validation scheme wherein the data set is divided into training and test sets based\n    on two statistical parameters, mean and standard deviation. The user selects the number\n    of events in each category and has the option to select the subset mean, standard deviation,\n    number in the validation set and the acceptable limit in the number of retries of random selection\n    from the original data set.\n\n\n    Example:\n     samples = {'Class 1':2500, \"Class 2\":2500}\n     validation = {'Class 1':2000, \"Class 2\":2000}\n\n     client.pipeline.set_validation_method({\"name\": \"Set Sample Validation\",\n                                         \"inputs\": {\"samples_per_class\": samples,\n                                                    \"validation_samples_per_class\": validation}})\n\n    Args:\n        data_set_mean (numpy.array[floats]): mean value of each feature in dataset\n        data_set_stdev (numpy.array[floats]): standard deviation of each feature in dataset\n        samples_per_class (dict): Number of members in subset for training, validation,\n            and testing\n        validation_samples_per_class (dict): Overrides the number of members in subset for\n            validation if not empty\n        mean_limit (numpy.array[floats]): minimum acceptable difference between mean of\n            subset and data for any feature\n        stdev_limit (numpy.array[floats]): minimum acceptable difference between standard\n            deviation of subset and data for any feature\n        retries (int): Number of attempts to find a subset with similar statistics\n        norm (list[str]): ['Lsup','L1'] Distance norm for determining whether subset is\n            within user defined limits\n        optimize_mean_std (list[str]): ['both','mean'] Logic to use for optimizing subset.\n            If 'mean', then only mean distance must be improved. If 'both', then both mean\n            and stdev must improve.\n        binary_class1 (str): Category name that will be the working class in set composition\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "54d039a2-e9ef-4435-91a7-23398fb37daa",
    name: "Average Time Over Threshold",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Offset to check for percent time over",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description: "\n    Average of the time spent above threshold for all times crossed.\n\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "cebcac42-7ef4-421e-b501-0d7ea5e8468f",
    name: "Interquartile Range",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "\n    The IQR (inter quartile range) of a vector V with N items, is the\n    difference between  the 75th percentile and 25th percentile value.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Interquartile Range',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxIQR  gen_0002_accelyIQR  gen_0003_accelzIQR\n            0     s01                 4.0                 2.0                 2.0\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "ad723f6a-40f6-49e8-b500-35c780c6bcac",
    name: "75th Percentile",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "\n    Computes the 75th percentile of each column in 'columns' in the dataframe.\n    A q-th percentile of a vector V of length N is the q-th ranked value in a\n    sorted copy of V. If the normalized ranking doesn't match the q exactly,\n    interpolation is done on two nearest values.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with 75th percentile of each specified column.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'75th Percentile',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n              Subject  gen_0001_accelx75Percentile  gen_0002_accely75Percentile  gen_0003_accelz75Percentile\n            0     s01                          2.0                          8.0                          7.0\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e1c3f7a2-734d-489f-96e1-b918778035fc",
    name: "Min Column",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: -1,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Returns the index of the column with the min value for each segment.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector with index of max abs value column.\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "dabc426d-99de-416c-a548-fbc8f28c5012",
    name: "Global Peak to Peak of Low Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Global peak to peak of low frequency. The low frequency signal is calculated by\n    applying a moving average filter with a smoothing factor.\n\n    Args:\n        smoothing_factor (int); Determines the amount of attenuation for\n          frequencies over the cutoff frequency.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame of `global p2p low frequency` for each column and the specified group_columns\n\n    Examples:\n        >>> import numpy as np\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Global Peak to Peak of Low Frequency',\n                                     'params':{\"smoothing_factor\": 5,\n                                               \"columns\": ['accelx','accely','accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelxMaxP2PGlobalDC  gen_0002_accelyMaxP2PGlobalDC  gen_0003_accelzMaxP2PGlobalDC\n            0      0     s01                     195.600006                     191.800003                     187.000000\n            1      1     s01                     195.600006                     191.800003                     185.800003\n\n    ",
    type: "Feature Generator",
    subtype: "Amplitude",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "6260e942-0427-4ee8-a999-c9b897881443",
    name: "Global Peak to Peak of High Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Global peak to peak of high frequency. The high frequency signal is calculated by\n    subtracting the moving average filter output from the original signal.\n\n    Args:\n        smoothing_factor (int); Determines the amount of attenuation for frequencies\n          over the cutoff frequency. The number of elements in individual\n          columns should be al least three times the smoothing factor.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame of `global p2p high frequency` for each column and the specified group_columns\n\n    Examples:\n        >>> import numpy as np\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Global Peak to Peak of High Frequency',\n                                     'params':{\"smoothing_factor\": 5,\n                                               \"columns\": ['accelx','accely','accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelxMaxP2PGlobalAC  gen_0002_accelyMaxP2PGlobalAC  gen_0003_accelzMaxP2PGlobalAC\n            0      0     s01                            3.6                            7.8                      86.400002\n            1      1     s01                            3.6                            7.8                     165.000000\n\n    ",
    type: "Feature Generator",
    subtype: "Amplitude",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c2d5036f-1077-412b-96d2-4a2efbe5edb7",
    name: "Variance of Movement Intensity",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Variance of movement intensity\n\n    Args:\n        columns:  List of str; The `columns` represents a list of all\n                  column names on which `average_energy` is to be found.\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print(df)\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Variance of Movement Intensity',\n                                     'params':{ \"columns\": ['accelx','accely','accelz'] }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print(result)\n            out:\n              Subject  gen_0000_VarInt\n            0     s01         3.082455\n    ",
    type: "Feature Generator",
    subtype: "Physical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "41f90002-d669-4215-8393-06f771eb3912",
    name: "Histogram",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Column on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "range_left",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: -32000,
      },
      {
        name: "range_right",
        type: "int",
        range: [-32768, 32767],
        c_param: 1,
        default: 32000,
      },
      {
        name: "number_of_bins",
        type: "int",
        range: [1, 255],
        c_param: 2,
        default: 32,
      },
      {
        name: "scaling_factor",
        type: "int",
        range: [1, 255],
        c_param: 3,
        default: 255,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "params['number_of_bins']",
        scratch_buffer: {
          name: "number_of_bins",
          type: "parameter",
        },
      },
    ],
    description:
      "\n    Translates to the data stream(s) from a segment into a feature vector in histogram space.\n\n    Args:\n        column (list of strings): name of the sensor streams to use\n        range_left (int): the left limit (or the min) of the range for a fixed bin histogram\n        range_right (int): the right limit (or the max) of the range for a fixed bin histogram\n        number_of_bins (int, optional): the number of bins used for the histogram\n        scaling_factor (int, optional): scaling factor used to fit for the device\n\n    Returns:\n        DataFrame: feature vector in histogram space.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Histogram',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"range_left\": 10,\n                                               \"range_right\": 1000,\n                                               \"number_of_bins\": 5,\n                                               \"scaling_factor\": 254 }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0000_hist_bin_000000  gen_0000_hist_bin_000001  gen_0000_hist_bin_000002  gen_0000_hist_bin_000003  gen_0000_hist_bin_000004\n            0  Crawling    1     s01                       8.0                      38.0                      46.0                      69.0                       0.0\n            1   Running    1     s01                      85.0                       0.0                       0.0                       0.0                      85.0\n\n    ",
    type: "Feature Generator",
    subtype: "Histogram",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "0e555c6e-6a39-40fa-a847-795211c208b8",
    name: "Total Energy",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Total Energy.\n\n    1) Calculate the element-wise abs sum of the input columns.\n    2) Sum the energy values over all streams to get the total energy.\n\n    Args:\n        columns:  List of str; The `columns` represents a list of all column names\n                 on which total energy is to be found.\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Total Energy',\n                                     'params':{ \"columns\": ['accelx','accely','accelz'] }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0000_TotEng\n            0     s01            475.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Energy",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b81badac-bf39-4d27-8df2-3357cd4e976b",
    name: "Downsample",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "new_length",
        type: "int",
        range: [5, 32],
        c_param: 0,
        default: 12,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: true,
        output_formula: "params['new_length']*len(params['columns'])",
      },
    ],
    description:
      "\n    This function takes a dataframe `input_data` as input and performs group by operation on specified `group_columns`.\n    For each group, it drops the `passthrough_columns` and performs downsampling on the remaining columns by following steps:\n\n    - Divide the entire column into windows of size total length/`new_length`.\n    - Calculate mean for each window.\n    - Concatenate all the mean values.\n    - The length of the downsampled signal is equal to `new length`.\n\n    Then all such means are concatenated to get `new_length` * # of columns. These constitute features in downstream analyses.\n    For instance, if there are three columns and the `new_length` value is 12, then total number of means we get is 12 * 3 = 36.\n    Each will represent a feature.\n\n    Args:\n        input_data (DataFrame): Input pandas dataframe.\n        columns (List[str]): List of column names to perform downsampling.\n        new_length (int): Downsampled length. Defaults to 12.\n\n    Returns:\n        DataFrame: DataFrame containing Downsampled Feature Vector.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx'],\n                                               \"new_length\": 5}}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0001_accelx_0  gen_0001_accelx_1  gen_0001_accelx_2  gen_0001_accelx_3  gen_0001_accelx_4\n            0  Crawling    1     s01              367.0              336.5              391.0              471.0              523.0\n            1   Running    1     s01              -45.5              -41.5              -50.0              -64.0              -64.0\n\n    ",
    type: "Feature Generator",
    subtype: "Sampling",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "52b24500-df46-4b5f-a27f-da5afb672544",
    name: "Undersample Majority Classes",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "target_class_size",
        type: "int",
        default: null,
      },
      {
        name: "maximum_samples_size_per_class",
        type: "int",
        default: null,
      },
      {
        name: "seed",
        type: "int",
        default: null,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Create a balanced data set by undersampling the majority classes using random sampling without replacement.\n\n    Args:\n        input_data (DataFrame): input DataFrame\n        label_column (str): The column to split against\n        target_class_size (int): Specifies the size of the minimum class to use, if None we will use\n         the min class size. If size is greater than min class size we use min class size (default: None)\n        seed (int): Specifies a random seed to use for sampling\n        maximum_samples_size_per_class(int): Specifies the size of the maximum class to use per class,\n\n    Returns:\n        DataFrame containing undersampled classes\n\n    ",
    type: "Sampler",
    subtype: "Balance Data",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4640f392-c40e-46d8-88fb-3b96fb1e3fd5",
    name: "Sigma Outliers Filtering",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "filtering_label",
        type: "list",
        default: [],
        description:
          "List of classes that will be filered. If it is not defined, all class will be filtered.",
        display_name: "Filtering Label",
      },
      {
        name: "feature_columns",
        type: "list",
        default: [],
        description: "List of features. if it is not defined, it uses all features.",
        display_name: "Feature Columns",
      },
      {
        name: "sigma_threshold",
        type: "float",
        range: [2, 4],
        default: 3,
        description: "Define the ratio of outliers.",
        display_name: "Sigma Threshold",
      },
      {
        name: "assign_unknown",
        type: "bool",
        default: false,
        description: "Assign unknown label to outliers.",
        display_name: "Assign Unknown",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    A sigma outlier filter algorithm is a technique used to identify and remove\n    outliers from feature vectors based on their deviation from the mean. In this\n    algorithm, an outlier is defined as a data point that falls outside a certain\n    number of standard deviations (sigma) from the mean of the distribution.\n\n\n\n    Args:\n        input_data (DataFrame): The feature set that is a result of either a generator_set or feature_selector.\n        label_column (str): The label column name.\n        filtering_label (str): List of classes that will be filtered. If it is not defined, all classes\n                                       will be filtered.\n        feature_columns (list of str): List of features. If it is not defined, it uses all features.\n        sigma_threshold (float): Defines the ratio of outliers.\n        assign_unknown (bool): Assigns an unknown label to outliers.\n\n    Returns:\n        DataFrame: The filtered DataFrame containing features without outliers and noise.\n\n        Examples:\n\n            .. code-block:: python\n\n                client.pipeline.reset(delete_cache=False)\n                df = client.datasets.load_activity_raw()\n                client.pipeline.set_input_data('test_data', df, force=True,\n                                data_columns = ['accelx', 'accely', 'accelz'],\n                                group_columns = ['Subject','Class'],\n                                label_column = 'Class')\n                client.pipeline.add_feature_generator([{'name':'Downsample',\n                                        'params':{\"columns\": ['accelx','accely','accelz'],\n                                                \"new_length\": 5 }}])\n                results, stats = client.pipeline.execute()\n                # List of all data indices before the filtering algorithm\n                results.index.tolist()\n                # Out:\n                # [0, 1, 2, 3, 4, 5, 6, 7, 8]\n\n                client.pipeline.add_transform(\"Sigma Outliers Filtering\",\n                            params={ \"sigma_threshold\": 1.0 })\n\n                results, stats = client.pipeline.execute()\n                # List of all data indices after the filtering algorithm\n                results.index.tolist()\n                # Out:\n                # [0, 1, 2, 3, 4, 5]\n\n    ",
    type: "Sampler",
    subtype: "Outlier Filter",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "74c10378-0815-4f5f-a9d6-46965db722c8",
    name: "Local Outlier Factor Filtering",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "filtering_label",
        type: "list",
        default: [],
        description: "List of classes.",
        display_name: "Filtering Label",
      },
      {
        name: "feature_columns",
        type: "list",
        default: [],
        description: "List of features.",
        display_name: "Feature Columns",
      },
      {
        name: "outliers_fraction",
        type: "float",
        range: [0.01, 1],
        default: 0.05,
        description: "Define the ratio of outliers.",
        display_name: "Outliers Fraction",
      },
      {
        name: "number_of_neighbors",
        type: "int",
        range: [5, 500],
        default: 50,
        description: "Number of neighbors for a vector.",
        display_name: "Number Of Neighbors",
      },
      {
        name: "norm",
        type: "str",
        default: "L1",
        description: "Metric that will be used for the distance computation.",
        display_name: "Distance Norm",
      },
      {
        name: "assign_unknown",
        type: "bool",
        default: false,
        description: "Assign unknown label to outliers.",
        display_name: "Assign Unknown",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    The local outlier factor (LOF) to measure the local deviation of a given data point with respect\n    to its neighbors by comparing their local density.\n\n    The LOF algorithm is an unsupervised outlier detection method which computes the local density\n    deviation of a given data point with respect to its neighbors. It considers as outlier samples\n    that have a substantially lower density than their neighbors.\n\n    Args:\n        input_data: Dataframe, feature set that is results of generator_set or feature_selector\n        label_column (str): Label column name.\n        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.\n        feature_columns: List<String>, List of features. if it is not defined, it uses all features.\n        outliers_fraction (float) : Define the ratio of outliers.\n        number_of_neighbors (int) : Number of neighbors for a vector.\n        norm (string) : Metric that will be used for the distance computation.\n        assign_unknown (bool): Assign unknown label to outliers.\n\n    Returns:\n        DataFrame containing features without outliers and noise.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices before the filtering algorithm\n        >>> results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5, 6, 7, 8]\n\n        >>> client.pipeline.add_transform(\"Local Outlier Factor Filtering\",\n                           params={\"outliers_fraction\": 0.05,\n                                    \"number_of_neighbors\": 5})\n\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices after the filtering algorithm\n        >>>results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5]\n\n    ",
    type: "Sampler",
    subtype: "Outlier Filter",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "38712cff-3321-4d90-8808-b146b3048249",
    name: "Percent Time Over Zero",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Percentage of samples in the series that are positive.\n\n    Args:\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Zero',\n                                     'params':{\"columns\": ['accelx','accely','accelz'] }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                Class  Rep Subject  gen_0001_accelxPctTimeOverZero  gen_0002_accelyPctTimeOverZero  gen_0003_accelzPctTimeOverZero\n          0  Crawling    1     s01                        0.909091                             1.0                             1.0\n          1   Running    1     s01                        0.000000                             0.0                             1.0\n\n\n\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "5daf8892-9b39-42dd-b982-341cad992adb",
    name: "Max Column",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: -1,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Returns the index of the column with the max value for each segment.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector with index of max column.\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "f29cf61c-bda7-495c-9df6-fb629012d6cd",
    name: "Vertical AutoScale Segment",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Scale the amplitude of the input columns to MAX_INT_16 or as close as possible without overflowing.\n    Scaling is only applied to the input columns; other sensor columns will be ignored.\n\n    Args:\n        input_data (DataFrame): Input data to be vertically scaled.\n        input_columns (list): List of column names to be vertically scaled.\n        group_columns (list): List of column names on which grouping is to be done. Each group will be scaled one at a time.\n\n    Returns:\n        DataFrame: The vertically scaled DataFrame for each segment for input_columns.\n    ",
    type: "Transform",
    subtype: "Segment",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "43a94d26-46bc-4758-b012-a669edb175b1",
    name: "Transfer Learning",
    input_contract: [
      {
        name: "base_model",
        type: "str",
        element_type: "UUID",
      },
      {
        name: "final_activation",
        type: "str",
        default: "softmax",
        options: [
          {
            name: "softmax",
          },
          {
            name: "sigmoid",
          },
        ],
      },
      {
        name: "dense_layers",
        type: "list",
        range: [1, 256],
        default: [],
        description:
          "The size of each dense layer. If dense layer is empty, the base models head will be used instead.",
        element_type: "int",
      },
      {
        name: "training_size_limit",
        type: "int",
        range: [1, 5000],
        default: 1000,
        description:
          "Maximum number of training samples per labels. At each training epoch, data is randomly resampled to have even distribution across all labels.",
      },
      {
        name: "validation_size_limit",
        type: "int",
        range: [1, 2000],
        default: 500,
        description:
          "Maximum number of validation samples per labels. The validation sample is suggested to be at least as large as 20% of the training sample. At eah epoch, validation set is used to evaluate the early stopping condition.",
      },
      {
        name: "batch_normalization",
        type: "bool",
        default: true,
        description: "Apply batch normalization after each dense layer",
      },
      {
        name: "drop_out",
        type: "float",
        range: [0, 0.2],
        default: 0.1,
        description: "Apply drop out after each dense layer",
      },
      {
        name: "random_sparse_noise",
        type: "bool",
        default: false,
        description: "Augmentation using additional bias on pixels chosen randomly.",
      },
      {
        name: "random_bias_noise",
        type: "bool",
        default: false,
        description: "Augmentation using additional random bias along row and/or columns.",
      },
      {
        name: "random_frequency_mask",
        type: "bool",
        default: false,
        description: "Augmentation by masking features at random frequency rows.",
      },
      {
        name: "random_time_mask",
        type: "bool",
        default: false,
        description: "Augmentation by masking features at random time columns.",
      },
      {
        name: "auxiliary_augmentation",
        type: "bool",
        default: false,
        description: "Augmentation using auxiliary data.",
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "TensorFlow Lite for Microcontrollers",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "class_map",
        type: "dict",
        default: null,
        handle_by_set: true,
      },
      {
        name: "epochs",
        type: "int",
        range: [1, 100],
        default: 5,
      },
      {
        name: "batch_size",
        type: "int",
        range: [8, 128],
        default: 32,
      },
      {
        name: "threshold",
        type: "float",
        range: [0, 1],
        default: 0.8,
        description: "Threshold value below which the classification will return Unknown.",
      },
      {
        name: "early_stopping_threshold",
        type: "float",
        range: [0.5, 1],
        default: 0.8,
        description:
          "Early stopping threshold to stop training when the validation accuracy stops improving.",
      },
      {
        name: "early_stopping_patience",
        type: "int",
        range: [0, 5],
        default: 2,
        description:
          "The number of epochs after the early stopping threshold was reached to continue training.",
      },
      {
        name: "loss_function",
        type: "str",
        default: "categorical_crossentropy",
        options: [
          {
            name: "categorical_crossentropy",
          },
          {
            name: "binary_crossentropy",
          },
          {
            name: "poisson",
          },
          {
            name: "kl_divergence",
          },
        ],
      },
      {
        name: "learning_rate",
        type: "float",
        range: [0, 0.2],
        default: 0.01,
        description: "The learning rate to apply during training",
      },
      {
        name: "tensorflow_optimizer",
        type: "str",
        default: "adam",
        options: [
          {
            name: "adam",
          },
          {
            name: "SGD",
          },
        ],
      },
      {
        name: "metrics",
        type: "str",
        default: "accuracy",
        options: [
          {
            name: "accuracy",
          },
        ],
        description: "The metric reported during the training.",
      },
      {
        name: "input_type",
        type: "str",
        default: "int8",
        options: [
          {
            name: "int8",
          },
        ],
        description: "use int8 as input. Typically Accelerated OPS require int8.",
      },
      {
        name: "estimator_type",
        type: "str",
        default: "classification",
        options: [
          {
            name: "classification",
          },
          {
            name: "regression",
          },
        ],
      },
    ],
    output_contract: [],
    description: "Apply transfer learning to a pre-trained TensorFlow model.",
    type: "Training Algorithm",
    subtype: "Neural Network",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "91d6b642-b157-45a0-aa6d-c12276da6c41",
    name: "Two Column Peak Location Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Computes the location of the maximum value for each column and then finds the difference\n       between those two points.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector mean difference\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b9bd8029-731f-4db1-8825-7e0c166d8e1b",
    name: "Duration of the Signal",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Duration of the signal. It is calculated by dividing the length of vector\n    by the sampling rate.\n\n    Args:\n        sample_rate: float; Sampling rate\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Duration of the Signal',\n                                     'params':{\"columns\": ['accelx'] ,\n                                               \"sample_rate\": 10\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n               Subject  gen_0001_accelxDurSignal\n             0     s01                       0.5\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "508f3eb6-53ad-42fb-8534-8276afc93287",
    name: "Variance Threshold",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "threshold",
        type: "float",
        default: 0.01,
        description:
          "Minimum variance threshold under which features should be eliminated (0 to ~)",
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "The set of columns the selector should ignore",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Feature selector that removes all low-variance features.\n\n    This step is an unsupervised feature selection algorithm and looks only at the input features (X) and not the Labels\n    or outputs (y). Select features whose variance exceeds the given threshold (default is set to 0.05). It should be\n    applied prior to standardization.\n\n    Args:\n        input_data (DataFrame): Input data.\n        threshold (float): [Default 0.01] Minimum variance threshold under which features should be eliminated.\n        passthrough_columns (list): [Optional] A list of columns to include in the output DataFrame in addition to\n            the selected features.\n\n    Returns:\n        tuple: tuple containing:\n            selected_features (DataFrame): which includes selected features and the passthrough columns.\n            unselected_features (list): unselected features\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.add_feature_selector([{'name':'Variance Threshold',\n                                    'params':{\"threshold\": 4513492.05}}])\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4']\n\n    ",
    type: "Feature Selector",
    subtype: "Unsupervised",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "0e5794e1-e61d-49a1-b18b-cc11efe3862a",
    name: "Percent Time Over Second Sigma",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Percentage of samples in the series that are above  the sample mean + two sigma\n\n    Args:\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Second Sigma',\n                                     'params':{\"columns\": ['accelx','accely','accelz'] }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0001_accelxPctTimeOver2ndSigma  gen_0002_accelyPctTimeOver2ndSigma  gen_0003_accelzPctTimeOver2ndSigma\n            0  Crawling    1     s01                                 0.0                            0.090909                            0.090909\n            1   Running    1     s01                                 0.0                            0.000000                            0.000000\n\n\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "51ab0fb2-cdc6-400a-a878-b2f6f465395d",
    name: "Sensor Average",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "Average",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the average of a signal across the input_columns streams.\n\n    Args:\n        input_data: DataFrame containing the time series data\n        input_columns: sensor streams to use in computing the average\n\n    Returns:\n        The input DataFrame with an additional column containing the per-sample\n        average of the desired input_columns\n    ",
    type: "Transform",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "93af61c0-3a5e-46bd-a682-ce838b1bded2",
    name: "Percent Time Over Threshold",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Offset to check for percent time over",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Percentage of samples in the series that are above threshold\n\n    Args:\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Threshold',\n                                     'params':{\"columns\": ['accelx','accely','accelz'] }}])\n        >>> results, stats = client.pipeline.execute()\n\n\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "13705fcc-703b-48b8-8bc3-aa0ca8b7b4a5",
    name: "Correlation Threshold",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "threshold",
        type: "float",
        default: 0.95,
        description:
          "Maximum correlation     threshold over which features should be eliminated (0 to 1)",
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "The set of columns the selector should ignore",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n\n    Correlation feature selection is an unsupervised feature selection algorithm that aims\n    to select features based on their absolute correlation with the other features in the\n    dataset. The algorithm begins by computing a pairwise correlation matrix of all the\n    features. It then proceeds to identify a candidate feature for removal, which is the\n    feature that correlates with the highest number of other features that have a correlation\n    coefficient greater than the specified `threshold`. This process is repeated iteratively\n    until there are no more features with a correlation coefficient higher than the threshold,\n    or when there are no features left. The main objective is to remove the most correlated\n    features first, which could help reduce multicollinearity issues and improve model performance.\n\n\n    Args:\n        input_data: DataFrame containing the input features\n        threshold: float, default=0.85. Minimum correlation threshold over which\n            features should be eliminated (0 to 1).\n        passthrough_columns: Optional list of column names to be ignored by the selector.\n        feature_table: Optional DataFrame that contains the correlation matrix\n            of input features. If this argument is provided, the correlation matrix will\n            not be calculated again.\n        median_sample_size: Optional float value to use instead of median when a feature\n            has no correlation with other features.\n\n    Returns:\n        Tuple[DataFrame, list]: A tuple containing the DataFrame with selected features\n            and the list of removed features.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', results, force=True,\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_selector([{'name':'Correlation Threshold',\n                                    'params':{ \"threshold\": 0.85 }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0']\n\n    ",
    type: "Feature Selector",
    subtype: "Unsupervised",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "8a4c1b01-240e-423c-a80d-dcbd78561fce",
    name: "Windowing Threshold Segmentation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        no_display: true,
      },
      {
        name: "column_of_interest",
        type: "str",
        streams: true,
        display_name: "Column Of Interest",
        number_of_elements: 1,
      },
      {
        name: "group_columns",
        type: "list",
        no_display: true,
        element_type: "str",
      },
      {
        name: "window_size",
        type: "int",
        c_param: 1,
        default: 200,
        description: "number of samples in the segment",
        display_name: "Window Size",
      },
      {
        name: "offset",
        type: "int",
        c_param: 2,
        default: 0,
        description: "Offset from anchor point to start of segment.",
        display_name: "Offset",
      },
      {
        name: "vt_threshold",
        type: "float",
        c_param: 3,
        default: 1000,
        description: "threshold above which a segment will be identified",
        display_name: "Vertical Threshold",
      },
      {
        name: "threshold_space_width",
        type: "int",
        c_param: 4,
        default: 25,
        description: "the size of the window to transform into threshold space",
        display_name: "Threshold Space Width",
      },
      {
        name: "comparison",
        type: "str",
        default: "maximum",
        options: [
          {
            name: "maximum",
          },
          {
            name: "minimum",
          },
        ],
        description: "the comparison between threshold space and vertical threshold (>=, <=)",
        display_name: "Comparison",
      },
      {
        name: "threshold_space",
        type: "str",
        default: "std",
        options: [
          {
            name: "std",
          },
          {
            name: "absolute sum",
          },
          {
            name: "sum",
          },
          {
            name: "variance",
          },
          {
            name: "absolute avg",
          },
        ],
        description: "space to transform signal into",
        display_name: "Threshold Space",
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      "\n    This function transfer the `input_data` and `group_column` from the previous pipeline block. This\n    is a single pass threshold segmentation algorithm which transforms a window of the data stream\n    that defined with 'threshold_space_width' into threshold space. The threshold space can be\n    computed as 'standard deviation'(std), 'sum', 'absolute sum', 'absolute average' and 'variance'.\n    The vt threshold is then compared against the calculated value with a comparison type of >=.\n    Once the threshold space is detected above the vt_threshold that becomes the anchor point.\n    The segment starts at the index of the detected point minus a user specified offset. The end\n    of the segment is immediately set to the window size.\n\n    Args:\n        column_of_interest (str): name of the stream to use for segmentation\n        window_size (int): number of samples in the window (default is 100)\n        offset (int): The offset from the anchor point and the start of the segment. for a offset of 0, the start of the window will start at the anchor point. ( default is 0)\n        vt_threshold (int): vt_threshold value which determines the segment.\n        threshold_space_width (int): Size of the threshold buffer.\n        threshold_space (str): Threshold transformation space. (std, sum, absolute sum, variance, absolute avg)\n        comparison (str): the comparison between threshold space and vertical threshold (>=, <=)\n        return_segment_index (False): Set to true to see the segment indexes for start and end.\n\n    Returns:\n        DataFrame: The segmented result will have a new column called `SegmentID` that\n        contains the segment IDs.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n\n        >>> client.pipeline.add_transform(\"Windowing Threshold Segmentation\",\n                               params={\"column_of_interest\": 'accelx',\n                                       \"window_size\": 5,\n                                       \"offset\": 0,\n                                       \"vt_threshold\": 0.05,\n                                       \"threshold_space_width\": 4,\n                                       \"threshold_space\": 'std',\n                                       \"return_segment_index\": False\n                                      })\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                      Class  Rep  SegmentID Subject  accelx  accely  accelz\n               0   Crawling    1          0     s01     377     569    4019\n               1   Crawling    1          0     s01     357     594    4051\n               2   Crawling    1          0     s01     333     638    4049\n               3   Crawling    1          0     s01     340     678    4053\n               4   Crawling    1          0     s01     372     708    4051\n               5   Crawling    1          1     s01     410     733    4028\n               6   Crawling    1          1     s01     450     733    3988\n               7   Crawling    1          1     s01     492     696    3947\n               8   Crawling    1          1     s01     518     677    3943\n               9   Crawling    1          1     s01     528     695    3988\n               10   Running    1          0     s01     -44   -3971     843\n               11   Running    1          0     s01     -47   -3982     836\n               12   Running    1          0     s01     -43   -3973     832\n               13   Running    1          0     s01     -40   -3973     834\n               14   Running    1          0     s01     -48   -3978     844\n               15   Running    1          1     s01     -52   -3993     842\n               16   Running    1          1     s01     -64   -3984     821\n               17   Running    1          1     s01     -64   -3966     813\n               18   Running    1          1     s01     -66   -3971     826\n               19   Running    1          1     s01     -62   -3988     827\n\n    ",
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "51ff1aca-343f-4285-b8ba-e372725672ff",
    name: "Scale Factor",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "mode",
        type: "str",
        c_param: 0,
        default: "scalar",
        options: [
          {
            name: "scalar",
          },
        ],
        c_param_mapping: {
          std: 0,
          median: 1,
          scalar: 2,
        },
      },
      {
        name: "scale_factor",
        type: "float",
        range: [0.1, 10],
        c_param: 1,
        default: 1,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Performs a pre-emphasis filter on the input columns and modifies the sensor streams in place.\n    This is a first-order FIR filter that performs a weighted average of each sample with the previous sample.\n\n    Args:\n        input_data (DataFrame): Input data containing the sensor streams to be filtered.\n        input_column (str): Name of the sensor stream to apply the pre-emphasis filter to.\n        group_columns (list): List of column names to group by.\n        alpha (float, optional): Pre-emphasis factor (weight given to the previous sample). Defaults to 0.97.\n        prior (int, optional): The value of the previous sample. Defaults to 0.\n\n    Returns:\n        DataFrame: Input data after having been passed through a pre-emphasis filter.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n        >>> client.pipeline.set_input_data('test_data', df, force=True)\n        >>> client.pipeline.add_transform('Scale Factor',\n                            params={'scale_factor':4096.,\n                            'input_columns':['accely']})\n        >>> results, stats = client.pipeline.execute()\n\n    ",
    type: "Transform",
    subtype: "Segment",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c1023796-6016-479e-bf8a-4289df61db59",
    name: "Offset Factor",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "offset_factor",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Adds an offset to each column in the input data. This can be used in conjunction with a scale factor to split\n    multiple channels into distinct bands of data.\n\n    Args:\n        input_data (DataFrame): The input data to transform.\n        input_columns (list): A list of column names to transform.\n        offset_factor (float, optional): The number by which input_columns are offset by. Defaults to 0.0.\n\n    Returns:\n        DataFrame: The updated input data with the transformation applied.\n    ",
    type: "Transform",
    subtype: "Segment",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c16961e9-5d48-46e6-bf79-62d926f8ca50",
    name: "Strip",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "type",
        type: "str",
        c_param: 0,
        default: "mean",
        options: [
          {
            name: "mean",
          },
          {
            name: "median",
          },
          {
            name: "min",
          },
          {
            name: "zero",
          },
        ],
        c_param_mapping: {
          min: 2,
          mean: 0,
          zero: 3,
          median: 1,
        },
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Remove each signal's mean or min from its values, while leaving specified passthrough columns unmodified.\n    This function transforms a DataFrame in such a way that the entire signal is shifted towards 'mean', 'median', 'min', or 'zero'.\n\n    Args:\n        input_data: The input DataFrame.\n        group_columns: The list of columns to group by.\n        input_columns: The list of column names to use.\n        type: Possible values are 'mean' or 'min', 'median' and 'zero'.\n         zero - zeros out the segment by subtracting the starting value of data\n         from the rest of the segment\n\n    Returns:\n        A DataFrame containing the transformed signal.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n\n        >>> client.pipeline.add_transform(\"Strip\",\n                           params={\"input_columns\": ['accelx'],\n                                   \"type\": 'min' })\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                       Class  Rep Subject  accelx  accely  accelz\n                0   Crawling    1     s01   378.0     569    4019\n                1   Crawling    1     s01   358.0     594    4051\n                2   Crawling    1     s01   334.0     638    4049\n                3   Crawling    1     s01   341.0     678    4053\n                4   Crawling    1     s01   373.0     708    4051\n                5   Crawling    1     s01   411.0     733    4028\n                6   Crawling    1     s01   451.0     733    3988\n                7   Crawling    1     s01   493.0     696    3947\n                8   Crawling    1     s01   519.0     677    3943\n                9   Crawling    1     s01   529.0     695    3988\n                10  Crawling    1     s01     0.0    2558    4609\n                11   Running    1     s01    22.0   -3971     843\n                12   Running    1     s01    19.0   -3982     836\n                13   Running    1     s01    23.0   -3973     832\n                14   Running    1     s01    26.0   -3973     834\n                15   Running    1     s01    18.0   -3978     844\n                16   Running    1     s01    14.0   -3993     842\n                17   Running    1     s01     2.0   -3984     821\n                18   Running    1     s01     2.0   -3966     813\n                19   Running    1     s01     0.0   -3971     826\n                20   Running    1     s01     4.0   -3988     827\n                21   Running    1     s01     9.0   -3984     843\n    ",
    type: "Transform",
    subtype: "Segment",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "0494165a-0c3d-4c17-a68a-710796d412b8",
    name: "Variance",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the variance of desired column(s) in the dataframe.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Variance',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n              Subject  gen_0001_accelxVariance  gen_0002_accelyVariance  gen_0003_accelzVariance\n            0     s01                      6.5                      1.7                      3.7\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "267e32e6-5a23-4103-944b-d995ca11ec34",
    name: "Two Column Min Max Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Compute the min max difference between two columns. Computes the location of the\n    min value for each of the two columns, whichever one larger, it computes the difference\n    between the two at that index.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector difference of two columns\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "2d27386e-3804-43ff-a0a6-63c710fe27ea",
    name: "Abs Max Column",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: -1,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Returns the index of the column with the max abs value for each segment.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector with index of max abs value column.\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "134bf758-0822-42b6-8e08-05a90560c143",
    name: "Interleave Signal",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Columns on which to apply the feature generator",
        num_columns: -1,
        element_type: "str",
      },
      {
        name: "cutoff",
        type: "int",
        range: [1, 32768],
        c_param: 0,
        default: 1,
        description: "The total length of the signal to use as part of the feature extractor.",
      },
      {
        name: "delta",
        type: "int",
        range: [1, 32],
        c_param: 1,
        default: 1,
        description: "Dowsample signal by selecting every delta data point.",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "math.ceil(params['cutoff']/params['delta'])*len(params['columns'])",
      },
    ],
    description:
      "\n    Turns raw signal into a feature over a range. Interleaves the signal while doing the transform\n    so the feature is stacked. Useful for feeding raw data into a CNN without additional reshaping.\n\n\n    Args:\n        input_data (DataFrame) : input data as pandas dataframe\n        columns:  list of columns on which to apply the feature generator\n        group_columns: List of column names for grouping\n        **kwargs:\n\n    Returns:\n        DataFrame: Returns data frame containing transpose range values of each specified column.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8],\n                               [0, 6, 3], [-2, 8, 7],\n                               [2, 9, 6]], columns= ['accelx', 'accely', 'accelz'])\n        >>> df\n            out:\n               accelx  accely  accelz\n            0      -3       6       5\n            1       3       7       8\n            2       0       6       3\n            3      -2       8       7\n            4       2       9       6\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force=True)\n        >>> client.pipeline.add_feature_generator([\"Interleave\"],\n                params = {\"group_columns\": [], 'range':2},                 function_defaults={\"columns\":['accelx','accely]})\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n                   accelx_range0  accely_range0 accelx_range1 accely_range1\n            0         -3             6                3             7\n    ",
    type: "Feature Generator",
    subtype: "Transpose",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "88cc3080-bd99-4291-b665-b45a14250c85",
    name: "Time Stretch",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "fraction",
        type: "float",
        range: [0.1, 5],
        default: 2,
        description: "Fraction of the input data segments that are used for this augmentation.",
        handle_by_set: false,
      },
      {
        name: "stretch_factor_range",
        type: "list",
        range: [0.9, 1.1],
        default: [0.95, 1.05],
        description: "Range of the allowed stretch factors.",
        element_type: "float",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: false,
        description:
          "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      '\n    Time Stretch:\n        Change the temporal resolution of time series. Time stretching/compression is often used to alter the tempo or speed of an audio signal without changing the pitch.\n        The resized time series is obtained by linear interpolation of the original time series.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.\n        stretch_factor_range [int, int]: Allowed factor range to resize the target signals. A signal is stretched if factor > 1  and is shrunk if factor < 1 and remains unchanged if factor = 1.\n        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of the transformed datasegments\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)\n        >>> client.upload_dataframe("toy_data.csv", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data(\'toy_data\',\n                                data_columns=[\'accelx\', \'accely\', \'accelz\'],\n                                group_columns=[\'Subject\', \'Class\', \'Rep\', \'segment_uuid\'],\n                                label_column=\'Class\')\n        >>> client.pipeline.add_transform(\'Windowing\', params={\'window_size\' : 5, \'delta\': 5})\n\n        >>> client.pipeline.add_augmentation(\n                                        [\n                                            {\n                                                "name": "Time Stretch",\n                                                "params": {\n                                                    "stretch_factor_range": [0.5, 4],\n                                                    "fraction": 1,\n                                                    "target_labels": ["Running"],\n                                                },\n                                        },\n                                        ]\n                                    )\n\n        >>> results, stats = client.pipeline.execute()\n\n        Only the size of "Running" segments are changed in the augmented segments.\n        Original segments are NOT removed from the output dataset.\n\n        >>> print(results)\n            Out:\n                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n                0      -44   -3971     843   Running    1     s01  e2a80997-346a-fff2-2de7-ffde966f3f00  398000000\n                1      -43   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-ffde966f3f00  398000000\n                2      -48   -3978     844   Running    1     s01  e2a80997-346a-fff2-2de7-ffde966f3f00  398000000\n                3      -44   -3971     843   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                4      -44   -3973     841   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                5      -45   -3976     839   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                6      -46   -3979     837   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                7      -46   -3981     835   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                8      -45   -3979     834   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                9      -44   -3976     833   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                10     -43   -3974     832   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                11     -42   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                12     -41   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                13     -41   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                14     -40   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                15     -41   -3974     836   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                16     -43   -3975     838   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                17     -45   -3976     841   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                18     -48   -3978     844   Running    1     s01  e2a80997-346a-fff2-2de7-d174664cef00  568000000\n                19     -52   -3993     842   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                20     -58   -3988     831   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                21     -64   -3984     821   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                22     -64   -3975     817   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                23     -64   -3966     813   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                24     -65   -3968     819   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                25     -66   -3971     826   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                26     -64   -3979     826   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                27     -62   -3988     827   Running    1     s01  e2a80997-346a-fff2-2de7-caab434dbf00  828000001\n                28     -44   -3971     843   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                29     -45   -3975     840   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                30     -46   -3979     837   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                31     -46   -3981     835   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                32     -45   -3977     834   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                33     -43   -3974     832   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                34     -42   -3973     832   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                35     -41   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                36     -40   -3973     833   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                37     -42   -3974     836   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                38     -45   -3976     840   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                39     -48   -3978     844   Running    1     s01  e2a80997-346a-fff2-2de7-09e48e2d8f00  704000000\n                40     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                41     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                42     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                43     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                44     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                45     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                46     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                47     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                48     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                49     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                50     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                51     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                52     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                53     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                54     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                55     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                56     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                57     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                58     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                59     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n\n    ',
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "a6235848-cf8e-4cfc-867d-757d65910ad4",
    name: "Random Crop",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "overlap_factor",
        type: "float",
        range: [-1, 1],
        default: 0,
        description:
          "The overlapping degree of the cropped segments. Use any values larger than -1. Use 0 for no overlaps, 1 for 100% overlaps and so on.",
        handle_by_set: false,
      },
      {
        name: "crop_size",
        type: "int",
        default: 100,
        description: "Lengths of the cropped segments.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      "\n    Random Crop:\n        Randomly cropping a set of long input segments. A set of output segments of the same size are generated.\n        The starting point of each segment is drawn randomly. The odds of larger segments to contribute to the output set are proportional to their size.\n        If N samples exist in all input segments, in total, the number of output cropped segments is n = N * (1.0 + overlap_factor) / crop_size, where\n        overlap_factor is a real number larger than -1 indicating how tightly the output segments are distribute. Crop_size is the size of the segments in the output set.\n\n        If the UUID of the input segment has the augmented format, the UUID of the output segment would have the augmented format as well.\n        If the input segment is an original segment, the UUID of the output segment follows the UUID of a semi-original segment.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        overlap_factor [float, float]: Allowed overlapping factor range to determined the number of randomly generated cropped signals. The minimum overlap factor is -1 that implied only one cropped output segment. For not having overlapping segments use negative values. Any value larger than 1 causes generating segments that randomly overlap each other.\n        crop_size (int): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of cropped segments.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df[\"segment_uuid\"] = df.apply(lambda row: \"07baf4b8-21b9-4b98-8927-de1264bb2a92\" if row.Class==\"Crawling\" else \"e2a80997-346a-4327-8fa4-2de7de65ac99\", axis=1)\n        >>> client.upload_dataframe(\"toy_data.csv\", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('toy_data',\n                                data_columns=['accelx', 'accely', 'accelz'],\n                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],\n                                label_column='Class')\n        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})\n        >>> client.pipeline.add_augmentation(\n                                        [\n                                            {\n                                                \"name\": \"Random Crop\",\n                                                \"params\": {\n                                                    \"crop_size\": 4,\n                                                    \"overlap_factor\": 1,\n                                                    \"target_labels\": [\"Crawling\"],\n                                                },\n                                            },\n                                        ], overwrite=False,\n                                    )\n        >>> results, stats = client.pipeline.execute()\n        >>> print(results)\n            Out:\n                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n                0      357     594    4051  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000\n                1      333     638    4049  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000\n                2      340     678    4053  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000\n                3      372     708    4051  Crawling    1     s01  07baf4b8-dfaa-eee4-9299-be17a3ab3fee  930000000\n                4      410     733    4028  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001\n                5      450     733    3988  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001\n                6      492     696    3947  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001\n                7      518     677    3943  Crawling    1     s01  07baf4b8-70ad-eee4-a771-21bef3c039ee  645000001\n                8      450     733    3988  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001\n                9      492     696    3947  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001\n                10     518     677    3943  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001\n                11     528     695    3988  Crawling    1     s01  07baf4b8-4634-eee4-8875-e6de6934deee  256000001\n                12     410     733    4028  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001\n                13     450     733    3988  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001\n                14     492     696    3947  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001\n                15     518     677    3943  Crawling    1     s01  07baf4b8-866f-eee4-b98e-a89937185fee  380000001\n                16     357     594    4051  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000\n                17     333     638    4049  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000\n                18     340     678    4053  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000\n                19     372     708    4051  Crawling    1     s01  07baf4b8-9d7c-eee4-8b8b-bc0aae9551ee  112000000\n                20     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                21     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                22     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                23     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                24     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                25     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                26     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                27     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                28     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                29     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n\n    ",
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c4b41b9f-5342-4dfc-9509-adc9c354b72c",
    name: "Resize Segment",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "new_size",
        type: "int",
        default: 10,
        description: "Desired size of the segment.",
        handle_by_set: false,
      },
      {
        name: "padding_value",
        type: "int",
        default: 0,
        description:
          "The value used to pad signals when resizing. This parameter is only effective when the input 'averaging_window_size' is not positive.",
        handle_by_set: false,
      },
      {
        name: "averaging_window_size",
        type: "int",
        default: 0,
        description:
          "The window size on the opposite side segment, within which the signal average is calculated and used for padding. 'padding_value' is used if the provided window size is not positive.",
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: true,
        description: "Replacing segment with the resized versions.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      "\n    Resize Segment:\n        Resizing segments. Segment is padded with the average within a window or with the input padding value.\n\n        If the UUID of the input segment has the augmented format, the UUID of the output segment would have the augmented format as well.\n        If the input segment is an original segment, the UUID of the output segment follows the UUID of a semi-original segment.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        new_size (int): The output segment size.\n        averaging_window_size (int): The window size on the opposite side segment, within which the signal average is calculated and used for padding. 'padding_value' is used if the provided window size is not positive.\n        padding_value (int): The value used to pad signals when resizing. This parameter is only effective when the input 'averaging_window_size' is not positive.\n        replace (boolean): Replacing segment with the resized versions.\n\n    Returns:\n        DataSegment: A list of randomly shifted segments.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df[\"segment_uuid\"] = df.apply(lambda row: \"07baf4b8-21b9-4b98-8927-de1264bb2a92\" if row.Class==\"Crawling\" else \"e2a80997-346a-4327-8fa4-2de7de65ac99\", axis=1)\n        >>> client.upload_dataframe(\"toy_data.csv\", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('toy_data',\n                                data_columns=['accelx', 'accely', 'accelz'],\n                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],\n                                label_column='Class')\n        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})\n        >>> client.pipeline.add_augmentation(\n                                        [\n                                            {\n                                                \"name\": \"Resize Segment\",\n                                                \"params\": {\n                                                    \"new_size\": 10,\n                                                    \"padding_value\": 9999,\n                                                },\n                                            },\n                                        ], overwrite=False,\n                                    )\n        >>> results, stats = client.pipeline.execute()\n        >>> print(results)\n        >>> # padded with 9999 on both end, original segments are replaced by the resize semi-original segments\n            Out:\n                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n                0     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                1      -52   -3993     842   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                2      -64   -3984     821   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                3      -64   -3966     813   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                4      -66   -3971     826   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                5      -62   -3988     827   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                6     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                7     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                8     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                9     9999    9999    9999   Running    1     s01  e2a80997-edd6-eee7-9874-5d9db06203ee  309000001\n                10    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                11     377     569    4019  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                12     357     594    4051  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                13     333     638    4049  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                14     340     678    4053  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                15     372     708    4051  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                16    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                17    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                18    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                19    9999    9999    9999  Crawling    1     s01  07baf4b8-49ac-eee7-87b2-431acc9471ee  702000000\n                20    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                21     410     733    4028  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                22     450     733    3988  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                23     492     696    3947  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                24     518     677    3943  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                25     528     695    3988  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                26    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                27    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                28    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                29    9999    9999    9999  Crawling    1     s01  07baf4b8-7f2a-eee7-b2a9-9e12e89a3cee  964000001\n                30     -44   -3971     843   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                31     -47   -3982     836   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                32     -43   -3973     832   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                33     -40   -3973     834   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                34     -48   -3978     844   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                35    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                36    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                37    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                38    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n                39    9999    9999    9999   Running    1     s01  e2a80997-f8e0-eee7-90e4-453ecce4fbee  764000000\n\n    ",
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4f2f95e9-e7e5-4cc9-9272-03721b529e75",
    name: "Mean",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the arithmetic mean of each column in `columns` in the dataframe.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Mean',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxMean  gen_0002_accelyMean  gen_0003_accelzMean\n            0     s01                  0.0                  7.2                  5.8\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "937e22e8-2449-4fcd-9255-34704bb6cfd5",
    name: "Kurtosis",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Kurtosis is the degree of 'peakedness' or 'tailedness' in the distribution and\n    is related to the shape. A high Kurtosis portrays a chart with fat tail and\n    peaky distribution, whereas a low Kurtosis corresponds to the skinny tails and\n    the distribution is concentrated towards the mean. Kurtosis is calculated using Fisher's method.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Kurtosis',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxKurtosis  gen_0002_accelyKurtosis  gen_0003_accelzKurtosis\n            0     s01                -1.565089                -1.371972                -1.005478\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "92ea6874-b8e7-4424-a23e-c30b3168ed78",
    name: "Sigma Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the rate at which standard deviation value (sigma) is crossed for\n    each specified column. The total number of sigma crossings are found and then\n    the number is divided by total number of samples to get the `sigma_crossing_rate`.\n\n    Args:\n        columns: The `columns` represents a list of all column names on which\n                 `sigma_crossing_rate` is to be found.\n\n    Returns:\n        DataFrame : Return the sigma crossing rate.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Sigma Crossing Rate',\n                                     'params':{\"columns\": ['accelx','accely', 'accelz']}\n                                    }])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0001_accelxSigmaCrossingRate  gen_0002_accelySigmaCrossingRate  gen_0003_accelzSigmaCrossingRate\n            0  Crawling    1     s01                          0.090909                               0.0                               0.0\n            1   Running    1     s01                          0.000000                               0.0                               0.0\n\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "66ffffcc-106a-47a1-a4c6-96f85afaa21a",
    name: "Threshold With Offset Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Threshold to check for crossing rate over",
      },
      {
        name: "offset",
        type: "int",
        range: [-32768, 32767],
        c_param: 1,
        default: 0,
        description: "Offset must fall under before new crossing can be detected",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the rate at which each specified column crosses a given threshold with a specified offset.\n    The total number of threshold crossings are found,\n    and then the number is divided by the total number of samples to get the `threshold_crossing_rate`.\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (list of strings): A list of all column names on which `threshold_crossing_rate` is to be found.\n        threshold (int, optional): The threshold value. Defaults to 0.\n        offset (int, optional): The offset value. Defaults to 0.\n\n    Returns:\n        DataFrame : Return the number of threshold crossings divided by the length of the signal.\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "975e49e0-96d0-41bf-bd65-99f401646e2e",
    name: "Streaming Downsample",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "input_columns",
        type: "list",
      },
      {
        name: "filter_length",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 1,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Downsample the entire dataframe into a dataframe of size `filter_length` by taking the average over the samples within the filter length.\n\n    Args:\n        input_data: dataframe\n        group_columns (a list): List of columns on which grouping is to be done.\n                             Each group will go through downsampling one at a time\n        input_columns: List of columns to be downsampled\n        filter_length: Number of samples in each new filter length\n\n    Returns:\n        DataFrame: The downsampled dataframe.\n\n    ",
    type: "Transform",
    subtype: "Sensor Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "3c9efb7e-5f54-4f9d-adf1-439e708c7f1c",
    name: "Recursive Feature Elimination",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "method",
        type: "str",
        default: "Log R",
        options: [
          {
            name: "Log R",
          },
          {
            name: "Linear SVC",
          },
        ],
        description: "Selection method",
      },
      {
        name: "number_of_features",
        type: "int",
        default: 10,
        description: "The number of     features you would like the selector to reduce to",
        handle_by_set: false,
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "The set of columns the selector should ignore",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This is a supervised method of feature selection. The goal of recursive feature elimination (RFE) is to select\n    features by recursively considering smaller and smaller sets of features. First, the estimator (`method`: 'Log R'\n    or 'Linear SVC') is trained on the initial set of features and weights are assigned to each one of them. Then,\n    features whose absolute weights are the smallest are pruned from the current set of features. That procedure is\n    recursively repeated on the pruned set until the desired number of features `number_of_features` to select is\n    eventually reached.\n\n    Args:\n        input_data (DataFrame): Input data to perform feature selection on.\n        label_column (str): Name of the column containing the labels.\n        method (str): The type of selection method. Two options available: 1) `Log R` and 2) `Linear SVC`. For\n            `Log R`, the value of Inverse of regularization strength `C` is default to 1.0 and `penalty` is\n            defaulted to `l1`. For `Linear SVC`, the default for `C` is 0.01, `penalty` is `l1` and `dual` is\n            set to `False`.\n        number_of_features (int): The number of features you would like the selector to reduce to.\n        passthrough_columns (list): [Optional] A list of columns to include in the output DataFrame in addition to\n            the selected features.\n\n    Returns:\n        tuple: A tuple containing:\n            - DataFrame: A DataFrame that includes the selected features and the passthrough columns.\n            - list: A list of unselected features.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', results, force=True,\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_selector([{'name':'Recursive Feature Elimination',\n                                    'params':{\"method\": \"Log R\",\n                                              \"number_of_features\": 3}}],\n                                  params={'number_of_features':3})\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            Out:\n                  Class Subject  gen_0001_accelx_2  gen_0003_accelz_1  gen_0003_accelz_4\n            0  Crawling     s01         208.341858        3881.038330        3900.734863\n            1  Crawling     s02          91.971481        3821.513428        3896.376221\n            2  Crawling     s03         200.263031        3896.349121        3889.297119\n            3   Running     s01         -16.322056         641.164185         605.192993\n            4   Running     s02         431.893585         870.608459         846.671204\n            5   Running     s03         360.777466         263.184052         234.177200\n            6   Walking     s01           0.492386         559.139587         558.538086\n            7   Walking     s02         374.443237         658.902710         669.394592\n            8   Walking     s03         283.627502         -87.612816         -98.735649\n\n    Notes:\n        For more information on defaults of `Log R`, please see: http://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression\n        For `Linear SVC`, please see: http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html#sklearn.svm.LinearSVC\n\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "3d63ae90-b90c-490b-9f51-7f19ff74309e",
    name: "Pitch Shift",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "input_columns",
        type: "list",
        default: [],
        description: "List of sensors that are transformed by this augmentation.",
        handle_by_set: false,
      },
      {
        name: "sample_rate",
        type: "int",
        default: 16000,
        description: "Number of recorded samples per second.",
        handle_by_set: false,
      },
      {
        name: "fraction",
        type: "float",
        range: [0.1, 5],
        default: 2,
        description: "Fraction of the input data segments that are used for this augmentation.",
        handle_by_set: false,
      },
      {
        name: "step_per_octave",
        type: "float",
        range: [8, 256],
        default: 128,
        description: "Number of steps per octave.",
        handle_by_set: false,
      },
      {
        name: "shift_range",
        type: "list",
        range: [-64, 64],
        default: [-4, 4],
        description: "Range of the allowed number of (fractional) steps to shift",
        element_type: "float",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: false,
        description:
          "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      "\n    Pitch Shift:\n        Pitch shifting is used to change the pitch of an audio signal without changing its tempo or speed.\n        Shift the pitch of a waveform by ``n_steps`` steps.\n\n        UUID format:\n            Original Segment: yyyyyyyy-yyyy-xxxx-xxxx-xxxxxxxxxxxx\n            Augmented Segments: yyyyyyyy-yyyy-fffc-xxxx-xxxxxxxnnf01\n            Semi-original Segments: yyyyyyyy-xxxx-eee4-xxxx-xxxxxxxxxxee\n\n            'y' is the wildcard carried over from the original signal UUIDs.\n            'f' and 'e' are reserved codes for augmented or semi-original (cropped original) segments.\n            'c' is the numeric code of the last augmentation transformation.\n            For the augmented segments, 'nn' is replaced with the checksum control digits.\n            The first 8 digits of UUIDs (yyyyyyyy) are used to find and match the segments of the same origin.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        input_columns [str]: List of sensors that are transformed by this augmentation.\n        sample_rate (int): Number of recorded samples per second.\n        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.\n        step_per_octave (int): Number of steps per octave.\n        shift_range [float, float]: Range of the allowed number of (fractional) steps to shift.\n        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of the datasegments with added background noise.\n\n\n    ",
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "94c609da-c439-433f-9bf4-44589992fa7a",
    name: "Moving Average Sensor Transform",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "input_columns",
        type: "list",
      },
      {
        name: "filter_order",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 1,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Performs a symmetric moving average filter on the input column,\n    creates a new column with the filtered data.\n\n    Args:\n        input_data: DataFrame containing the time series data.\n        group_columns: columns to group data by before processing.\n        input_column: sensor stream to apply moving average filter on.\n        filter order: the number of samples to average to the left and right.\n\n    Returns:\n        input data after having been passed through symmetric moving average filter\n    ",
    type: "Transform",
    subtype: "Sensor Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "aed157ed-61e9-4e1d-8b44-389c05b09585",
    name: "Streaming Downsample by Decimation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "input_columns",
        type: "list",
      },
      {
        name: "filter_length",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 1,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Decrease the sample rate by a factor of filter_length, this will only keep one samples for every length of the filter.\n\n    Args:\n        input_data: dataframe\n        columns: List of columns to be downsampled\n        group_columns (a list): List of columns on which grouping is to be done.\n                             Each group will go through downsampling one at a time\n        filter_length: integer; Number of samples in each new filter length\n\n    Returns:\n        DataFrame: The downsampled dataframe.\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6], [3, 1],\n                            [3, 1], [4, 3], [5, 5], [4, 7], [3, 6]],\n                            columns=['accelx', 'accely'])\n        >>> df\n        Out:\n               accelx  accely\n            0       3       3\n            1       4       5\n            2       5       7\n            3       4       6\n            4       3       1\n            5       3       1\n            6       4       3\n            7       5       5\n            8       4       7\n            9       3       6\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force = True)\n        >>> client.pipeline.add_transform('Streaming Downsample by Decimation', params={'group_columns':[],                                                            'columns' : ['accelx', 'accely'],                                                            'filter_length' : 5 })\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            Out:\n                    accelx  accely\n                0     3       3\n                1     3       1\n                2     3       6\n    ",
    type: "Transform",
    subtype: "Sensor Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "0b6aaf26-21cf-4626-b64f-50d6412cc843",
    name: "Absolute Area of Spectrum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Absolute area of spectrum.\n\n    Args:\n        sample_rate: Sampling rate of the signal\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n\n        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area of Spectrum',\n                                     'params':{\"sample_rate\": 10,\n                                               \"columns\": ['accelx','accely','accelz']\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxAbsAreaSpec  gen_0002_accelyAbsAreaSpec  gen_0003_accelzAbsAreaSpec\n            0     s01                       260.0                      2660.0                      1830.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b01a6361-d1e3-4204-95bc-628fdd669bc5",
    name: "Scale Amplitude",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "input_columns",
        type: "list",
        default: [],
        description: "List of sensors that are transformed by this augmentation.",
        handle_by_set: false,
      },
      {
        name: "fraction",
        type: "float",
        range: [0.1, 5],
        default: 2,
        description: "Fraction of the input data segments that are used for this augmentation.",
        handle_by_set: false,
      },
      {
        name: "scale_range",
        type: "list",
        range: [0.01, 10],
        default: [0.1, 2],
        description: "Range of the allowed factors to scale the target sensors.",
        element_type: "float",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: false,
        description:
          "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      '\n    Scale Amplitude:\n        Scaling the target sensor values.\n        All targeted sensors of the selected segment are scaled according to a scale factor randomly chosen from the provided scale range.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        input_columns [str]: List of sensors that are transformed by this augmentation.\n        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.\n        scale_range [int, int]: Allowed factor range to scale the target signals.\n        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of the transformed datasegments.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)\n        >>> client.upload_dataframe("toy_data.csv", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data(\'toy_data\',\n                                data_columns=[\'accelx\', \'accely\', \'accelz\'],\n                                group_columns=[\'Subject\', \'Class\', \'Rep\', \'segment_uuid\'],\n                                label_column=\'Class\')\n        >>> client.pipeline.add_transform(\'Windowing\', params={\'window_size\' : 5, \'delta\': 5})\n\n        >>> client.pipeline.add_augmentation(\n                                        [\n                                            {\n                                                "name": "Scale Amplitude",\n                                                "params": {\n                                                    "scale_range": [2, 2],\n                                                    "fraction": 1,\n                                                    "target_labels": ["Running"],\n                                                    "input_columns": ["accelx", "accely"],\n                                                },\n                                        },\n                                        ]\n                                    )\n\n        >>> results, stats = client.pipeline.execute()\n\n        Only "Running" segments are augmented by scaling "accelx", and "accely" columns.\n        Original segments are NOT removed from the output dataset.\n\n        >>> print(results)\n            Out:\n                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n                0      -88   -7942     843   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000\n                1      -94   -7964     836   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000\n                2      -86   -7946     832   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000\n                3      -80   -7946     834   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000\n                4      -96   -7956     844   Running    1     s01  e2a80997-346a-fff1-2de7-ea7cba3e7f00  838000000\n                5     -104   -7986     842   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001\n                6     -128   -7968     821   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001\n                7     -128   -7932     813   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001\n                8     -132   -7942     826   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001\n                9     -124   -7976     827   Running    1     s01  e2a80997-346a-fff1-2de7-20c56c6cff00  138000001\n                10     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                11     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                12     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                13     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                14     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                15     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                16     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                17     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                18     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                19     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                20     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                21     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                22     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                23     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                24     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                25     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                26     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                27     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                28     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                29     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n\n    ',
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "9d0aa12f-ffee-4937-89f6-efe581254fa0",
    name: "Two Column Mean Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Compute the mean difference between two columns.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector mean difference\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e78929d5-24da-4719-8950-09aec5a83eb5",
    name: "Two Column Peak To Peak Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Compute the max value for each column, then subtract the first column for the second.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector mean difference\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "27b5f5e7-40f2-4fa9-99e2-3de2e91b5f55",
    name: "Resampling by Majority Vote",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
      },
      {
        name: "metadata_name",
        type: "str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    For each group, perform max pooling on the specified metadata_name column\n    and set the value of that metadata column to the maximum occurring value.\n\n    Args:\n        input_data (DataFrame): Input DataFrame.\n        group_columns (list): Columns to group over.\n        metadata_name (str): Name of the metadata column to use for sampling.\n\n    Returns:\n        DataFrame: The modified input_data DataFrame with metadata_name column being modified by max pooling.\n    ",
    type: "Sampler",
    subtype: "Feature Grouping",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "3a3646cc-cd51-499c-a580-7cfcb540ff5b",
    name: "PME",
    input_contract: [
      {
        name: "distance_mode",
        type: "str",
        default: "L1",
        options: [
          {
            name: "L1",
          },
          {
            name: "Lsup",
          },
          {
            name: "DTW",
          },
        ],
      },
      {
        name: "classification_mode",
        type: "str",
        default: "KNN",
        options: [
          {
            name: "RBF",
          },
          {
            name: "KNN",
          },
        ],
        description:
          "Set the classifier recognition mode. KNN mode will always return a result corresponding to the nearest neuron that fires. RBF will only return results that are within the influence field. If the feature vector does not fall within any of the influence fiels RBF will return Unknown or 0.",
      },
      {
        name: "max_aif",
        type: "int",
        range: [1, 16384],
        default: 400,
        description:
          "The maximum size of the influence field for a pattern in the database. The influence field determines the distance from the center that it will activate.",
      },
      {
        name: "min_aif",
        type: "int",
        range: [1, 16383],
        default: 25,
        description:
          "The minimum size of the influence field for a pattern in the database. Patterns will not be created with an influence field smaller than this number.",
      },
      {
        name: "num_channels",
        type: "int",
        range: [1, 12],
        default: 1,
        description:
          "the number of channels that are specified for calculations when DTW is used as the distance metric (default: 1)",
      },
      {
        name: "reserved_patterns",
        type: "int",
        range: [0, 1000],
        default: 0,
        description:
          "The number of patterns to reserve in the database in addition to the predefined patterns during training",
      },
      {
        name: "reinforcement_learning",
        type: "bool",
        default: false,
      },
    ],
    output_contract: null,
    description:
      "\n    PME or pattern matching engine is a distance based classifier that is optimized for high performance\n    on resource constrained devices. It computes the distances between an input vector and a database\n    of stored patterns and returns a prediction based on the classification classifier settings.\n\n    There are three distance metrics that can be computed L1, LSUP and DTW(Dynamic Time Warping).\n\n    The are two classification criteria, RBF and KNN. For RBF every pattern in the database is given an influence\n    field that the distance between it and the input vector must be less than in order to pattern to fire.\n    KNN returns the category of pattern with the smallest computed distance bewteen it and the input vector.\n\n    Args:\n        distance_mode (str): L1, Lsup or DTW\n        classification_mode (str):  RBF or KNN\n        max_aif (int): the maximum value of the influence field\n        min_aif (int): the minimum value of the influence field\n        reserved_patterns (int): The number of patterns to reserve in the database in addition to the\n         predefined patterns during training\n        online_learning  (bool): To generate the code for online learning on the edge device\n         this takes up additional SRAM, but can be used to tune the model at the edge.\n        num_channels (int): the number of channels that are specified for calculations when DTW is used as\n         the distance metric (default: 1).\n\n    ",
    type: "Classifier",
    subtype: "Clustering",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "d1b6b0c9-c935-42fb-8349-1737192f9c64",
    name: "TF Micro",
    input_contract: [],
    output_contract: [],
    description:
      "\n    The Tensorflow Micro Classifier uses Tensorflow Lite for Microcontrollers, an inference engine\n    from Google optimized run machine learning models on embedded devices.\n\n    Tensorflow Lite for Microcontrollers supports a subset of all Tensorflow functions. For a full\n    list see `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.\n\n    For additional documentation on Tensorflow Lite for Microcontrollers see `here <https://www.tensorflow.org/lite/microcontrollers>`_.\n    ",
    type: "Classifier",
    subtype: "NN",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "db4dcc87-5446-4353-8a9b-1ab178b0e9f1",
    name: "TensorFlow Lite for Microcontrollers",
    input_contract: [],
    output_contract: [],
    description:
      "\n    The Tensorflow Micro Classifier uses Tensorflow Lite for Microcontrollers, an inference engine\n    from Google optimized run machine learning models on embedded devices.\n\n    Tensorflow Lite for Microcontrollers supports a subset of all Tensorflow functions. For a full\n    list see `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.\n\n    For additional documentation on Tensorflow Lite for Microcontrollers see `here <https://www.tensorflow.org/lite/microcontrollers>`_.\n    ",
    type: "Classifier",
    subtype: "NN",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "3c1fadcb-7e6a-4765-8672-5810da8976a3",
    name: "Downsample Average with Normalization",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "new_length",
        type: "int",
        range: [5, 32],
        c_param: 0,
        default: 12,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: true,
        output_formula: "params['new_length']",
        scratch_buffer: {
          name: "new_length",
          type: "parameter",
        },
      },
    ],
    description:
      "\n    This function takes `input_data` dataframe as input and group by `group_columns`.\n    Then for each group, it drops the `passthrough_columns` and performs a convolution\n    on the remaining columns.\n\n    On each column, perform the following steps:\n\n    - Divide the entire column into windows of size total length/`new_length`.\n    - Calculate mean for each window\n    - Concatenate all the mean values into a feature vector of length new_length\n    - Normalize the signal to be between 0-255\n\n    Then all such means are concatenated to get `new_length` * # of columns. These constitute\n    features in downstream analyses. For instance, if there are three columns and the\n    `new_length` value is 12, then total number of means we get is 12 * 3 = 36. Each will represent a feature.\n\n    Args:\n        input_data (DataFrame): Input data to transform\n        columns: List of columns\n        group_columns (a list): List of columns on which grouping is to be done.\n                                 Each group will go through downsampling one at a time\n        new_length (int): Dopwnsample Length length\n\n    Returns:\n        DataFrame: Downsampled Features Normalized\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6],\n                            [3, 1], [3, 1], [4, 3], [5, 5],\n                            [4, 7], [3, 6]], columns=['accelx', 'accely'])\n        >>> df\n        Out:\n           accelx  accely\n        0       3       3\n        1       4       5\n        2       5       7\n        3       4       6\n        4       3       1\n        5       3       1\n        6       4       3\n        7       5       5\n        8       4       7\n        9       3       6\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force=True)\n        >>> client.pipeline.add_feature_generator([\"Downsample Average with Normalization\"],\n                 params = {\"group_columns\": []},\n                           function_defaults={\"columns\":['accelx', 'accely'],\n                                             'new_length' : 5})\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            Out:\n                   accelx_1  accelx_2  accelx_3  accelx_4  accelx_5  accely_1  accely_2\n                0       3.5       4.5         3       4.5       3.5         4       6.5\n                   accely_3  accely_4  accely_5\n                0         1         4       6.5\n    ",
    type: "Feature Generator",
    subtype: "Sampling",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "79c588bb-33e9-496b-a539-dc3c994a2216",
    name: "Sample Features by Metadata",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "metadata_name",
        type: "str",
      },
      {
        name: "metadata_values",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Select rows from the input DataFrame based on a metadata column. Rows\n    that have a metadata value that is in the values list will be returned.\n\n    Args:\n        input_data (DataFrame): Input DataFrame.\n        metadata_name (str): Name of the metadata column to use for sampling.\n        metadata_values (list[str]): List of values of the named column for which to\n            select rows of the input data.\n\n    Returns:\n        DataFrame: The input_data DataFrame containing only the rows for which the metadata value is\n        in the accepted list.\n    ",
    type: "Sampler",
    subtype: "Feature Grouping",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "166cd33f-ad83-4c76-b78b-724f4460e2d9",
    name: "One Class SVM filtering",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "filtering_label",
        type: "list",
        default: [],
        description: "List of classes.",
        display_name: "Filtering Label",
      },
      {
        name: "feature_columns",
        type: "list",
        default: [],
        description: "List of features.",
        display_name: "Feature Columns",
      },
      {
        name: "outliers_fraction",
        type: "float",
        range: [0.01, 1],
        default: 0.05,
        description: "Define the ratio of outliers.",
        display_name: "Outliers Fraction",
      },
      {
        name: "kernel",
        type: "str",
        default: "rbf",
        description:
          "Specifies the kernel type to be used in the algorithm. It must be one of 'linear', 'poly', 'rbf', 'sigmoid'.",
        display_name: "Kernel",
      },
      {
        name: "assign_unknown",
        type: "bool",
        default: false,
        description: "Assign unknown label to outliers.",
        display_name: "Assign Unknown",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Unsupervised Outlier Detection. Estimate the support of a high-dimensional distribution. The implementation is based on libsvm.\n\n    Args:\n        input_data: Dataframe, feature set that is results of generator_set or feature_selector\n        label_column (str): Label column name.\n        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.\n        feature_columns: List<String>, List of features. if it is not defined, it uses all features.\n        outliers_fraction (float) : Define the ratio of outliers.\n        kernel (str) : Specifies the kernel type to be used in the algorithm. It must be one of 'linear', 'poly', 'rbf', 'sigmoid'.\n        assign_unknown (bool): Assign unknown label to outliers.\n\n    Returns:\n        DataFrame containing features without outliers and noise.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices before the filtering algorithm\n        >>> results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5, 6, 7, 8]\n\n        >>> client.pipeline.add_transform(\"One Class SVM filtering\",\n                           params={\"outliers_fraction\": 0.05})\n\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices after the filtering algorithm\n        >>>results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5]\n\n    ",
    type: "Sampler",
    subtype: "Outlier Filter",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "c1706d2a-b854-4eec-a33b-8394b962114d",
    name: "RBF with Neuron Allocation Limit",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "remove_unknown",
        type: "boolean",
        default: false,
        description:
          "If there is an Unknown label, remove that from the database of patterns prior to saving the model.",
      },
      {
        name: "chunk_size",
        type: "int",
        range: [1, 1000],
        default: 20,
        handle_by_set: false,
      },
      {
        name: "inverse_relearn_frequency",
        type: "int",
        range: [1, 1000],
        default: 5,
        handle_by_set: false,
      },
      {
        name: "max_neurons",
        type: "int",
        range: [1, 16384],
        default: 64,
        handle_by_set: false,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "PME",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "aggressive_neuron_creation",
        type: "bool",
        default: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [],
    description:
      "\n    The Train and Prune algorithm takes as input feature vectors, corresponding class\n    labels, and maximum desired number of neurons, and outputs a model.\n\n    The training vectors are partitioned into subsets (chunks) and presented to the PME\n    classifier which places neurons and determines areas of influence (AIFs). After each\n    subset is learned, the neurons that fired the most on the validation set are retained\n    and the others are removed (pruned) from the model. After a defined number of train and\n    prune cycles, the complete retained set of neurons is then re-learned, which results in\n    larger neuron AIFs. Train/prune/re-learn cycles continue to run on all of the remaining\n    chunks, keeping the total number of neurons within the limit while giving preference to\n    neurons that fire frequently.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        chunk_size (int): the number of training vectors in each chunk\n        inverse_relearn_frequency (int): the number of chunks to train and prune between\n         each re-learn phase\n        max_neurons (int): the maximum allowed number of neurons\n        aggressive_neuron_creation (bool): flag for placing neurons even if they are within\n         the influence field of another neuron of the same category (default is False)\n\n    Returns:\n        a model\n\n    ",
    type: "Training Algorithm",
    subtype: "PME",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "19a14ce0-d182-4c6c-acaf-62a89ca6805b",
    name: "Total Area of High Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 50],
        c_param: 1,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Total area of high frequency components of the signal. It calculates total\n    area by applying a moving average filter on the signal with a smoothing factor\n    and subtracting the filtered signal from the original.\n\n    Args:\n        sample_rate: float; Sampling rate of the signal\n        smoothing_factor (int): Determines the amount of attenuation for frequencies\n                         over the cutoff frequency.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Total Area of High Frequency',\n                                     'params':{\"sample_rate\": 10,\n                                               \"smoothing_factor\": 5,\n                                               \"columns\": ['accelx','accely','accelz']\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxTotAreaAc  gen_0002_accelyTotAreaAc  gen_0003_accelzTotAreaAc\n            0     s01                       0.0                      0.12                      0.28\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "dec45628-cdc3-4be3-abab-67b08d78da76",
    name: "Absolute Area of High Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 50],
        c_param: 1,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Absolute area of high frequency components of the signal. It calculates absolute\n    area by applying a moving average filter on the signal with a smoothing factor\n    and subtracting the filtered signal from the original.\n\n\n    Args:\n        sample_rate: float; Sampling rate of the signal\n        smoothing_factor (int): Determines the amount of attenuation for frequencies\n                         over the cutoff frequency.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area of High Frequency',\n                                     'params':{\"sample_rate\": 10,\n                                               \"smoothing_factor\": 5,\n                                               \"columns\": ['accelx','accely','accelz']\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxAbsAreaAc  gen_0002_accelyAbsAreaAc  gen_0003_accelzAbsAreaAc\n            0     s01                 76.879997                800.099976                470.160004\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "5f8cf01a-a3b9-4fda-844f-4a40f557bd79",
    name: "Adaptive Windowing Segmentation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        no_display: true,
      },
      {
        name: "columns_of_interest",
        type: "list",
        streams: true,
        display_name: "Columns Of Interest",
        number_of_elements: -1,
      },
      {
        name: "group_columns",
        type: "list",
        no_display: true,
        element_type: "str",
      },
      {
        name: "max_segment_length",
        type: "int16_t",
        c_param: 1,
        default: 256,
        description: "Max segment to search over",
        display_name: "Max Segment Size",
      },
      {
        name: "min_segment_length",
        type: "int16_t",
        c_param: 2,
        default: 100,
        description: "Size of window to search over",
        display_name: "Min Segment Length",
      },
      {
        name: "threshold",
        type: "int16_t",
        c_param: 3,
        default: 50,
        description: "Threshold above which value must be to consider it a maxx value",
        display_name: "Threshold",
      },
      {
        name: "absolute_value",
        type: "boolean",
        c_param: 4,
        default: true,
        description: "Take the absolute value of the sensor data before doing the comparison",
        display_name: "Absolute Value",
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
        description: "Append columns start and stop of the segment index.",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      "\n    A sliding windowing technique with adaptive sizing. This will find the largest point after\n    min_segment_length that is above the threshold. That point will be considered the end of\n    the segment. If no points are above the threshold before reaching max segment length, then\n    the segment will stop at max_segment_length\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns_of_interest (str): The stream to use for segmentation.\n        group_columns ([str]): A list of column names to use for grouping.\n        max_segment_length (int): This is the maximum number of samples a\n         segment can contain.\n        min_segment_length (int) This is the minimum number of samples a\n         segment can contain.\n        threshold (int): The threshold must be met to start looking for the\n         end of the segment early. If the threshold is not met, the segment\n         ends at the max_segment_length\n        absolute_value (bool): Takes the absolute value of the sensor data prior\n         do doing the comparison\n        return_segment_index (False): Set to true to see the segment indexes\n         for start and end.\n    ",
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "15c901ef-2743-4a96-8ef6-eaa8c8117d98",
    name: "Cascade Windowing",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "window_size",
        type: "int",
        c_param: 1,
        default: 250,
      },
      {
        name: "delta",
        type: "int",
        c_param: 2,
        default: 250,
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
        description: "Append columns start and stop of the segment index.",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      "\n    This function transfer the `input_data` and `group_column` from the previous pipeline block.\n    It groups 'input_data' by using group_column. It divides each group into windows of size `window_size`.\n    The argument `delta` represents the extent of overlap.\n\n    Args:\n        window_size: Size of each window\n        delta: The number of samples to increment. It is similar to overlap.\n          If delta is equal to window size, this means no overlap.\n        return_segment_index (False): Set to true to see the segment indexes\n          for start and end. Note: This should only be used for visualization not\n          pipeline building.\n    Returns:\n        DataFrame: Returns dataframe with `SegmentID` column added to the original dataframe.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n\n        >>> client.pipeline.add_transform('Windowing',\n                                        params={'window_size' : 5,\n                                                'delta': 5})\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                      Class  Rep  SegmentID Subject  accelx  accely  accelz\n               0   Crawling    1          0     s01     377     569    4019\n               1   Crawling    1          0     s01     357     594    4051\n               2   Crawling    1          0     s01     333     638    4049\n               3   Crawling    1          0     s01     340     678    4053\n               4   Crawling    1          0     s01     372     708    4051\n               5   Crawling    1          1     s01     410     733    4028\n               6   Crawling    1          1     s01     450     733    3988\n               7   Crawling    1          1     s01     492     696    3947\n               8   Crawling    1          1     s01     518     677    3943\n               9   Crawling    1          1     s01     528     695    3988\n               10   Running    1          0     s01     -44   -3971     843\n               11   Running    1          0     s01     -47   -3982     836\n               12   Running    1          0     s01     -43   -3973     832\n               13   Running    1          0     s01     -40   -3973     834\n               14   Running    1          0     s01     -48   -3978     844\n               15   Running    1          1     s01     -52   -3993     842\n               16   Running    1          1     s01     -64   -3984     821\n               17   Running    1          1     s01     -64   -3966     813\n               18   Running    1          1     s01     -66   -3971     826\n               19   Running    1          1     s01     -62   -3988     827\n\n\n    ",
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "2f22cec6-adf6-4278-9044-ea30667b8fab",
    name: "Segment Filter Threshold",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_column",
        type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Value which if passed will cause the segment to be filtered.",
      },
      {
        name: "comparison",
        type: "int",
        c_param: 1,
        default: 0,
        options: [0, 1],
        description:
          "0 for less than, 1 for greater than. If a value is greater/less than the segment will be filtered.",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Filters out segments that have values greater or less than the specified threshold.\n\n    Args:\n        input_column (str): The name of the column to use for filtering.\n        threshold (int16): The threshold value to filter against.\n        comparison (int): 0 for less than, 1 for greater than.\n\n    Returns:\n        DataFrame: Segments that pass the energy threshold.\n    ",
    type: "Transform",
    subtype: "Segment Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "8b588f08-49a4-4338-9b19-260ee8328513",
    name: "Stratified Shuffle Split",
    input_contract: [
      {
        name: "test_size",
        type: "float",
        range: [0, 0.4],
        default: 0,
      },
      {
        name: "validation_size",
        type: "float",
        range: [0, 0.4],
        default: 0.2,
      },
      {
        name: "number_of_folds",
        type: "int",
        range: [1, 5],
        default: 1,
      },
    ],
    output_contract: [],
    description:
      "\n    A validation scheme which splits the data set into training, validation, and (optionally)\n    test sets based on the parameters provided, with similar distribution of labels (hence\n    stratified).\n\n    In other words, for a data set consisting of 100 samples in total with 40\n    samples from class 1 and 60 samples from class 2, for stratified shuffle split with\n    validation_size = 0.4, the validation set will consist of 40 samples with 16 samples from\n    class 1 and 24 samples from class 2, and the training set will consist of 60 samples\n    with 24 samples from class 1 and 36 samples from class 2.\n\n    For each fold, training and validation data re-shuffle and split.\n\n    Args:\n        test_size (float): target percent of total size to use for testing\n        validation_size (float): target percent of total size to use for validation\n        number_of_folds (int): the number of stratified folds (iteration) to produce\n\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "9fe66f29-4c0f-4ba4-964c-3bd1b867d893",
    name: "Stratified Metadata k-fold",
    input_contract: [
      {
        name: "number_of_folds",
        type: "int",
        range: [2, 5],
        default: 3,
      },
      {
        name: "metadata_name",
        type: "str",
        default: "",
      },
    ],
    output_contract: [],
    description:
      '\n    K-fold iterator variant with non-overlapping metadata/group and label\n    combination which also attempts to evenly distribute the number of each\n    class across each fold. This is similar to GroupKFold, where, you cannot\n    have the same group in in multiple folds, but in this case you cannot\n    have the same group and label combination across multiple folds.\n\n    The main use case is for time series data where you may have a Subject\n    group, where the subject performs several activities. If you build a model\n    using a sliding window to segment data, you will end up with "Subject A"\n    performing "action 1" many times. If you use a validation method that\n    splits up "Subject A" performing "action 1" into different folds it can\n    often result in data leakage and overfitting. If however, you build your\n    validation set such that "Subject A" performing "action 1" is only in a\n    single fold you can be more confident that your model is generalizing.\n    This validation will also attempt to ensure you have a similar amount\n    of "action 1\'s" across your folds.\n\n\n    Args:\n        number_of_folds (int): the number of stratified folds to produce\n        metadata_name (str): the metadata to group on for splitting data into folds.\n    ',
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "134bf758-0806-42b6-8e08-05a90560c143",
    name: "Transpose Signal",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Column on which to apply the feature generator",
        num_columns: -1,
        element_type: "str",
      },
      {
        name: "cutoff",
        type: "int",
        range: [1, 32768],
        c_param: 0,
        default: 1,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "params['cutoff']*len(params['columns'])",
      },
    ],
    description:
      "\n    Turns raw signal into a feature over a range.\n\n    Args:\n        input_data (DataFrame) : input data as pandas dataframe\n        columns:  list of columns on which to apply the feature generator\n        group_columns: List of column names for grouping\n        **kwargs:\n\n    Returns:\n        DataFrame: Returns data frame containing transpose range values of each specified column.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8],\n                               [0, 6, 3], [-2, 8, 7],\n                               [2, 9, 6]], columns= ['accelx', 'accely', 'accelz'])\n        >>> df\n            out:\n               accelx  accely  accelz\n            0      -3       6       5\n            1       3       7       8\n            2       0       6       3\n            3      -2       8       7\n            4       2       9       6\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force=True)\n        >>> client.pipeline.add_feature_generator([\"Transpose Range\"],\n                params = {\"group_columns\": [], 'range':2},\n                 function_defaults={\"columns\":['accelx']})\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n                   accelx_range0  accelx_range1\n            0         -3             3\n    ",
    type: "Feature Generator",
    subtype: "Transpose",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4172c18e-3307-45b5-85f7-9e4f9242ef71",
    name: "Mean Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculate the mean difference of each specified column. Works with grouped data.\n    For a given column, it finds difference of ith element and (i-1)th element and\n    finally takes the mean value of the entire column.\n\n    mean(diff(arr)) = mean(arr[i] - arr[i-1]), for all 1 <= i <= n.\n\n    Args:\n        columns:  The `columns` represents a list of all column names on which `mean_difference` is to be found.\n\n    Returns:\n        DataFrame : Return the number of mean difference divided by the length of the signal.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Mean Difference',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxMeanDifference  gen_0002_accelyMeanDifference  gen_0003_accelzMeanDifference\n            0     s01                           1.25                           0.75                           0.25\n\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "1809c4f9-141c-47ca-9574-64f760d7f30d",
    name: "Dominant Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "fixed_value",
          value: 512,
        },
      },
    ],
    description:
      "\n    Calculate the dominant frequency for each specified signal. For each column,\n    find the frequency at which the signal has highest power.\n\n    Note: the current FFT length is 512, data larger than this will be truncated.\n    Data smaller than this will be zero padded\n\n    Args:\n        columns: List of columns on which `dominant_frequency` needs to be calculated\n\n    Returns:\n        DataFrame of `dominant_frequency` for each column and the specified group_columns\n\n    Examples:\n        >>> import matplotlib.pyplot as plt\n        >>> import numpy as np\n\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Dominant Frequency',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz' ],\n                                              \"sample_rate\" : sample\n                                              }\n                                    }])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelxDomFreq  gen_0002_accelyDomFreq  gen_0003_accelzDomFreq\n            0      0     s01                    22.0                    28.0                    34.0\n            1      1     s01                    22.0                    26.0                    52.0\n\n    ",
    type: "Feature Generator",
    subtype: "Frequency",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "dd390934-a435-4517-8290-3ba4cee64ef4",
    name: "Average Energy",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Average Energy.\n\n    1) Calculate the element-wise square of the input columns.\n    2) Sum the squared components across each column for the total energy per sample.\n    3) Take the average of the sum of squares to get the average energy.\n\n    .. math::\n\n        \\frac{1}{N}\\sum_{i=1}^{N}x_{i}^2+y_{i}^2+..n_{i}^2\n\n\n    Args:\n        columns:  List of str; The `columns` represents a list of all\n                  column names on which `average_energy` is to be found.\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print(df)\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Average Energy',\n                                     'params':{ \"columns\": ['accelx','accely','accelz'] }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print(result)\n            out:\n              Subject  gen_0000_AvgEng\n            0     s01             95.0\n\n    ",
    type: "Feature Generator",
    subtype: "Energy",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4f2f95e9-e7e5-4cc9-9272-03721b529e74",
    name: "Negative Zero Crossings",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "numeric",
        range: [-32767, 32766],
        c_param: 0,
        default: 100,
        description: "value in addition to mean which must be crossed to count as a crossing",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the number of times the selected input crosses the mean+threshold and mean-threshold values with a negative slope. The threshold value is specified by the user.\n    crossing the mean value when the threshold is 0 only coutns as a single crossing.\n\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n        threshold: value in addition to mean which must be crossed to count as a crossing\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4f8cc0ba-ebda-11ea-b33b-080027b304c0",
    name: "Linear Regression Stats",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "4",
      },
    ],
    description:
      "\n    Calculate a linear least-squares regression and returns\n    the linear regression stats which are slope, intercept, r value, standard error.\n\n    slope: Slope of the regression line.\n    intercept: Intercept of the regression line.\n    r value: Correlation coefficient.\n    StdErr: Standard error of the estimated gradient.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n\n        >>> from pandas import DataFrame\n        >>> df = pd.DataFrame({'Subject': ['s01'] * 10,'Class': ['Crawling'] * 10 ,'Rep': [1] * 10 })\n        >>> df[\"X\"] = [i + 2 for i in range(10)]\n        >>> df[\"Y\"] = [i for i in range(10)]\n        >>> df[\"Z\"] = [1, 2, 3, 3, 5, 5, 7, 7, 9, 10]\n        >>> print(df)\n            out:\n              Subject     Class  Rep   X  Y   Z\n            0     s01  Crawling    1   2  0   1\n            1     s01  Crawling    1   3  1   2\n            2     s01  Crawling    1   4  2   3\n            3     s01  Crawling    1   5  3   3\n            4     s01  Crawling    1   6  4   5\n            5     s01  Crawling    1   7  5   5\n            6     s01  Crawling    1   8  6   7\n            7     s01  Crawling    1   9  7   7\n            8     s01  Crawling    1  10  8   9\n            9     s01  Crawling    1  11  9  10\n\n\n        >>> client.upload_dataframe('test_data', df, force=True)\n        >>> client.pipeline.reset(delete_cache=True)\n        >>> client.pipeline.set_input_data('test_data.csv',\n                                        group_columns=['Subject','Rep'],\n                                        label_column='Class',\n                                        data_columns=['X','Y','Z'])\n        >>> client.pipeline.add_feature_generator([{'name':'Linear Regression Stats',\n                                                 'params':{\"columns\": ['X','Y','Z'] }}])\n        >>> results, stats = client.pipeline.execute()\n        >>> print(results.T)\n            out:\n                                                     0\n            Rep                                      1\n            Subject                                s01\n            gen_0001_XLinearRegressionSlope          1\n            gen_0001_XLinearRegressionIntercept      2\n            gen_0001_XLinearRegressionR              1\n            gen_0001_XLinearRegressionStdErr         0\n            gen_0002_YLinearRegressionSlope          1\n            gen_0002_YLinearRegressionIntercept      0\n            gen_0002_YLinearRegressionR              1\n            gen_0002_YLinearRegressionStdErr         0\n            gen_0003_ZLinearRegressionSlope      0.982\n            gen_0003_ZLinearRegressionIntercept  0.782\n            gen_0003_ZLinearRegressionR          0.987\n            gen_0003_ZLinearRegressionStdErr     0.056\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "cac0ee90-6735-4596-9819-fc85f6ae6d31",
    name: "Percent Time Over Sigma",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Percentage of samples in the series that are above the sample mean + one sigma\n\n    Args:\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Percent Time Over Sigma',\n                                     'params':{\"columns\": ['accelx','accely','accelz'] }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                Class  Rep Subject  gen_0001_accelxPctTimeOverSigma  gen_0002_accelyPctTimeOverSigma  gen_0003_accelzPctTimeOverSigma\n          0  Crawling    1     s01                         0.181818                         0.090909                         0.090909\n          1   Running    1     s01                         0.272727                         0.090909                         0.272727\n\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4c609bb9-dd16-41b6-b179-8a511efe83b2",
    name: "Isolation Forest Filtering",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "filtering_label",
        type: "list",
        default: [],
        description: "List of classes.",
        display_name: "Filtering Label",
      },
      {
        name: "feature_columns",
        type: "list",
        default: [],
        description: "List of features.",
        display_name: "Feature Columns",
      },
      {
        name: "outliers_fraction",
        type: "float",
        range: [0.01, 1],
        default: 0.05,
        description: "Define the ratio of outliers.",
        display_name: "Outliers Fraction",
      },
      {
        name: "assign_unknown",
        type: "bool",
        default: false,
        description: "Assign unknown label to outliers.",
        display_name: "Assign Unknown",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Isolation Forest Algorithm returns the anomaly score of each sample using the IsolationForest\n    algorithm. The \"Isolation Forest\" isolates observations by randomly selecting a feature and\n    then randomly selecting a split value between the maximum and minimum values of the selected\n    feature.\n\n    Args:\n        input_data: Dataframe, feature set that is results of generator_set or feature_selector\n        label_column (str): Label column name.\n        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.\n        feature_columns: List<String>, List of features. if it is not defined, it uses all features.\n        outliers_fraction (float) : Define the ratio of outliers.\n        assign_unknown (bool): Assign unknown label to outliers.\n\n    Returns:\n        DataFrame containing features without outliers and noise.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices before the filtering algorithm\n        >>> results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5, 6, 7, 8]\n\n        >>> client.pipeline.add_transform(\"Isolation Forest Filtering\",\n                           params={ \"outliers_fraction\": 0.01})\n\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices after the filtering algorithm\n        >>>results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5]\n\n\n    ",
    type: "Sampler",
    subtype: "Outlier Filter",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "6bbc8c35-2fb9-4196-8d7c-a5bf7a4976c7",
    name: "Boosted Tree Ensemble",
    input_contract: [],
    output_contract: [],
    description:
      "\n    The boosted tree ensemble classifier is an ensemble of decision trees that are evaluated against an input vector. Each\n    decision tree in the ensemble provides a bias towards a predicted value and the sum overall all biases determines\n    the final prediction.\n\n    ",
    type: "Classifier",
    subtype: "Ensemble",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "56468471-da19-4673-ab0b-37867537afb8",
    name: "Bonsai",
    input_contract: [],
    output_contract: [],
    description:
      "\n    Bonsai is a tree model for supervised learning tasks such as binary and multi-class classification,\n    regression, ranking, etc. Bonsai learns a single, shallow, sparse tree with powerful predictors at\n    internal and leaf nodes. This allows Bonsai to achieve state-of-the-art prediction accuracies\n    while making predictions efficiently in microseconds to milliseconds (depending on processor speed)\n    using models that fit in a few KB of memory.\n\n    Bonsai was developed by Microsoft, for detailed information see the `ICML 2017 Paper <https://github.com/Microsoft/EdgeML/wiki/files/BonsaiPaper.pdf>`_.\n\n    ",
    type: "Classifier",
    subtype: "Ensemble",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "145a8e6a-25ec-4f41-badf-a8b95767d9e5",
    name: "Skewness",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    The skewness is the measure of asymmetry of the distribution of a variable\n    about its mean. The skewness value can be positive, negative, or even undefined.\n    A positive skew indicates that the tail on the right side is fatter than the left.\n    A negative value indicates otherwise.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                    [-2, 8, 7], [2, 9, 6]],\n                    columns=['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Skewness',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxSkew  gen_0002_accelySkew  gen_0003_accelzSkew\n            0     s01                  0.0             0.363174            -0.395871\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b27d1290-d4cf-4c9b-8ff9-aff889368fa0",
    name: "Minimum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the minimum of each column in 'columns' in the dataframe.\n    A minimum of a vector V the minimum value in V.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Minimum',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxminimum  gen_0002_accelyminimum  gen_0003_accelzminimum\n            0     s01                    -3.0                     6.0                     3.0\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "1f60221b-7ecc-4545-88ed-f38403d6baec",
    name: "Maximum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the maximum of each column in 'columns' in the dataframe.\n    A maximum of a vector V the maximum value in V.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Maximum',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxmaximum  gen_0002_accelymaximum  gen_0003_accelzmaximum\n            0     s01                     3.0                     9.0                     8.0\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "33875688-5aec-470b-b599-88c85df77412",
    name: "Decision Tree Ensemble",
    input_contract: [],
    output_contract: [],
    description:
      "\n    The decision tree ensemble classifier is an ensemble of decision trees that are evaluated against an input vector. Each\n    decision tree in the ensemble provides a single prediction and the majority vote of all the trees is returned\n    as the prediction for the ensemble.\n\n    ",
    type: "Classifier",
    subtype: "Ensemble",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e58e18f1-8c8e-4c9c-8cc0-720fe41f2556",
    name: "Min Max Scale",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "passthrough_columns",
        type: "list",
      },
      {
        name: "min_bound",
        type: "numeric",
        range: [0, 255],
        default: 0,
      },
      {
        name: "max_bound",
        type: "numeric",
        range: [0, 255],
        default: 255,
      },
      {
        name: "pad",
        type: "float",
        range: [0, 10],
        default: null,
      },
      {
        name: "feature_min_max_parameters",
        type: "dict",
        default: null,
      },
      {
        name: "feature_min_max_defaults",
        type: "dict",
        default: null,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
      {
        name: "feature_min_max_parameters",
        type: "list",
        persist: true,
      },
    ],
    description:
      "\n    Normalize and scale data to integer values between min_bound and max_bound,\n    while leaving specified passthrough columns unscaled. This operates on each\n    feature column separately and  saves min/max data transforming the features\n    prior to classification\n\n    Args:\n        min_bound: min value in the output (0~255)\n        max_bound: max value in the output (0~255)\n        feature_min_max_parameters: Dictionary of 'maximums' and 'minimums'.\n            If a non-empty dictionary is passed as parameter, the minimum and maximum value will\n            be calculated based on the 'maximums' and 'minimums' in the dictionary. If the value\n            of this parameter is {}, then a new min-max value for each feature is\n            calculated.\n        pad: pad the min and max value by +-col.std()/pad. Can be used to make min max more robust to\n             unseen data.\n        feature_min_max_defaults: allows you to set the min max value for all values at once. example {'minimum':-1000, maximum:1000}\n\n    Returns:\n        The scaled dataframe and minimums and maximums for each feature.\n        If 'feature_min_max_parameters' values is {} then the minimums\n        and maximums for each feature are calculated based on the data passed.\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                            [-2, 8, 7], [2, 9, 6]],\n                            columns=['feature1', 'feature2', 'feature3'])\n        >>> df['Subject'] = 's01'\n        >>> df\n            Out:\n               feature1  feature2  feature3 Subject\n            0        -3         6         5     s01\n            1         3         7         8     s01\n            2         0         6         3     s01\n            3        -2         8         7     s01\n            4         2         9         6     s01\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force = True)\n        >>> client.pipeline.add_transform('Min Max Scale',\n                params={'passthrough_columns':['Subject'],\n                        'min_bound' : 0, 'max_bound' : 255})\n            Out:\n                  Subject  feature1  feature2  feature3\n                0     s01         0         0       101\n                1     s01       254        84       254\n                2     s01       127         0         0\n                3     s01        42       169       203\n                4     s01       212       254       152\n\n        Passing min-max parameter as arguments\n\n        >>> my_min_max_param = {'maximums': {'feature1': 30,\n                                            'feature2': 100,\n                                            'feature3': 500},\n                                'minimums': {'feature1': 0,\n                                            'feature2': 0,\n                                            'feature3': -100}}\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force = True)\n        >>> client.pipeline.add_transform('Min Max Scale',\n                            params={'passthrough_columns':['Subject'],\n                                    'min_bound' : 0,\n                                    'max_bound' : 255,\n                                    'feature_min_max_parameters': my_min_max_param})\n        >>> results, stats = client.pipeline.execute()\n        >>> print results, stats\n            Out:\n                    feature1  feature2  feature3 Subject\n                 0         0        15        44     s01\n                 1        25        17        45     s01\n                 2         0        15        43     s01\n                 3         0        20        45     s01\n                 4        16        22        45     s01\n    ",
    type: "Transform",
    subtype: "Feature Vector",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "692f128e-5529-4dc8-b22c-0da3c8f35db5",
    name: "Abs Percent Time Over Threshold",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Threshold to check for percent time over",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Percentage of absolute value of samples in the series that are above the offset\n\n    ",
    type: "Feature Generator",
    subtype: "Time",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e81959cf-6ea0-476d-90ed-ae61afc88602",
    name: "Shape Median Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "center_ratio",
        type: "numeric",
        range: [0.1, 0.9],
        c_param: 0,
        default: 0.5,
        description: "ratio of the signal to be on the first half to second half",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "\n    Computes the difference in median between the first and second half of a signal\n\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n        center_ratio: ratio of the signal to be on the first half to second half\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Shape Median Difference',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'],\n                                               \"center_ratio: 0.5}\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n              Subject  gen_0001_accelxShapeMedianDifference  gen_0002_accelyShapeMedianDifference  gen_0003_accelzShapeMedianDifference\n            0     s01\n    ",
    type: "Feature Generator",
    subtype: "Shape",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "09b101ba-8d80-44e1-ad17-0898308e02eb",
    name: "Average Demeaned Energy",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Average Demeaned Energy.\n\n    1) Calculate the element-wise demeaned by its column average of the input columns.\n    2) Sum the squared components across each column for the total demeaned energy per sample.\n    3) Take the average of the sum of squares to get the average demeaned energy.\n\n    Args:\n        columns:  List of str; The `columns` represents a list of all\n                  column names on which `average_energy` is to be found.\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Average Demeaned Energy',\n                                     'params':{ \"columns\": ['accelx','accely','accelz'] }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0000_AvgDemeanedEng\n            0     s01                     9.52\n\n    ",
    type: "Feature Generator",
    subtype: "Energy",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "68b5d1f6-f4fd-4a9e-8e53-aee51eddbb49",
    name: "Global Min Max Sum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This function is the sum of the maximum and minimum values. It is also\n    used as the 'min max amplitude difference'.\n\n    Args:\n        columns: (list of str): Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame of `min max sum` for each column and the specified group_columns\n\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],\n                            columns=['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Global Min Max Sum',\n                                     'params':{\"columns\": ['accelx','accely','accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Subject  gen_0001_accelxMinMaxSum  gen_0002_accelyMinMaxSum  gen_0003_accelzMinMaxSum\n            0     s01                       0.0                      15.0                      11.0\n\n    ",
    type: "Feature Generator",
    subtype: "Amplitude",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e81959cf-6ea0-476d-90ed-ae61afc88604",
    name: "Shape Absolute Median Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "center_ratio",
        type: "numeric",
        range: [0.1, 0.9],
        c_param: 0,
        default: 0.5,
        description: "ratio of the signal to be on the first half to second half",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "\n    Computes the absolute value of the difference in median between the first and second half of a signal\n\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n        center_ratio: ratio of the signal to be on the first half to second half\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Shape Absolute Median Difference',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'],\n                                            \"center_ratio\": 0.5}\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n              Subject  gen_0001_accelxShapeAbsoluteMedianDifference  gen_0002_accelyShapeAbsoluteMedianDifference  gen_0003_accelzShapeAbsoluteMedianDifference\n            0     s01\n    ",
    type: "Feature Generator",
    subtype: "Shape",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b47ce2ce-e05b-475d-8c95-cd84a575414b",
    name: "Second Sigma Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the rate at which 2nd standard deviation value (second sigma) is\n    crossed for each specified column. The total number of second sigma crossings\n    are found and then the number is divided by total number of samples  to get\n    the `second_sigma_crossing_rate`.\n\n\n    Args:\n        columns:  The `columns` represents a list of all column names on which\n                  `second_sigma_crossing_rate` is to be found.\n\n    Returns:\n        DataFrame : Return the second sigma crossing rate.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Second Sigma Crossing Rate',\n                                     'params':{\"columns\": ['accelx','accely', 'accelz']}\n                                    }])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0001_accelx2ndSigmaCrossingRate  gen_0002_accely2ndSigmaCrossingRate  gen_0003_accelz2ndSigmaCrossingRate\n            0  Crawling    1     s01                             0.090909                             0.090909                                  0.0\n            1   Running    1     s01                             0.000000                             0.000000                                  0.0\n\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "250f1952-62b2-472f-9486-ff33f1d0d3a3",
    name: "Mean Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the rate at which the mean value is crossed for each specified column.\n    Works with grouped data. The total number of mean value crossings are found\n    and then the number is divided by the total number of samples to get\n    the `mean_crossing_rate`.\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (list of strings): A list of all column names on which `mean_crossing_rate` is to be found.\n\n    Returns:\n        DataFrame : Return the number of mean crossings divided by the length of the signal.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n\n        >>> client.pipeline.add_feature_generator([{'name':'Mean Crossing Rate',\n                                     'params':{\"columns\": ['accelx','accely', 'accelz']}\n                                    }])\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0001_accelxMeanCrossingRate  gen_0002_accelyMeanCrossingRate  gen_0003_accelzMeanCrossingRate\n            0  Crawling    1     s01                         0.181818                         0.090909                         0.090909\n            1   Running    1     s01                         0.090909                         0.454545                         0.363636\n\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "5c2a69e3-c831-43d0-8401-1ba26eeddc50",
    name: "Threshold Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Threshold to check for crossing rate over",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the rate at which each specified column crosses a given threshold.\n    The total number of threshold crossings are found,\n    and then the number is divided by the total number of samples to get the `threshold_crossing_rate`.\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (list of strings): A list of all column names on which `threshold_crossing_rate` is to be found.\n        threshold (int, optional): The threshold value. Defaults to 0.\n\n    Returns:\n        DataFrame : Return the number of threshold crossings divided by the length of the signal.\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e144859b-6d65-4bd1-93fc-3542a364cf39",
    name: "Average of Movement Intensity",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the average movement intensity defined by:\n\n    .. math::\n\n        \\frac{1}{N}\\sum_{i=1}^{N} \\sqrt{x_{i}^2 + y_{i}^2 + .. n_{i}^2}\n\n    Args:\n        columns (list):  list of columns to calculate average movement intensity.\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print(df)\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Average of Movement Intensity',\n                                     'params':{ \"columns\": ['accelx','accely','accelz'] }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print(result)\n            out:\n              Subject  gen_0000_AvgInt\n            0     s01         9.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Physical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "00780f99-45c9-4056-990a-ea8339076757",
    name: "Average Signal Magnitude Area",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Average signal magnitude area.\n\n    .. math::\n\n        \\frac{1}{N}\\sum_{i=1}^{N} {x_{i} + y_{i} + .. n_{i}}\n\n    Args:\n        columns:  List of str; The `columns` represents a list of all\n                  column names on which `average_energy` is to be found.\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print(df)\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':\"Average Signal Magnitude Area\",\n                                     'params':{ \"columns\": ['accelx','accely','accelz'] }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print(result)\n            out:\n              Subject  gen_0000_AvgSigMag\n                s01          13.0\n\n    ",
    type: "Feature Generator",
    subtype: "Physical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e81959cf-6ea0-476d-90ed-ae61afc88607",
    name: "Ratio of Peak to Peak of High Frequency between two halves",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the ratio of peak to peak of high frequency between two halves. The high frequency\n    signal is calculated by subtracting the moving average filter output from the original signal.\n\n    Args:\n        input_data (DataFrame): Input pandas dataframe.\n        smoothing_factor (int): Determines the amount of attenuation for frequencies over the cutoff frequency.\n            Number of elements in individual columns should be at least three times the smoothing factor.\n        columns (List[str]): List of column names on which to apply the feature generator.\n\n    Returns:\n        DataFrame: `ratio high frequency` for each column and the specified group_columns.\n\n    Examples:\n        >>> import numpy as np\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Ratio of Peak to Peak of High Frequency between two halves',\n                                     'params':{\"smoothing_factor\": 5,\n                                               \"columns\": ['accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelzACRatio\n            0      0     s01                3.888882\n            1      1     s01                0.350000\n\n    ",
    type: "Feature Generator",
    subtype: "Shape",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "a6cdad7e-9a7b-445d-84c8-a61d3b8f2d93",
    name: "Difference of Peak to Peak of High Frequency between two halves",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the difference of peak to peak of high frequency between two halves.\n    The high frequency signal is calculated by subtracting the moving average filter output from the original signal.\n\n    Args:\n        input_data (DataFrame): Input pandas dataframe.\n        smoothing_factor (int): Determines the amount of attenuation for frequencies over the cutoff frequency.\n            Number of elements in individual columns should be at least three times the smoothing factor.\n        columns (List[str]): List of column names on which to apply the feature generator.\n\n\n    Returns:\n        DataFrame: `difference high frequency` for each column and the specified group_columns.\n\n\n    Examples:\n        >>> import numpy as np\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Difference of Peak to Peak of High Frequency between two halves',\n                                     'params':{\"smoothing_factor\": 5,\n                                               \"columns\": ['accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelzACDiff\n            0      0     s01              -5.199997\n            1      1     s01              13.000000\n\n\n    ",
    type: "Feature Generator",
    subtype: "Shape",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "a96aa2da-a344-4db5-b0dc-67db473d091b",
    name: "t-Test Feature Selector",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "feature_number",
        type: "int",
        default: 1,
        description: "The number of features you would like select for each class",
        handle_by_set: false,
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "The set of columns the selector should ignore",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This is a supervised feature selection algorithm that selects features based on a two-tailed t-test.\n    It computes the p-values and selects the top-performing number of features for each class as defined by feature_number.\n    It returns a reduced combined list of all the selected features.\n\n    Args:\n        input_data (DataFrame): Input data\n        label_column (str): Column containing class labels\n        feature_number (int): Number of features to select for each class\n        passthrough_columns (Optional[List[str]]): List of columns that the selector should ignore\n\n    Returns:\n        Tuple[DataFrame, List[str]]: A tuple containing:\n            - DataFrame: DataFrame which includes selected features and the passthrough columns.\n            - List[str]: List of unselected features.\n\n     Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.add_feature_selector([{'name':'ttest Feature Selector',\n                'params':{\"feature_number\": 2 }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            Out:\n             [u'Class',\n             u'Subject',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_4']\n\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "3b7ab03e-81fc-4d4d-afd8-42cc1c6c2e42",
    name: "Histogram Auto Scale Range",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Column on which to apply the feature generator",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "number_of_bins",
        type: "int",
        range: [1, 255],
        c_param: 0,
        default: 32,
      },
      {
        name: "scaling_factor",
        type: "int",
        range: [1, 255],
        c_param: 1,
        default: 255,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "params['number_of_bins']",
        scratch_buffer: {
          name: "number_of_bins",
          type: "parameter",
        },
      },
    ],
    description:
      "\n    Translates to the data stream(s) from a segment into a feature vector in histogram space where the range\n    is set by the min and max values and the number of bins by the user.\n\n    Args:\n        column (list of strings): name of the sensor streams to use\n        number_of_bins (int, optional): the number of bins used for the histogram\n        scaling_factor (int, optional): scaling factor used to fit for the device\n\n    Returns:\n        DataFrame: feature vector in histogram space.\n\n    Examples:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> print df\n            out:\n               Subject     Class  Rep  accelx  accely  accelz\n            0      s01  Crawling    1     377     569    4019\n            1      s01  Crawling    1     357     594    4051\n            2      s01  Crawling    1     333     638    4049\n            3      s01  Crawling    1     340     678    4053\n            4      s01  Crawling    1     372     708    4051\n            5      s01  Crawling    1     410     733    4028\n            6      s01  Crawling    1     450     733    3988\n            7      s01  Crawling    1     492     696    3947\n            8      s01  Crawling    1     518     677    3943\n            9      s01  Crawling    1     528     695    3988\n            10     s01  Crawling    1      -1    2558    4609\n            11     s01   Running    1     -44   -3971     843\n            12     s01   Running    1     -47   -3982     836\n            13     s01   Running    1     -43   -3973     832\n            14     s01   Running    1     -40   -3973     834\n            15     s01   Running    1     -48   -3978     844\n            16     s01   Running    1     -52   -3993     842\n            17     s01   Running    1     -64   -3984     821\n            18     s01   Running    1     -64   -3966     813\n            19     s01   Running    1     -66   -3971     826\n            20     s01   Running    1     -62   -3988     827\n            21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Histogram',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"range_left\": 10,\n                                               \"range_right\": 1000,\n                                               \"number_of_bins\": 5,\n                                               \"scaling_factor\": 254 }}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            out:\n                  Class  Rep Subject  gen_0000_hist_bin_000000  gen_0000_hist_bin_000001  gen_0000_hist_bin_000002  gen_0000_hist_bin_000003  gen_0000_hist_bin_000004\n            0  Crawling    1     s01                       8.0                      38.0                      46.0                      69.0                       0.0\n            1   Running    1     s01                      85.0                       0.0                       0.0                       0.0                      85.0\n\n    ",
    type: "Feature Generator",
    subtype: "Histogram",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "19b2fe3c-3c29-4e74-bb15-e1c7cfcd23b4",
    name: "Power Spectrum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "number_of_bins",
        type: "numeric",
        range: [4, 256],
        c_param: 0,
        default: 16,
        description: "number of bins to use to compute the power spectrum",
      },
      {
        name: "window_type",
        type: "str",
        c_param: 1,
        default: "hanning",
        options: [
          {
            name: "hanning",
          },
        ],
        description: "window function to use before fft",
        c_param_mapping: {
          hanning: 0,
        },
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "params['number_of_bins']",
        scratch_buffer: {
          type: "fixed_value",
          value: 512,
        },
      },
    ],
    description:
      "\n    Calculate the power spectrum for the signal. The resulting power spectrum will be binned into number_of_bins.\n\n    Note: The current FFT length is 512. Data larger than this will be truncated. Data smaller than this will be zero padded.\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (List[str]): A list of column names to use for the frequency calculation.\n        window_type (str): The type of window to apply to the signal before taking the FFT. Defaults to 'hanning'.\n        number_of_bins (int): The number of bins to use to compute the power spectrum.\n\n    Returns:\n        DataFrame: DataFrame containing the 'power spectrum' for each column and the specified group_columns.\n    ",
    type: "Feature Generator",
    subtype: "Frequency",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "f262ae18-8a55-47cc-b6da-699d00e4b59f",
    name: "Cross Column Mean Crossing with Offset",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "offset",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "Offset from the mean to use",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Compute the crossing rate of column 2 of over the mean of column 1\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use (requires 2 inputs)\n\n    Returns:\n        DataFrame: feature vector mean crossing rate\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "9d0aa12f-ffee-4937-89f6-efe581254fa2",
    name: "Two Column Median Difference",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "Compute the median difference between two columns.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n\n    Returns:\n        DataFrame: feature vector median difference\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "3eac2f77-5a8b-4e17-bb18-869fe83880a0",
    name: "Downsample Max With Normaliztion",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "new_length",
        type: "int",
        range: [5, 32],
        c_param: 0,
        default: 12,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: true,
        output_formula: "params['new_length']",
        scratch_buffer: {
          name: "new_length",
          type: "parameter",
        },
      },
    ],
    description:
      "\n    This function takes `input_data` dataframe as input and group by `group_columns`.\n    Then for each group, it drops the `passthrough_columns` and performs a max downsampling\n    on the remaining columns.\n\n    On each column, perform the following steps:\n\n    - Divide the entire column into windows of size total length/`new_length`.\n    - Calculate max value for each window\n    - Concatenate all the max values into a feature vector of length new_length\n    - Nomralize the signal to be between 0-255\n\n    Then all such means are concatenated to get `new_length` * # of columns. These constitute\n    features in downstream analyses. For instance, if there are three columns and the\n    `new_length` value is 12, then total number of means we get is 12 * 3 = 36. Each will represent a feature.\n\n    Args:\n        input_data (DataFrame): Input data to transform\n        columns: List of columns\n        group_columns (a list): List of columns on which grouping is to be done.\n                                 Each group will go through downsampling one at a time\n        new_length (int): Dopwnsample Length length\n\n    Returns:\n        DataFrame: Downsampled Features Normalized to the Max Value\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6],\n                            [3, 1], [3, 1], [4, 3], [5, 5],\n                            [4, 7], [3, 6]], columns=['accelx', 'accely'])\n        >>> df\n        Out:\n           accelx  accely\n        0       3       3\n        1       4       5\n        2       5       7\n        3       4       6\n        4       3       1\n        5       3       1\n        6       4       3\n        7       5       5\n        8       4       7\n        9       3       6\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('test_data', df, force=True)\n        >>> client.pipeline.add_feature_generator([\"Downsample Max with Normalization\"],\n                 params = {\"group_columns\": []},\n                           function_defaults={\"columns\":['accelx', 'accely'],\n                                             'new_length' : 5})\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            Out:\n                   accelx_1  accelx_2  accelx_3  accelx_4  accelx_5  accely_1  accely_2\n                0       3.5       4.5         3       4.5       3.5         4       6.5\n                   accely_3  accely_4  accely_5\n                0         1         4       6.5\n    ",
    type: "Feature Generator",
    subtype: "Sampling",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "f81d7808-2ca2-425f-8bc3-173c610af57b",
    name: "Peak Frequencies",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "min_frequency",
        type: "numeric",
        range: [0, 512],
        c_param: 1,
        default: 0,
        description: "min cutoff frequency",
      },
      {
        name: "max_frequency",
        type: "numeric",
        range: [0, 512],
        c_param: 2,
        default: 500,
        description: "max cutoff frequency",
      },
      {
        name: "threshold",
        type: "numeric",
        range: [0, 1],
        c_param: 3,
        default: 0.2,
        description: "threshold value a peak must be above",
      },
      {
        name: "num_peaks",
        type: "numeric",
        range: [1, 12],
        c_param: 4,
        default: 2,
        description: "number of frequency peaks to find",
      },
      {
        name: "window_type",
        type: "str",
        c_param: 5,
        default: "hanning",
        options: [
          {
            name: "hanning",
          },
        ],
        description: "window function to use before fft",
        c_param_mapping: {
          hanning: 0,
        },
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        scratch_buffer: {
          type: "fixed_value",
          value: 512,
        },
      },
    ],
    description:
      "\n    Calculate the peak frequencies for each specified signal. For each column, find the frequencies at which the signal\n    has highest power.\n\n    Note: The current FFT length is 512. Data larger than this will be truncated. Data smaller than this will be zero padded.\n          The FFT is computed and the cutoff frequency is converted to a bin based on the following formula:\n          fft_min_bin_index = (min_freq * FFT_length / sample_rate)\n          fft_max_bin_index = (max_freq * FFT_length / sample_rate)\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (List[str]): A list of column names on which 'dominant_frequency' needs to be calculated.\n        sample_rate (int): The sample rate of the sensor data.\n        window_type (str): The type of window to apply to the signal before taking the FFT. Currently only 'hanning'\n                           window is supported.\n        num_peaks (int): The number of peaks to identify.\n        min_frequency (int): The minimum frequency bound to look for peaks.\n        max_frequency (int): The maximum frequency bound to look for peaks.\n        threshold (int): The threshold value that a peak must be above to be considered a peak.\n\n    Returns:\n        DataFrame: DataFrame containing the 'peak frequencies' for each column and the specified group_columns.\n    ",
    type: "Feature Generator",
    subtype: "Frequency",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c16961e9-5d48-46e6-bf79-62d926f8cae3",
    name: "Normalize Segment",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "mode",
        type: "str",
        c_param: 0,
        options: [
          {
            name: "mean",
          },
          {
            name: "median",
          },
          {
            name: "none",
          },
          {
            name: "zero",
          },
        ],
        c_param_mapping: {
          None: 2,
          mean: 0,
          zero: 3,
          median: 1,
        },
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Subtract a value from the data defined by the mode selected, then expand the data to fill MAX_INT_16.\n\n    Args:\n        input_data (DataFrame): Input data to be normalized.\n        group_columns (list): List of column names to group by.\n        input_columns (list): List of column names to be normalized.\n        mode (str): Normalization mode, which can be 'mean', 'median', \"zero\" or 'none'.\n         zero - zeros out the segment by subtracting the starting value of data\n         from the rest of the segment\n         none - skips the subtraction steps and only expands the data\n\n    Returns:\n        DataFrame: Normalized data as a new DataFrame.\n    ",
    type: "Transform",
    subtype: "Segment",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "9b58bb6c-ec39-426b-8905-39fe246a6f3d",
    name: "Segment Energy Threshold Filter",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_column",
        type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
        description: "The threshold that must be crossed for the segment to not be filtered.",
      },
      {
        name: "backoff",
        type: "int",
        range: [0, 64],
        c_param: 1,
        default: 0,
        description:
          "The backoff is used on the device to determine how many segments after a non filtered segment to continue passing if they are below the threshold.",
      },
      {
        name: "delay",
        type: "int",
        range: [0, 64],
        c_param: 2,
        default: 0,
        description: "The delay after the event is triggered before starting classification.",
      },
      {
        name: "disable_train",
        type: "boolean",
        default: false,
        description:
          "Disables the segment filter during training. This is typically used in conjunction with the backoff parameter.",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Takes the absolute value of each point and compares it with the threshold. If no values are above the threshold, the segment is filtered.\n\n    Args:\n        input_data (_type_): _description_\n        input_column (_type_): _description_\n        group_columns (_type_): _description_\n        threshold (int, optional): _description_. Defaults to 0.\n        backoff (int, optional): _description_. Defaults to 0.\n        delay (int, optional): _description_. Defaults to 0.\n        disable_train (bool, optional): _description_. Defaults to False.\n\n    Returns:\n        DataFrame: The segments that were not filtered.\n    ",
    type: "Transform",
    subtype: "Segment Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "459d484c-be53-11ed-afa1-0242ac120002",
    name: "Add Noise",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "noise_types",
        type: "list",
        default: "[white]",
        description:
          'List of background noise flavors. Accepted values are: "white", "pink", "violet", and "blue".',
        element_type: "str",
        handle_by_set: false,
      },
      {
        name: "input_columns",
        type: "list",
        default: [],
        description: "List of sensors that are transformed by this augmentation.",
        handle_by_set: false,
      },
      {
        name: "fraction",
        type: "float",
        range: [0.1, 5],
        default: 2,
        description: "Fraction of the input data segments that are used for this augmentation.",
        handle_by_set: false,
      },
      {
        name: "background_scale_range",
        type: "list",
        range: [1, 10000],
        default: [1, 1000],
        description:
          "Range of the allowed factor to scale the background noise. The generated noise is drawn from a normal distribution, with the mean of zero and standard deviation of 1. Then it is scaled according to the provided scaled range to meet the synthetic data characteristics.",
        element_type: "float",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: false,
        description:
          "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      '\n    Add Noise:\n        Add random noise to time series.\n        The added noise to each sample is independent and follows the distribution provided by the method parameter.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        noise_types [str]: List of background noise flavors. Accepted values are: "white", "pink", "violet", and "blue".\n        input_columns [str]: List of sensors that are transformed by this augmentation.\n        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.\n        background_scale_range [int, int]: Allowed factor range to scale the background noise. The generated noise is drawn from a normal distribution, with the mean of zero and standard deviation of 1. Then it is scaled according to the provided scaled range to meet the synthetic data characteristics.\n        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of the datasegments with added background noise.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)\n        >>> client.upload_dataframe("toy_data.csv", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data(\'toy_data\',\n                                data_columns=[\'accelx\', \'accely\', \'accelz\'],\n                                group_columns=[\'Subject\', \'Class\', \'Rep\', \'segment_uuid\'],\n                                label_column=\'Class\')\n        >>> client.pipeline.add_transform(\'Windowing\', params={\'window_size\' : 5, \'delta\': 5})\n\n        >>> client.pipeline.add_augmentation(\n                                [\n                                    {\n                                        "name": "Add Noise",\n                                        "params": {\n                                            "background_scale_range": [100, 200],\n                                            "fraction": 1,\n                                            "noise_types": ["pink", "white"],\n                                            "target_labels": ["Crawling"],\n                                            "input_columns": ["accelx", "accely"],\n                                    },\n                                },\n\n                            ]\n                        )\n\n        >>> results, stats = client.pipeline.execute()\n\n        Only "Crawling" segments are augmented by adding noise to their "accelx", and "accely" columns.\n        Original segments are NOT removed from the output dataset.\n\n        >>> print(results)\n            Out:\n                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n                0      332     794    4028  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001\n                1      200     753    3988  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001\n                2      447     666    3947  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001\n                3      480     474    3943  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001\n                4      467     839    3988  Crawling    1     s01  07baf4b8-21b9-fff0-de12-44af0a3d2f00  900000001\n                5      400     738    4019  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000\n                6      676     274    4051  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000\n                7      244     503    4049  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000\n                8       43     843    4053  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000\n                9      441     889    4051  Crawling    1     s01  07baf4b8-21b9-fff0-de12-8b54cdfe8f00  248000000\n                10     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                11     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                12     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                13     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                14     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                15     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                16     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                17     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                18     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                19     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                20     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                21     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                22     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                23     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                24     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                25     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                26     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                27     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                28     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                29     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n\n    ',
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c3e45cb6-47d5-4641-8220-400bb4f556d4",
    name: "Robust Covariance Filtering",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "filtering_label",
        type: "list",
        default: [],
        description: "List of classes.",
        display_name: "Filtering Label",
      },
      {
        name: "feature_columns",
        type: "list",
        default: [],
        description: "List of features.",
        display_name: "Feature Columns",
      },
      {
        name: "outliers_fraction",
        type: "float",
        range: [0.01, 1],
        default: 0.05,
        description: "Define the ratio of outliers.",
        display_name: "Outliers Fraction",
      },
      {
        name: "assign_unknown",
        type: "bool",
        default: false,
        description: "Assign unknown label to outliers.",
        display_name: "Assign Unknown",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Unsupervised Outlier Detection. An object for detecting outliers in a Gaussian distributed dataset.\n\n    Args:\n        input_data: Dataframe, feature set that is results of generator_set or feature_selector\n        label_column (str): Label column name.\n        filtering_label: List<String>, List of classes. if it is not defined, it use all classes.\n        feature_columns: List<String>, List of features. if it is not defined, it uses all features.\n        outliers_fraction (float) : An upper bound on the fraction of training errors and a lower bound of the fraction of support vectors. Should be in the interval (0, 1]. By default 0.5 will be taken.\n        assign_unknown (bool): Assign unknown label to outliers.\n\n    Returns:\n        DataFrame containing features without outliers and noise.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices before the filtering algorithm\n        >>> results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5, 6, 7, 8]\n\n        >>> client.pipeline.add_transform(\"Robust Covariance Filtering\",\n                           params={\"outliers_fraction\": 0.05})\n\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices after the filtering algorithm\n        >>>results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5]\n\n    ",
    type: "Sampler",
    subtype: "Outlier Filter",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "969f333e-e079-45dc-ab4b-ab501d8a6ee5",
    name: "Split by Metadata Value",
    input_contract: [
      {
        name: "metadata_name",
        type: "str",
        default: "Set",
        lookup_field: "metadata_name",
      },
      {
        name: "training_values",
        type: "list",
        default: ["Train"],
        options: ["Train"],
        element_type: "str",
        lookup_field: "metadata_label_values",
      },
      {
        name: "validation_values",
        type: "list",
        default: ["Validate"],
        options: ["Validate", "Test"],
        element_type: "str",
        lookup_field: "metadata_label_values",
      },
    ],
    output_contract: [],
    description:
      "\n    A validation scheme wherein the data set is divided into training and test sets based\n    on the metadata value. In other words, for a data set consisting of 100 samples with the\n    metadata column set to 'train' for 60 samples, and 'test' for 40 samples, the training set\n    will consist of 60 samples for which the metadata value is 'train' and the test set will\n    consist of 40 samples for which the metadata value is 'test'.\n\n    Args:\n        metadata_name (str): name of the metadata column to use for splitting\n        training_values (list[str]): list of values of the named column to select samples for\n          training\n        validation_values (list[str)): list of values of the named column to select samples for\n          validation\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "f926150c-3b8e-4a12-8895-3a598e7dc1a3",
    name: "Global Peak to Peak",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Global Peak to Peak of signal.\n\n    Args:\n        columns: (list of str): Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame of `peak to peak` for each column and the specified group_columns\n\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3], [-2, 8, 7], [2, 9, 6]],\n                            columns=['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Global Peak to Peak',\n                                     'params':{\"columns\": ['accelx','accely','accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n              Subject  gen_0001_accelxP2P  gen_0002_accelyP2P  gen_0003_accelzP2P\n            0     s01                 6.0                 3.0                 5.0\n\n    ",
    type: "Feature Generator",
    subtype: "Amplitude",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "43551a11-5f2d-4a96-b979-574c7b9e8350",
    name: "Combine Labels",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "combine_labels",
        type: "dict",
        description: "Map of label columns to combine",
        element_type: "list_str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Select rows from the input DataFrame based on a metadata column. Rows that have\n    a label value that is in the combined label list will be returned.\n\n    Syntax:\n        combine_labels = {'group1': ['label1', 'label2'], 'group2': ['label3', 'label4'],\n                          'group3': ['group5']}\n\n    Args:\n        input_data (DataFrame): Input DataFrame.\n        label_column (str): Label column name.\n        combine_labels (dict): Map of label columns to combine.\n\n    Returns:\n        DataFrame: The input_data containing only the rows for which the label value is in\n        the combined list.\n    ",
    type: "Sampler",
    subtype: "Feature Grouping",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "5d685c61-26d7-4298-b309-615732d7fb62",
    name: "General Threshold Segmentation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        no_display: true,
      },
      {
        name: "first_column_of_interest",
        type: "str",
        streams: true,
        description: "column used to identify the start of the segment",
        display_name: "First Column Of Interest",
        number_of_elements: 1,
      },
      {
        name: "second_column_of_interest",
        type: "str",
        streams: true,
        description: "column used to identify the end of the segment",
        display_name: "Second Column Of Interest",
        number_of_elements: 1,
      },
      {
        name: "group_columns",
        type: "list",
        no_display: true,
        element_type: "str",
      },
      {
        name: "max_segment_length",
        type: "int",
        c_param: 1,
        default: 200,
        description: "maximum number of samples a segment can have",
        display_name: "Maximum Segment Length",
      },
      {
        name: "min_segment_length",
        type: "int",
        c_param: 2,
        default: 50,
        description: "minimum number of samples a segment can have",
        display_name: "Minimum Segment Length",
      },
      {
        name: "threshold_space_width",
        type: "int",
        c_param: 3,
        default: 25,
        description: "the size of the window to transform into threshold space",
        display_name: "Threshold Space Width",
      },
      {
        name: "first_vt_threshold",
        type: "float",
        c_param: 4,
        default: 1000,
        description: "the threshold value to identify the start of a segment",
        display_name: "Initial Vertical Threshold",
      },
      {
        name: "first_threshold_space",
        type: "str",
        default: "std",
        options: [
          {
            name: "std",
          },
          {
            name: "absolute sum",
          },
          {
            name: "sum",
          },
          {
            name: "variance",
          },
          {
            name: "absolute avg",
          },
        ],
        description:
          "space to transform signal into to compare against the first vertical threshold",
        display_name: "First Threshold Space",
      },
      {
        name: "first_comparison",
        type: "str",
        default: "max",
        options: [
          {
            name: "max",
          },
          {
            name: "min",
          },
        ],
        description: "the comparison between threshold space and vertical threshold (>=, <=)",
        display_name: "First Comparison",
      },
      {
        name: "second_vt_threshold",
        type: "float",
        c_param: 5,
        default: 1000,
        description: "the threshold value to identify the end of a segment",
        display_name: "Second Vertical Threshold",
      },
      {
        name: "second_threshold_space",
        type: "str",
        default: "std",
        options: [
          {
            name: "std",
          },
          {
            name: "absolute sum",
          },
          {
            name: "sum",
          },
          {
            name: "variance",
          },
          {
            name: "absolute avg",
          },
        ],
        description:
          "space to transform signal into to compare against the second vertical threshold",
        display_name: "Second Threshold Space",
      },
      {
        name: "second_comparison",
        type: "str",
        default: "min",
        options: [
          {
            name: "max",
          },
          {
            name: "min",
          },
        ],
        description: "the comparison between threshold space and vertical threshold (>=, <=)",
        display_name: "Second Comparison",
      },
      {
        name: "drop_over",
        type: "boolean",
        default: false,
        options: [
          {
            name: true,
          },
          {
            name: false,
          },
        ],
        description:
          "If the second threshold has not been triggered by max length, drop the segment.",
        display_name: "Drop over max length",
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
      },
      {
        name: "keep_partial_segment",
        type: "boolean",
        default: false,
        no_display: false,
        description:
          "When training if True, when the algorithm gets to the end of file and has only found part of a segment, it will keep the segment. If False it will discard any unfinished segments.",
        display_name: "Keep Partial Segment",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      '\n    This is a general threshold segmentation algorithm which transforms a window\n    of the data stream of size threshold_space_width into threshold space. This function\n    transfer the `input_data` and `group_column` from the previous pipeline block.\n\n    The threshold space can be computed as standard deviation, sum, absolute sum, absolute\n    average and variance. The vt threshold is then compared against the calculated value\n    with a comparison type of <= or >= based on the use of "min" or "max" in the comparison\n    type. This algorithm is a two pass detection, the first pass detects the start of the\n    segment, the second pass detects the end of the segment. In this generalized algorithm,\n    the two can be set independently.\n\n    Args:\n        first_column_of_interest (str): name of the stream to use for first threshold segmentation\n        second_column_of_interest (str): name of the stream to use for second threshold segmentation\n        max_segment_length (int): number of samples in the window (default is 200)\n        min_segment_length (int): The smallest segment allowed. (default 100)\n        first_vt_threshold (int):vt_threshold value to begin detecting a segment\n        first_threshold_space (str): threshold space to detect segment against (std, variance, absolute avg, absolute sum, sum)\n        first_comparison (str): detect threshold above(max) or below(min) the vt_threshold (max, min)\n        second_vt_threshold (int):vt_threshold value to detect a segments\n           end.\n        second_threshold_space (str): threshold space to detect segment end (std, variance, absolute avg, absolute sum, sum)\n        second_comparison (str): detect threshold above(max) or below(min) the vt_threshold (max, min)\n           threshold_space_width (int): the size of the buffer that the threshold value is calculated from.\n        return_segment_index (False): set to true to see the segment indexes for start and end.\n\n    Returns:\n        DataFrame: The segmented result will have a new column called `SegmentID` that\n        contains the segment IDs.\n\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.set_input_data(\'test_data\', df, force=True,\n                            data_columns=[\'accelx\', \'accely\', \'accelz\'],\n                            group_columns=[\'Subject\', \'Class\', \'Rep\'],\n                            label_column=\'Class\')\n\n        >>> client.pipeline.add_transform("General Threshold Segmentation",\n                           params={"first_column_of_interest": \'accelx\',\n                                "second_column_of_interest": \'accely\',\n                                "max_segment_length": 5,\n                                "min_segment_length": 5,\n                                "threshold_space_width": 2,\n                                "first_vt_threshold": 0.05,\n                                "first_threshold_space": \'std\',\n                                "first_comparison": \'max\',\n                                "second_vt_threshold": 0.05,\n                                "second_threshold_space": \'std\',\n                                "second_comparison": \'min\',\n                                "return_segment_index": False})\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                      Class  Rep  SegmentID Subject  accelx  accely  accelz\n                0  Crawling    1          0     s01     377     569    4019\n                1  Crawling    1          0     s01     357     594    4051\n                2  Crawling    1          0     s01     333     638    4049\n                3  Crawling    1          0     s01     340     678    4053\n                4  Crawling    1          0     s01     372     708    4051\n                5   Running    1          0     s01     -44   -3971     843\n                6   Running    1          0     s01     -47   -3982     836\n                7   Running    1          0     s01     -43   -3973     832\n                8   Running    1          0     s01     -40   -3973     834\n                9   Running    1          0     s01     -48   -3978     844\n\n\n    ',
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "79c588bb-33e9-496b-a539-dc3c994a2e16",
    name: "Sample By Metadata",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "metadata_name",
        type: "str",
      },
      {
        name: "metadata_values",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Select rows from the input DataFrame based on a metadata column. Rows\n    that have a metadata value that is in the values list will be returned.\n\n    Args:\n        input_data (DataFrame): Input DataFrame.\n        metadata_name (str): Name of the metadata column to use for sampling.\n        metadata_values (list[str]): List of values of the named column for which to\n            select rows of the input data.\n\n    Returns:\n        DataFrame: The input_data DataFrame containing only the rows for which the metadata value is\n        in the accepted list.\n    ",
    type: "Sampler",
    subtype: "Feature Grouping",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "ff7adad0-248e-4db1-90f2-4492491a2726",
    name: "Hierarchical Clustering with Neuron Optimization",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "remove_unknown",
        type: "boolean",
        default: false,
        description:
          "If there is an Unknown label, remove that from the database of patterns prior to saving the model.",
      },
      {
        name: "number_of_neurons",
        type: "int",
        range: [1, 16384],
        default: 32,
        handle_by_set: false,
      },
      {
        name: "linkage_method",
        type: "str",
        default: "average",
        options: [
          {
            name: "average",
          },
          {
            name: "complete",
          },
          {
            name: "ward",
          },
          {
            name: "single",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "centroid_calculation",
        type: "str",
        default: "robust",
        options: [
          {
            name: "robust",
          },
          {
            name: "mean",
          },
          {
            name: "median",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "flip",
        type: "int",
        default: 1,
        handle_by_set: false,
      },
      {
        name: "cluster_method",
        type: "str",
        default: "kmeans",
        options: [
          {
            name: "DHC",
          },
          {
            name: "DLHC",
          },
          {
            name: "kmeans",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "aif_method",
        type: "str",
        default: "max",
        options: [
          {
            name: "min",
          },
          {
            name: "max",
          },
          {
            name: "robust",
          },
          {
            name: "mean",
          },
          {
            name: "median",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "singleton_aif",
        type: "int",
        default: 0,
        handle_by_set: false,
      },
      {
        name: "min_number_of_dominant_vector",
        type: "int",
        range: [1, 20],
        default: 3,
        handle_by_set: false,
      },
      {
        name: "max_number_of_weak_vector",
        type: "int",
        range: [1, 20],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "PME",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [],
    description:
      "\n    Hierarchical Clustering with Neuron Optimization takes as input feature vectors,\n    corresponding class labels, and desired number of patterns, and outputs a model.\n\n    Each pattern in a model consists of a centroid, its class label, and its area of influence\n    (AIF). Each centroid is calculated as an average of objects in the cluster, each class\n    label is the label of the majority class, and each AIF is the distance between the\n    centroid and the farthest object in that cluster.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        number_of_neurons (int): the maximum number of output clusters (neurons) desired\n        linkage_method (str): options are average, complete, ward, and single (default\n            is average)\n        centroid_calculation (str): options are robust, mean, and median (default is\n            robust)\n        flip (int): default is 1\n        cluster_method (str): options are DLCH, DHC, and kmeans (default is DLHC)\n        aif_method (str): options are min, max, robust, mean, median (default is max)\n        singleton_aif (int): default is 0\n        min_number_of_dominant_vector (int) : It is used for pruning. It defines min. number of\n            vector for dominant class in the cluster.\n        max_number_of_weak_vector(int) : It is used for pruning. It defines max. number of\n            vector for weak class in the cluster.\n\n    Returns:\n        one or more models\n\n    ",
    type: "Training Algorithm",
    subtype: "PME",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "8c079a50-bb2b-4796-8501-b1773ea9ecd4",
    name: "Neuron Optimization",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "remove_unknown",
        type: "boolean",
        default: false,
        description:
          "If there is an Unknown label, remove that from the database of patterns prior to saving the model.",
      },
      {
        name: "neuron_range",
        type: "list",
        range: [1, 128],
        default: [5, 30],
        description: "The range of max neurons spaces to serach over specified as [Min, Max]",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
      },
      {
        name: "linkage_method",
        type: "str",
        default: "average",
        options: [
          {
            name: "average",
          },
          {
            name: "complete",
          },
          {
            name: "ward",
          },
          {
            name: "single",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "centroid_calculation",
        type: "str",
        default: "robust",
        options: [
          {
            name: "robust",
          },
          {
            name: "mean",
          },
          {
            name: "median",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "flip",
        type: "int",
        range: [1, 10],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "cluster_method",
        type: "str",
        default: "DLHC",
        options: [
          {
            name: "DHC",
          },
          {
            name: "DLHC",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "aif_method",
        type: "str",
        default: "max",
        options: [
          {
            name: "min",
          },
          {
            name: "max",
          },
          {
            name: "robust",
          },
          {
            name: "mean",
          },
          {
            name: "median",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "singleton_aif",
        type: "int",
        default: 0,
        handle_by_set: false,
      },
      {
        name: "min_number_of_dominant_vector",
        type: "int",
        range: [1, 100],
        default: 3,
        handle_by_set: false,
      },
      {
        name: "max_number_of_weak_vector",
        type: "int",
        range: [1, 100],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "PME",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [],
    description:
      '\n    Neuron Optimization performs an optimized grid search over KNN/RBF and the number of neurons for\n    the parameters of Hierarchical Clustering with Neuron Optimization. Takes as input feature vectors,\n    corresponding class labels and outputs a model.\n\n    Each  pattern in a model consists of a centroid, its class label, and its area of influence (AIF).\n    Each centroid is calculated as an average of objects in the cluster, each class label is the label\n    of the majority class, and each AIF is the distance between the centroid and the farthest object\n    in that cluster.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        neuron_range (list): the range of max neurons spaces to search over specified as [Min, Max]\n        linkage_method (str): options are average, complete, ward, and single (default\n            is average)\n        centroid_calculation (str): options are robust, mean, and median (default is\n            robust)\n        flip (int): default is 1\n        cluster_method (str): options are DLCH, DHC, and kmeans (default is DLHC)\n        aif_method (str): options are min, max, robust, mean, median (default is max)\n        singleton_aif (int): default is 0\n        min_number_of_dominant_vector (int) : It is used for pruning. It defines min. number of\n            vector for dominant class in the cluster.\n        max_number_of_weak_vector(int) : It is used for pruning. It defines max. number of\n            vector for weak class in the cluster.\n\n    Returns:\n        one or more models\n    "description": "."}\n\n\n    return None\n    ',
    type: "Training Algorithm",
    subtype: "PME",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "504991dd-d247-44b4-92eb-d29b2612431c",
    name: "Recall",
    input_contract: [],
    output_contract: [],
    description:
      "\n    The simplest validation method, wherein the training set itself is used as the\n    test set. In other words, for a data set consisting of 100 samples in total, both\n    the training set and the test set consist of the same set of 100 samples.\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "1baeb851-5a4a-4df4-9549-038ae71f0d6a",
    name: "Median",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "\n    The median of a vector V with N items, is the middle value of a sorted\n    copy of V (V_sorted). When N is even, it is the average of the two\n    middle values in V_sorted.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Median',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxMedian  gen_0002_accelyMedian  gen_0003_accelzMedian\n            0     s01                    0.0                    7.0                    6.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "461f62aa-f922-471b-9f4a-902f7b1f608c",
    name: "Load Model PME",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "PME",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "neuron_array",
        type: "list",
        default: [],
        element_type: "dict",
        handle_by_set: false,
      },
      {
        name: "class_map",
        type: "dict",
        default: {},
        handle_by_set: false,
      },
    ],
    output_contract: [],
    description:
      "\n    Load Neuron Array takes an input of feature vectors, corresponding class labels,\n    and a neuron array to use for classification.  The neuron array is loaded and\n    classification is performed.\n\n    Note: This training algorithm does not perform optimizations on the provided neurons.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        neuron_array (list): A list of neurons to load into the hardware simulator.\n        class_map (dict): class map for converting labels to neuron categories.\n\n    Returns:\n        a set of models\n\n    ",
    type: "Training Algorithm",
    subtype: "PME",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "6c7d2227-6600-4a53-affc-e9adaed6ca31",
    name: "Quantize254",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "passthrough_columns",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Scalar quantization of a normalized dataframe to integers between 0 and 254.\n    This step should only be applied after features have been normalized to the\n    range [-1, 1]. This function transfer the `input_data` and `passthrough_columns`\n    from the previous pipeline block. It does not require any feature-specific\n    statistics to be saved to the knowledgepack.\n\n    Returns:\n        dataframe: quantized dataframe\n    ",
    type: "Transform",
    subtype: "Feature Vector",
    has_c_version: true,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "c7782ccb-5bce-4e9c-8555-9bcb4468cefe",
    name: "Double Peak Key Segmentation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        no_display: true,
      },
      {
        name: "column_of_interest",
        type: "str",
        streams: true,
        display_name: "Column Of Interest",
        number_of_elements: 1,
      },
      {
        name: "group_columns",
        type: "list",
        no_display: true,
        element_type: "str",
      },
      {
        name: "last_twist_threshold",
        type: "int16_t",
        c_param: 1,
        default: 15000,
        description: "This will be the threshold for detecting the end of the segment",
        display_name: "last peak threshold",
      },
      {
        name: "twist_threshold",
        type: "int16_t",
        c_param: 2,
        default: -20000,
        description:
          "This will be the threshold for detecting the start of the first and second peaks",
        display_name: "peak threshold",
      },
      {
        name: "end_twist_threshold",
        type: "int16_t",
        c_param: 3,
        default: -1000,
        description:
          "This will be the threshold for detecting the  end of the first and second peaks",
        display_name: "end peak threshold",
      },
      {
        name: "max_segment_length",
        type: "int",
        c_param: 4,
        default: 256,
        description: "Maximum length of a segment that can be identified",
        display_name: "Max Segment Length",
      },
      {
        name: "min_peak_to_peak",
        type: "int",
        c_param: 5,
        default: 10,
        description: "Min number of samples between peak 1 and 2",
        display_name: "Min Peak to Peak Distance",
      },
      {
        name: "max_peak_to_peak",
        type: "int",
        c_param: 6,
        default: 80,
        description: "Max number of samples between peak 1 and 2",
        display_name: "Max Peak to Peak Distance",
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
        description: "Append columns start and stop of the segment index.",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      "\n    Considers a double peak as the key to begin segmentation and a single peak as the end.\n\n    Args:\n        input_data (DataFrame): The input data.\n        column_of_interest (str): The name of the stream to use for segmentation.\n        group_columns (List[str]): A list of column names to use for grouping.\n        return_segment_index (bool): If True, returns the segment indexes for start and end. This should only be used for\n                                     visualization purposes and not for pipeline building.\n        min_peak_to_peak (int): Minimum peak-to-peak distance for a potential double peak.\n        max_peak_to_peak (int): Maximum peak-to-peak distance for a potential double peak.\n        twist_threshold (int): Threshold to detect a first downward slope in a double peak.\n        end_twist_threshold (int): Threshold to detect an upward slope preceding the last peak in a double peak.\n        last_twist_threshold (int): Minimum threshold difference between the last peak and the following minimums.\n        max_segment_length (int): The maximum number of samples a segment can contain. A segment length too large will\n                                  not fit on the device.\n\n    Returns:\n        DataFrame: If return_segment_index is True, returns a dictionary containing the start and\n                                        end indexes of each segment for visualization purposes. Otherwise, returns a DataFrame.\n    ",
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "895e80b3-a2e2-4308-adf6-d5041c161b6c",
    name: "First Derivative",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
      },
    ],
    output_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the first derivative of a single sensor input column.\n\n    Args:\n        input_data: DataFrame\n        input_columns: list of the columns of which to calculate the first derivative\n\n    Returns:\n        The input DataFrame with an additional column containing the integer\n        derivative of the desired input_column\n    ",
    type: "Transform",
    subtype: "Sensor",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "ee0464cb-cf22-42a1-a203-e406d3f9ca40",
    name: "Windowing",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "window_size",
        type: "int",
        range: [1, 16384],
        c_param: 1,
        default: 250,
        description: "The amount of data that will be used to classify the current signal.",
        display_name: "Window Size",
      },
      {
        name: "delta",
        type: "int",
        range: [1, 16384],
        c_param: 2,
        default: 250,
        description:
          "The amount of overlap between this signal and the next. For example if the Window Size is 250 and the slide is 50, the next classification will add 50 new samples to the last 200 samples from the previous window. If Slide is equal to Window Size there will be no overlap.",
        display_name: "Slide",
      },
      {
        name: "train_delta",
        type: "int",
        range: [1, 16384],
        default: 0,
        description:
          "The Training Slide will replace the Slide setting during training, but the Slide will be used when generating the Knowledge Pack. Train slide is useful for data augmentation.",
        display_name: "Training Slide",
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
        description: "Append columns start and stop of the segment index.",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      "\n\n    Args:\n        input_data (_type_): _description_\n        group_columns (_type_): _description_\n        window_size (_type_): _description_\n        delta (_type_): _description_\n        train_delta (int, optional): _description_. Defaults to 0.\n        return_segment_index (bool, optional): _description_. Defaults to False.\n    ",
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "59918065-8a23-4c65-921a-471abcba36b9",
    name: "Load Model TensorFlow Lite for Microcontrollers",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "TensorFlow Lite for Microcontrollers",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "model_parameters",
        type: "dict",
        default: {
          tflite: "",
        },
      },
      {
        name: "estimator_type",
        type: "str",
        default: "classification",
        options: [
          {
            name: "classification",
          },
          {
            name: "regression",
          },
        ],
      },
      {
        name: "class_map",
        type: "dict",
        default: null,
        handle_by_set: false,
      },
      {
        name: "threshold",
        type: "float",
        default: 0,
        handle_by_set: false,
      },
      {
        name: "train_history",
        type: "dict",
        default: null,
        handle_by_set: false,
      },
      {
        name: "model_json",
        type: "dict",
        default: null,
        handle_by_set: false,
      },
      {
        name: "input_type",
        type: "str",
        default: "int8",
        options: [
          {
            name: "int8",
          },
        ],
        description: "use int8 as input. Typically Accelerated OPS require int8.",
      },
    ],
    output_contract: [],
    description:
      "\n    Provides the ability to upload a TensorFlow Lite flatbuffer to use as the final classifier step in a pipeline.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        model_parameters (int): The flatbuffer object of your TensorFlow micro model\n        class_map (dict): class map for converting labels to output\n        estimator_type (str): defines if this estimator performs regression or classification, defaults to classification\n        threshold (float):  if no values are greater than the threshold, classify as Unknown\n        train_history (dict): training history for this model\n        model_json (dict): expects the model json file from the tensorflow api tf_model.to_json()\n\n\n    Example:\n\n        SensiML provides the ability to train and bring your own NN architecture to use as the classifier for your pipeline.\n        This example starts from the point where you have created features using the SensiML Toolkit\n\n            >>> x_train, x_test, x_validate, y_train, y_test, y_validate, class_map =             >>>     client.pipeline.features_to_tensor(fv_t, test=0.0, validate=.1)\n\n        Tensorflow Lite Micro only supports a subset of the full tensorflow functions. For a full list of available functions\n        see the `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.\n        Use the Keras tensorflow API to create the NN graph.\n\n            >>> from tensorflow.keras import layers\n            >>> import tensorflow as tf\n            >>> tf_model = tf.keras.Sequential()\n            >>> tf_model.add(layers.Dense(12, activation='relu',kernel_regularizer='l1', input_shape=(x_train.shape[1],)))\n            >>> tf_model.add(layers.Dropout(0.1))\n            >>> tf_model.add(layers.Dense(8, activation='relu', input_shape=(x_train.shape[1],)))\n            >>> tf_model.add(layers.Dropout(0.1))\n            >>> tf_model.add(layers.Dense(y_train.shape[1], activation='softmax'))\n            >>> tf_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])\n            >>> tf_model.summary()\n            >>> train_history = {'loss':[], 'val_loss':[], 'accuracy':[], 'val_accuracy':[]}\n\n        Train the Tensorflow Model\n\n            >>> epochs=100\n            >>> batch_size=32\n            >>> data  = tf.data.Dataset.from_tensor_slices((x_train, y_train))\n            >>> shuffle_ds = data.shuffle(buffer_size=x_train.shape[0], reshuffle_each_iteration=True).batch(batch_size)\n            >>> history = tf_model.fit( shuffle_ds, epochs=epochs, batch_size=batch_size, validation_data=(x_validate, y_validate), verbose=0)\n            >>> for key in train_history:\n            >>>     train_history[key].extend(history.history[key])\n            >>> import sensiml.tensorflow.utils as sml_tf\n            >>> sml_tf.plot_training_results(tf_model, train_history, x_train, y_train, x_validate, y_validate)\n\n        Qunatize the Tensorflow Model\n\n        *   The ```representative_dataset_generator()``` function is necessary to provide statistical information about your dataset in order to quantize the model weights appropriatley.\n        *   The TFLiteConverter is used to convert a tensorflow model into a TensorFlow Lite model. The TensorFlow Lite model is stored as a `flatbuffer <https://google.github.io/flatbuffers/>`_ which allows us to easily store and access it on embedded systems.\n        *   Quantizing the model allows TensorFlow Lite micro to take advantage of specialized instructions on cortex-M class processors using the `cmsis-nn <http://www.keil.com/pack/doc/cmsis/NN/html/index.html>`_ DSP library which gives another huge boost in performance.\n        *   Quantizing the model can reduce size by up to 4x as 4 byte floats are converted to 1 byte ints in a number of places within the model.\n\n            >>> import numpy as np\n            >>> def representative_dataset_generator():\n            >>>     for value in x_validate:\n            >>>     # Each scalar value must be inside of a 2D array that is wrapped in a list\n            >>>         yield [np.array(value, dtype=np.float32, ndmin=2)]\n            >>>\n            >>> converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)\n            >>> converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]\n            >>> converter.representative_dataset = representative_dataset_generator\n            >>> tflite_model_quant = converter.convert()\n\n        Uploading Trained TF Lite model to SensiML\n\n            >>> class_map_tmp = {k:v+1 for k,v in class_map.items()} #increment by 1 as 0 corresponds to unknown\n            >>> client.pipeline.set_training_algorithm(\"Load Model TensorFlow Lite for Microcontrollers\",\n            >>>                                     params={\"model_parameters\": {\n            >>>                                             'tflite': sml_tf.convert_tf_lite(tflite_model_quant)},\n            >>>                                             \"class_map\": class_map_tmp,\n            >>>                                             \"estimator_type\": \"classification\",\n            >>>                                             \"threshold\": 0.0,\n            >>>                                             \"train_history\":train_history,\n            >>>                                             \"model_json\": tf_model.to_json()\n            >>>                                             })\n            >>> client.pipeline.set_validation_method(\"Recall\", params={})\n            >>> client.pipeline.set_classifier(\"TensorFlow Lite for Microcontrollers\", params={})\n            >>> client.pipeline.set_tvo()\n            >>> results, stats = client.pipeline.execute()\n            >>>\n            >>> results.summarize()\n\n    ",
    type: "Training Algorithm",
    subtype: "Load",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "a52f6c8f-ab5e-4ecb-9ba8-66c4fcc9e232",
    name: "Bonsai Tree Optimizer",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "Bonsai",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "projection_dimension",
        type: "int",
        range: [1, 50],
        default: 10,
        handle_by_set: false,
      },
      {
        name: "tree_depth",
        type: "int",
        range: [2, 10],
        default: 4,
        handle_by_set: false,
      },
      {
        name: "sigma",
        type: "float",
        range: [0.001, 10],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "epochs",
        type: "int",
        range: [1, 2000],
        default: 100,
        handle_by_set: false,
      },
      {
        name: "batch_size",
        type: "int",
        range: [1, 100],
        default: 25,
        handle_by_set: false,
      },
      {
        name: "reg_W",
        type: "float",
        range: [0.0001, 1],
        default: 0.001,
        handle_by_set: false,
      },
      {
        name: "reg_V",
        type: "float",
        range: [0.0001, 1],
        default: 0.001,
        handle_by_set: false,
      },
      {
        name: "reg_Theta",
        type: "float",
        range: [0.0001, 1],
        default: 0.001,
        handle_by_set: false,
      },
      {
        name: "reg_Z",
        type: "float",
        range: [0.0001, 1],
        default: 0.0001,
        handle_by_set: false,
      },
      {
        name: "sparse_V",
        type: "float",
        range: [0, 1],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "sparse_Theta",
        type: "float",
        range: [0, 1],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "sparse_W",
        type: "float",
        range: [0, 1],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "sparse_Z",
        type: "float",
        range: [0, 1],
        default: 1,
        handle_by_set: false,
      },
      {
        name: "learning_rate",
        type: "int",
        range: [0.0001, 0.1],
        default: 0.001,
        handle_by_set: false,
      },
    ],
    output_contract: [],
    description:
      "\n    Train a Bonsais Tree Classifier using backpropagation.\n\n    For detailed information see the `ICML 2017 Paper <https://github.com/Microsoft/EdgeML/wiki/files/BonsaiPaper.pdf>`_\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        epochs (str): The number of training epochs to iterate over\n        batch_size (float): The size of batches to use during training\n        learning_rate (float): The learning rate for training optimization\n        project_dimensions (int): The number of dimensions to project the input feature space into\n        sigma (float): tunable hyperparameter\n        reg_W (float): regularization for W matrix\n        reg_V (float): regularization for V matrix\n        reg_Theta (float): regularization for Theta matrix\n        reg_Z (float): regularization for Z matrix\n        sparse_V (float): sparcity factor for V matrix\n        sparse_Theta (float): sparcity factor for Theta matrix\n        sparse_W (float): sparcity factor for W matrix\n        sparse_Z (float): sparcity factor fo Z matrix\n\n\n    Returns:\n        model parameters for a bonsai tree classifier\n\n    ",
    type: "Training Algorithm",
    subtype: "Bonsai",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "fc013141-ccd8-4838-98e9-fd2466d542a3",
    name: "Stratified K-Fold Cross-Validation",
    input_contract: [
      {
        name: "number_of_folds",
        type: "int",
        range: [2, 5],
        default: 3,
      },
      {
        name: "test_size",
        type: "float",
        range: [0, 0.4],
        default: 0,
      },
      {
        name: "shuffle",
        type: "bool",
        default: true,
      },
    ],
    output_contract: [],
    description:
      "\n    A variation of k-fold which returns stratified folds: each set contains approximately the\n    same percentage of samples of each target class as the complete set. In other words, for a\n    data set consisting of total 100 samples with 40 samples from class 1 and 60 samples from\n    class 2, for a stratified 2-fold scheme, each fold will consist of total 50 samples with 20\n    samples from class 1 and 30 samples from class 2.\n\n    Args:\n        number_of_folds (int): the number of stratified folds to produce\n        test_size (float): the percentage of data to hold out as a final test set\n        shuffle (bool): Specifies whether or not to shuffle the data before performing the\n            cross-fold validation splits.\n\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b9017fce-a93e-4cb7-9c6f-76caa6822fe5",
    name: "xGBoost",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "Boosted Tree Ensemble",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "max_depth",
        type: "int",
        default: 5,
        handle_by_set: false,
      },
      {
        name: "n_estimators",
        type: "int",
        default: 25,
        handle_by_set: false,
      },
    ],
    output_contract: [],
    description:
      "\n    Train an ensemble of boosted tree classifiers using the xGBoost training algorithm.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        max_depth (int): The max depth to allow a decision tree to reach\n        n_estimators (int): The number of decision trees to build.\n\n    Returns:\n        a trained model\n\n    ",
    type: "Training Algorithm",
    subtype: "Boosted Tree Ensemble",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "a68de605-c556-4b7f-8615-4f6af76ddebc",
    name: "Random Forest",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "Decision Tree Ensemble",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "max_depth",
        type: "int",
        default: 5,
        handle_by_set: false,
      },
      {
        name: "n_estimators",
        type: "int",
        default: 25,
        handle_by_set: false,
      },
    ],
    output_contract: [],
    description:
      "\n    Train an ensemble of decision tree classifiers using the random forest training algorithm. A random forest is\n    a meta estimator that fits a number of decision tree classifiers on various sub-samples of the dataset and\n    uses averaging to improve the predictive accuracy and control overfitting. The sub-sample size is always\n    the same as the original input sample size but the samples are drawn with replacement\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        max_depth (int): The max depth to allow a decision tree to reach\n        n_estimators (int): The number of decision trees to build.\n\n    Returns:\n        a set of models\n\n    ",
    type: "Training Algorithm",
    subtype: "Decision Tree Ensemble",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "46a37652-1e88-4a3d-b566-7cf4d48c28bb",
    name: "Absolute Mean",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the arithmetic mean of absolute value in each column of `columns` in the dataframe.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Absolute Mean',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxAbsMean  gen_0002_accelyAbsMean  gen_0003_accelzAbsMean\n            0     s01                     2.0                     7.2                     5.8\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "a2a89056-00cc-4beb-b197-fad3cbdc9fb9",
    name: "MFE",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Column on which to apply the feature generator",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "num_filters",
        type: "int",
        range: [1, 23],
        c_param: 0,
        default: 23,
        description: "The number of mel filter bank values to return.",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "params['num_filters']",
        scratch_buffer: {
          type: "fixed_value",
          value: 512,
        },
      },
    ],
    description:
      "\n    Translates the data stream(s) from a segment into a feature vector of Mel-Frequency Energy (MFE).\n    The power spectrum of each frame of audio is passed through a filterbank of triangular filters\n    which are spaced uniformly in the mel-frequency domain.\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (list of strings): Names of the sensor streams to use.\n        num_filters (int): Number of filters for the mel-scale filterbank.\n\n    Returns:\n        DataFrame: Feature vector of MFE coefficients.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'MFE', 'params':{\"columns\": ['accelx'],\n                                                              \"num_filters\": 23 }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxmfe_000000  gen_0001_accelxmfe_000001 ... gen_0001_accelxmfe_000021  gen_0001_accelxmfe_000022\n            0     s01                    131357.0                    -46599.0 ...                      944.0                       308.0\n\n    ",
    type: "Feature Generator",
    subtype: "Frequency",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "1d24719f-40e7-40d5-abbb-fb965c4f0a69",
    name: "Total Area",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Total area under the signal. Total area = sum(signal(t)*dt), where\n    signal(t) is signal value at time t, and dt is sampling time (dt = 1/sample_rate).\n\n    Args:\n        sample_rate: Sampling rate of the signal\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n\n        >>> client.pipeline.add_feature_generator([{'name':'Total Area',\n                                     'params':{\"sample_rate\": 10,\n                                               \"columns\": ['accelx','accely','accelz']\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen0001_accelxTotArea  gen_0002_accelyTotArea  gen_0003_accelzTotArea\n            0     s01                    0.0                     3.6                     2.9\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "db7330db-2d02-4848-9e14-223677a5d800",
    name: "Absolute Area",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Absolute area of the signal. Absolute area = sum(abs(signal(t)) dt), where\n    `abs(signal(t))` is absolute signal value at time t, and dt is sampling time (dt = 1/sample_rate).\n\n    Args:\n        sample_rate: Sampling rate of the signal\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'],\n                                               \"sample_rate\": 10 }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxAbsArea  gen_0002_accelyAbsArea  gen_0003_accelzAbsArea\n            0     s01                     1.0                     3.6                     2.9\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "3bd70e49-a685-47b3-8dc1-f0d52ea51f6e",
    name: "Total Area of Low Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 50],
        c_param: 1,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Total area of low frequency components of the signal. It calculates total area\n    by first applying a moving average filter on the signal with a smoothing factor.\n\n    Args:\n        sample_rate: float; Sampling rate of the signal\n        smoothing_factor (int); Determines the amount of attenuation for\n                          frequencies over the cutoff frequency.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Total Area of Low Frequency',\n                                     'params':{\"sample_rate\": 10,\n                                               \"smoothing_factor\": 5,\n                                               \"columns\": ['accelx','accely','accelz']\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxTotAreaDc  gen_0002_accelyTotAreaDc  gen_0003_accelzTotAreaDc\n            0     s01                       0.0                      0.72                      0.58\n\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e4416c26-e513-4f51-beea-9166b6559acc",
    name: "Absolute Area of Low Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "sample_rate",
        type: "numeric",
        range: [1, 100000],
        c_param: 0,
        default: 100,
        description: "Sample rate of the sensor data",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 50],
        c_param: 1,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Absolute area of low frequency components of the signal. It calculates absolute area\n    by first applying a moving average filter on the signal with a smoothing factor.\n\n    Args:\n        sample_rate: float; Sampling rate of the signal\n        smoothing_factor (int); Determines the amount of attenuation for frequencies\n                         over the cutoff frequency.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'Absolute Area of Spectrum',\n                                     'params':{\"sample_rate\": 10,\n                                               \"columns\": ['accelx','accely','accelz']\n                                              }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxAbsAreaSpec  gen_0002_accelyAbsAreaSpec  gen_0003_accelzAbsAreaSpec\n            0     s01                       260.0                      2660.0                      1830.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Area",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "88aa51ea-21e4-11ed-861d-0242ac120002",
    name: "Feature Selector By Family",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "max_number_generators",
        type: "int",
        range: [0, 24],
        default: 5,
        description: "Maximum number of feature generators to keep",
      },
      {
        name: "generators",
        type: "list",
        default: null,
        description: "Number of generator groups to keep",
        element_type: "dict",
      },
      {
        name: "random_seed",
        type: "int",
        default: null,
        description: "seed to initialize the random state",
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "List of non sensor columns",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      '\n    This is an unsupervised method of feature selection. The goal is to randomly select features from the specified\n    feature generators until the maximum number of generators given as input is reached. If no specific generator is\n    provided, all feature generators have an equal chance to be selected.\n\n    Args:\n        input_data (DataFrame): Input data to perform feature selection on.\n        generators (List[Dict[str, Union[str, int]]]): A list of feature generators to select from. Each member of\n            this list is a dictionary of this form:\n            {"generator_names": [(str)] or (str), "number": (int)},\n            where "generator_names" lists the name(s) of the generator(s) to select from, and "number" is the desired\n            number of generators.\n        max_number_generators (int): [Default 5] The maximum number of feature generators to keep.\n        random_seed (int): [Optional] Random initialization seed.\n        passthrough_columns (List[str]): [Optional] A list of columns to include in the output DataFrame in addition\n            to the selected features.\n        **kwargs: Additional keyword arguments to pass.\n\n    Returns:\n        Tuple[DataFrame, List[str]]: A tuple containing a DataFrame that includes the selected features and the\n        passthrough columns and a list containing the unselected feature columns.\n\n    Examples:\n        >>> client.project  = <project_name>\n        >>> client.pipeline = <piepline_name>\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data(\'test_data\',\n                                     data_columns = [\'accelx\', \'accely\', \'accelz\', \'gyrox\', \'gyroy\', \'gyroz\'],\n                                     group_columns = [\'Subject\',\'Class\', \'Rep\'],\n                                     label_column = \'Class\')\n        >>> client.pipeline.add_feature_generator([\n                    {\n                        "name": "MFCC",\n                        "params": {\n                            "columns": ["accelx"],\n                            "sample_rate": 10,\n                            "cepstra_count": 3,\n                        },\n                    },\n                    {\n                        "name": "Downsample",\n                        "params": {"columns": ["accelx", "accely", "accelz"], "new_length": 3},\n                    },\n                    {\n                        "name": "MFCC",\n                        "params": {\n                            "columns": ["accely"],\n                            "sample_rate": 10,\n                            "cepstra_count": 4,\n                        },\n                    },\n                    {\n                        "name": "Power Spectrum",\n                        "params": {\n                            "columns": ["accelx"],\n                            "number_of_bins": 5,\n                            "window_type": "hanning",\n                        },\n                    },\n                    {\n                        "name": "Absolute Area",\n                        "params": {\n                            "sample_rate": 10,\n                            "columns": ["accelx", "accelz"],\n                        },\n                    },\n                ])\n        >>>\n        >>> results, stats = client.pipeline.execute()\n\n        >>> results.columns.tolist()\n            # List of all features before the feature selection algorithm\n            Out:\n            [\'gen_0001_accelxmfcc_000000\',\n            \'gen_0001_accelxmfcc_000001\',\n            \'gen_0001_accelxmfcc_000002\',\n            \'Class\',\n            \'Rep\',\n            \'Subject\',\n            \'gen_0002_accelxDownsample_0\',\n            \'gen_0002_accelxDownsample_1\',\n            \'gen_0002_accelxDownsample_2\',\n            \'gen_0003_accelyDownsample_0\',\n            \'gen_0003_accelyDownsample_1\',\n            \'gen_0003_accelyDownsample_2\',\n            \'gen_0004_accelzDownsample_0\',\n            \'gen_0004_accelzDownsample_1\',\n            \'gen_0004_accelzDownsample_2\',\n            \'gen_0005_accelymfcc_000000\',\n            \'gen_0005_accelymfcc_000001\',\n            \'gen_0005_accelymfcc_000002\',\n            \'gen_0005_accelymfcc_000003\',\n            \'gen_0006_accelxPowerSpec_000000\',\n            \'gen_0006_accelxPowerSpec_000001\',\n            \'gen_0006_accelxPowerSpec_000002\',\n            \'gen_0006_accelxPowerSpec_000003\',\n            \'gen_0006_accelxPowerSpec_000004\',\n            \'gen_0007_accelxAbsArea\',\n            \'gen_0008_accelzAbsArea\']\n\n        Here, feature selector picks upto 5 feature generators, of which 2 could be from the "Downsample" generator\n        and 2 of them could be either "MFCC" or "Power Spectrum" feature and the rest could be any other feature\n        not listed in any of the "generator_names" lists.\n\n        >>> client.pipeline.add_feature_selector([{"name": "Feature Selector By Family",\n                                                "params":{\n                                                    "max_number_generators": 5,\n                                                    "seed": 1,\n                                                    "generators":[\n                                                    {\n                                                        "generator_names": "Downsample",\n                                                        "number": 2\n                                                    },\n                                                    {\n                                                        "generator_names": ["MFCC", "Power Spectrum"],\n                                                        "number": 2\n                                                    }]\n                                            }}])\n\n        >>> results, stats = client.pipeline.execute()\n\n        >>> results.columns.tolist()\n            # List of all features after the feature selection algorithm\n            # Because of the random nature of this selector function, the output might be\n            # slightly different each time based on the chosen seed\n            Out:\n            [\'Class\',\n            \'Rep\',\n            \'Subject\',\n            \'gen_0003_accelyDownsample_0\',\n            \'gen_0003_accelyDownsample_1\',\n            \'gen_0003_accelyDownsample_2\',\n            \'gen_0002_accelxDownsample_0\',\n            \'gen_0002_accelxDownsample_1\',\n            \'gen_0002_accelxDownsample_2\',\n            \'gen_0005_accelymfcc_000000\',\n            \'gen_0005_accelymfcc_000001\',\n            \'gen_0005_accelymfcc_000002\',\n            \'gen_0005_accelymfcc_000003\',\n            \'gen_0001_accelxmfcc_000000\',\n            \'gen_0001_accelxmfcc_000001\',\n            \'gen_0001_accelxmfcc_000002\',\n            \'gen_0008_accelzAbsArea\']\n\n    ',
    type: "Feature Selector",
    subtype: "Unsupervised",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "c200e1e5-a0bf-421f-963d-49382d24eb01",
    name: "Normalize",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "passthrough_columns",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Scale each feature vector to between -1 and 1 by dividing each feature\n    in a feature vector by the absolute maximum value in that feature vector.\n\n    This function transfer the `input_data` and `passthrough_columns` from the previous pipeline block.\n\n    Returns:\n        dataframe: Normalized dataframe\n\n    Examples:\n        >>> from pandas import DataFrame\n        >>> df = DataFrame([[3, 3], [4, 5], [5, 7], [4, 6], [3, 1],\n                    [3, 1], [4, 3], [5, 5], [4, 7], [3, 6]],\n                    columns=['accelx', 'accely'])\n        >>> df['Subject'] = 's01'\n        >>> df['Rep'] = [0] * 5 + [1] * 5\n        >>> df\n            Out:\n               accelx  accely Subject  Rep\n            0       3       3     s01    0\n            1       4       5     s01    0\n            2       5       7     s01    0\n            3       4       6     s01    0\n            4       3       1     s01    0\n            5       3       1     s01    1\n            6       4       3     s01    1\n            7       5       5     s01    1\n            8       4       7     s01    1\n            9       3       6     s01    1\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('testn', df, data_columns=['accelx', 'accely'], group_columns=['Subject','Rep'])\n        >>> client.pipeline.add_transform('Normalize')\n        >>> r, s = client.pipeline.execute()\n        >>> r\n            Out:\n                  Rep Subject  accelx    accely\n                    0   0   s01 1.000000    1.000000\n                    1   0   s01 0.800000    1.000000\n                    2   0   s01 0.714286    1.000000\n                    3   0   s01 0.666667    1.000000\n                    4   0   s01 1.000000    0.333333\n                    5   1   s01 1.000000    0.333333\n                    6   1   s01 1.000000    0.750000\n                    7   1   s01 1.000000    1.000000\n                    8   1   s01 0.571429    1.000000\n                    9   1   s01 0.500000    1.000000\n\n\n    ",
    type: "Transform",
    subtype: "Feature Vector",
    has_c_version: true,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "069e9c7b-ab5e-442b-b2c6-853cb08d9a42",
    name: "Feature Cascade",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "group_columns",
        type: "list",
      },
      {
        name: "num_cascades",
        type: "int",
        range: [1, 100],
        default: 1,
        description:
          "The number of consecutive segments of data that will be combined to produce a final feature vector",
      },
      {
        name: "slide",
        type: "boolean",
        default: true,
        description:
          "When slide is True, classifications will be continuously created with each new feature cascade. The Slide setting will be used when generating the Knowledge Pack. When Slide is False, all features banks will be discarded after any classification made by the Knowledge Pack.",
      },
      {
        name: "training_slide",
        type: "boolean",
        default: true,
        description:
          "When Training Slide is True, feature vectors will be successively generated with each new feature cascade. Training Slide is often used for data augmentation during the training process, specially when the data size is small.",
      },
      {
        name: "training_delta",
        type: "int",
        range: [1, 100],
        default: null,
        depends_on: [
          {
            how: "less_than",
            name: "train_slide",
          },
        ],
        description:
          "When Training Slide is True, the delta value is how much to slide after creating a segment.",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
        metadata_columns: ["CascadeID"],
      },
    ],
    description:
      "\n    Flattens feature vectors over a specified number of segments.\n\n    Args:\n        input_data (DataFrame): The input dataset.\n        feature_table (DataFrame): The feature table to be used for flattening the input data.\n        group_columns (List[str]): The list of columns used for grouping data.\n        num_cascades (int): The number of cascaded windows to cover.\n        slide (bool): If True, after creating first vector, slide and create another vector until all possible cascades\n                      for this segment are created. This parameter is only used when creating a Knowledge Pack.\n        training_slide (bool): If True, similar to slide, but it is used during the training process for data augmentation\n                               purposes when available data size is rather small.\n        training_delta (Optional[int]): If provided, it specifies the offset between the beginning of each cascade during\n                                        training mode.\n\n    Returns:\n        DataFrame: A DataFrame of feature vectors.\n    ",
    type: "Transform",
    subtype: "Feature Vector",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "2d2545a6-9bfd-4d77-b098-875cc19954d2",
    name: "Magnitude",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "Magnitude",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the magnitude (square sum) of a signal across the input_columns\n    streams.\n\n    Args:\n        input_columns (list[str]): sensor streams to use in computing the magnitude\n\n    Returns:\n        The input DataFrame with an additional column containing the per-sample\n        magnitude of the desired input_columns\n    ",
    type: "Transform",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "d5aa5f41-1038-4475-951f-cf2b5066699d",
    name: "Sensor Absolute Average",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
    ],
    output_contract: [
      {
        name: "AbsAverage",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the absolute average of a signal across the input_columns\n    streams.\n\n    Args:\n        input_data: DataFrame containing the time series data\n        input_columns: sensor streams to use in computing the magnitude\n\n    Returns:\n        The input DataFrame with an additional column containing the per-sample\n        absolute average of the desired input_columns\n    ",
    type: "Transform",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e991c17e-1857-4cb2-a3d1-079b03450d8c",
    name: "Tree-based Selection",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "number_of_features",
        type: "int",
        default: 10,
        description: "The number of features you would like the selector to reduce to",
        handle_by_set: false,
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "The set of columns the selector should ignore",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Select features using a supervised tree-based algorithm. This class implements a meta estimator that fits a number of randomized decision trees\n    (a.k.a. extra-trees) on various sub-samples of the dataset and use averaging to improve the predictive accuracy and control overfitting.\n    The default number of trees in the forest is set at 250, and the `random_state` to be 0. Please see notes for more information.\n\n    Args:\n        input_data (DataFrame): Input data.\n        label_column (str): Label column of input data.\n        number_of_features (int): The number of features you would like the selector to reduce to.\n        passthrough_columns (list, optional): A list of columns to include in the output dataframe in addition to the selected features. Defaults to None.\n\n    Returns:\n        tuple: A tuple containing:\n            - selected_features (DataFrame): DataFrame which includes selected features and the passthrough columns for each class.\n            - unselected_features (list): A list of unselected features.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', results, force=True,\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_selector([{'name':'Tree-based Selection', 'params':{ \"number_of_features\": 4 }}] )\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            Out:\n                  Class Subject  gen_0002_accely_0  gen_0002_accely_1  gen_0002_accely_2  gen_0002_accely_3  gen_0002_accely_4  gen_0003_accelz_0  gen_0003_accelz_1  gen_0003_accelz_2  gen_0003_accelz_3  gen_0003_accelz_4\n            0  Crawling     s01           1.669203           1.559860           1.526786           1.414068           1.413625           1.360500           1.368615           1.413445           1.426949           1.400083\n            1  Crawling     s02           1.486925           1.418474           1.377726           1.414068           1.413625           1.360500           1.368615           1.388456           1.408576           1.397417\n            2  Crawling     s03           1.035519           1.252789           1.332684           1.328587           1.324469           1.410274           1.414961           1.384032           1.345107           1.393088\n            3   Running     s01          -0.700995          -0.678448          -0.706631          -0.674960          -0.713493          -0.572269          -0.600986          -0.582678          -0.560071          -0.615270\n            4   Running     s02          -0.659030          -0.709012          -0.678594          -0.688869          -0.700753          -0.494247          -0.458891          -0.471897          -0.475010          -0.467597\n            5   Running     s03          -0.712790          -0.713026          -0.740177          -0.728651          -0.733076          -0.836257          -0.835071          -0.868028          -0.855081          -0.842161\n            6   Walking     s01          -0.701450          -0.714677          -0.692671          -0.716556          -0.696635          -0.652326          -0.651784          -0.640956          -0.655958          -0.643802\n            7   Walking     s02          -0.698335          -0.689857          -0.696807          -0.702233          -0.682212          -0.551928          -0.590001          -0.570077          -0.558563          -0.576008\n            8   Walking     s03          -0.719046          -0.726102          -0.722315          -0.727506          -0.712461          -1.077342          -1.052320          -1.052297          -1.075949          -1.045750\n\n    Notes:\n        For more information, please see: http://scikit-learn.org/stable/modules/generated/sklearn.ensemble.ExtraTreesClassifier.html\n\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "8c5b0667-d0ed-4aba-9799-f7ca4533a77e",
    name: "Information Gain",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
        description: "Name of the label column",
        handle_by_set: true,
      },
      {
        name: "feature_number",
        type: "int",
        default: 2,
        description: "Number of features will be selected for each class",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This is a supervised feature selection algorithm that selects features based on Information Gain (one class vs other\n    classes approaches).\n\n    First, it calculates Information Gain (IG) for each class separately to all features then sort features based on IG\n    scores, std and mean differences. Feature with higher IG is a better feature to differentiate the class from others. At the end, each feature\n    has their own feature list.\n\n    Args:\n        input_data (DataFrame): Input data.\n        label_column (str): The label column in the input_data.\n        feature_number (int): [Default 2] Number of features to select for each class.\n        passthrough_columns (list): [Optional] A list of columns to include in the output DataFrame in addition to\n            the selected features.\n        **kwargs: Additional keyword arguments.\n\n    Returns:\n        Tuple[DataFrame, list]: A tuple containing the selected features and the passthrough columns as a DataFrame, and a list\n        of unselected features.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', results, force=True,\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_selector([{'name':'Information Gain',\n                                    'params':{\"feature_number\": 3}}])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            Out:\n                  Class Subject  gen_0001_accelx_0  gen_0001_accelx_1  gen_0001_accelx_2\n            0  Crawling     s01         347.881775         372.258789         208.341858\n            1  Crawling     s02         347.713013         224.231735          91.971481\n            2  Crawling     s03         545.664429         503.276642         200.263031\n            3   Running     s01         -21.588972         -23.511278         -16.322056\n            4   Running     s02         422.405182         453.950897         431.893585\n            5   Running     s03         350.105774         366.373627         360.777466\n            6   Walking     s01         -10.362945         -46.967007           0.492386\n            7   Walking     s02         375.751343         413.259460         374.443237\n            8   Walking     s03         353.421906         317.618164         283.627502\n\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "d1b6b0c9-c935-42fb-8349-1737192f9c66",
    name: "Metadata k-fold",
    input_contract: [
      {
        name: "number_of_folds",
        type: "int",
        range: [2, 5],
        default: 3,
      },
      {
        name: "metadata_name",
        type: "str",
        default: "",
      },
    ],
    output_contract: [],
    description:
      "\n    K-fold iterator variant with non-overlapping metadata groups.\n    The same group will not appear in two different folds (the number of\n    distinct groups has to be at least equal to the number of folds).\n    The folds are approximately balanced in the sense that the number of\n    distinct groups is approximately the same in each fold.\n\n\n    Args:\n        number_of_folds (int): the number of stratified folds to produce\n        metadata_name (str): the metadata to group on for splitting data into folds.\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "220b89c7-67c5-4a4d-8c5e-8954b9974659",
    name: "Second Derivative",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
      },
    ],
    output_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the second derivative of a single sensor input column.\n\n    Args:\n        input_data: DataFrame\n        input_column: list of the columns of which to calculate the second derivative\n\n    Returns:\n        The input DataFrame with an additional column containing the integer\n        second derivative of the desired input_column.\n    ",
    type: "Transform",
    subtype: "Sensor",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "a6bb2350-4ee0-4096-8528-ee9a74a58476",
    name: "High Pass Filter",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "alpha",
        type: "float",
        range: [0, 1],
        c_param: 0,
        default: 0.9,
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This is a simple IIR Filter that is useful for removing drift from sensors by subtracting the attentuated running average.\n\n    .. math::\n        y_{i}= y_{i-1} + \\alpha (x_{i} - y_{i-1})\n\n    Args:\n        input_data: DataFrame containing the time series data\n        input_columns: sensor streams to apply  the filter to\n        alpha: attenuation coefficient\n\n    Returns:\n        input data after having been passed through the IIR filter\n    ",
    type: "Transform",
    subtype: "Sensor Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c87b87bc-c930-4d1c-94ff-7104d6d2c557",
    name: "Custom Feature Selection",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "custom_feature_selection",
        type: "list",
        description: "List of features to keep",
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "List of non sensor columns",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This is a feature selection method which allows custom feature selection. This takes a list of strings where each\n    value is the feature name to keep.\n\n    Args:\n        input_data: DataFrame, input data\n        custom_feature_selection: list, feature generator names to keep\n        passthrough_columns: list, columns to pass through without modification\n        **kwargs: additional keyword arguments\n\n    Returns:\n        tuple: tuple containing:\n            selected_features: DataFrame, which includes selected features and the passthrough columns.\n            unselected_features: list, unselected features\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "323ea9a0-b6bb-4d4e-b6c8-9b026a85c28d",
    name: "Univariate Selection",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "number_of_features",
        type: "int",
        default: 1,
        description: "The number of     features you would like the selector to reduce to",
        handle_by_set: false,
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "The set of columns the selector should ignore",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Univariate feature selection using ANOVA (Analysis of Variance) is a statistical method used to identify the most\n    relevant features in a dataset by analyzing the variance between different groups. It is a supervised method of\n    feature selection, which means that it requires labeled data.\n\n    The ANOVA test calculates the F-value for each feature by comparing the variance within each class to the variance\n    between classes. The higher the F-value, the more significant the feature is in differentiating between the classes.\n    Univariate feature selection selects the top k features with the highest F-values, where k is a specified parameter.\n\n    Args:\n        input_data (DataFrame): Input data\n        label_column (str): Label column name\n        number_of_features (int): The number of features you would like the selector to reduce to.\n        passthrough_columns (Optional[list], optional): List of columns to pass through. Defaults to None.\n\n    Returns:\n        tuple: Tuple containing:\n            - DataFrame: DataFrame which includes selected features and the passthrough columns.\n            - list: List of unselected features.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all features before the feature selection algorithm\n        >>> results.columns.tolist()\n            Out:\n            [u'Class',\n             u'Subject',\n             u'gen_0001_accelx_0',\n             u'gen_0001_accelx_1',\n             u'gen_0001_accelx_2',\n             u'gen_0001_accelx_3',\n             u'gen_0001_accelx_4',\n             u'gen_0002_accely_0',\n             u'gen_0002_accely_1',\n             u'gen_0002_accely_2',\n             u'gen_0002_accely_3',\n             u'gen_0002_accely_4',\n             u'gen_0003_accelz_0',\n             u'gen_0003_accelz_1',\n             u'gen_0003_accelz_2',\n             u'gen_0003_accelz_3',\n             u'gen_0003_accelz_4']\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', results, force=True,\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_selector([{'name':'Univariate Selection',\n                            'params': {\"number_of_features\": 3 } }])\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print results\n            Out:\n                  Class Subject  gen_0002_accely_2  gen_0002_accely_3  gen_0002_accely_4\n            0  Crawling     s01           1.526786           1.496120           1.500535\n            1  Crawling     s02           1.377726           1.414068           1.413625\n            2  Crawling     s03           1.332684           1.328587           1.324469\n            3   Running     s01          -0.706631          -0.674960          -0.713493\n            4   Running     s02          -0.678594          -0.688869          -0.700753\n            5   Running     s03          -0.740177          -0.728651          -0.733076\n            6   Walking     s01          -0.692671          -0.716556          -0.696635\n            7   Walking     s02          -0.696807          -0.702233          -0.682212\n            8   Walking     s03          -0.722315          -0.727506          -0.712461\n\n    Notes:\n        Please see the following for more information:\n        http://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.SelectKBest.html\n        http://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.f_classif.html#sklearn.feature_selection.f_classif\n\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "d5491aa2-379c-4488-aec7-64a6b2fe66d5",
    name: "Segment Filter MSE",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "input_column",
        type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "MSE_target",
        type: "int",
        range: [-32768, 32767],
        c_param: 0,
        default: 0,
      },
      {
        name: "MSE_threshold",
        type: "int",
        range: [-32768, 32767],
        c_param: 1,
        default: 10,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Filters out groups that do not pass the MSE threshold.\n\n    Args:\n        input_column (str): The name of the column to use for filtering.\n        MSE_target (float): The filter target value. Default is -1.0.\n        MSE_threshold (float): The filter threshold value. Default is 0.01.\n\n    Returns:\n        DataFrame: The filtered input data.\n    ",
    type: "Transform",
    subtype: "Segment Filter",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "1e563312-2fb2-453f-a806-5f346884b0cd",
    name: "Iterate Neural Network",
    input_contract: [
      {
        name: "base_model",
        type: "str",
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "TensorFlow Lite for Microcontrollers",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "class_map",
        type: "dict",
        default: null,
        handle_by_set: true,
      },
      {
        name: "epochs",
        type: "int",
        range: [1, 100],
        default: 5,
      },
      {
        name: "batch_size",
        type: "int",
        range: [8, 128],
        default: 32,
      },
      {
        name: "threshold",
        type: "float",
        range: [0, 1],
        default: 0.8,
        description: "Threshold value below which the classification will return Unknown.",
      },
      {
        name: "early_stopping_threshold",
        type: "float",
        range: [0.5, 1],
        default: 0.8,
        description:
          "Early stopping threshold to stop training when the validation accuracy stops improving.",
      },
      {
        name: "early_stopping_patience",
        type: "int",
        range: [0, 5],
        default: 2,
        description:
          "The number of epochs after the early stopping threshold was reached to continue training.",
      },
      {
        name: "loss_function",
        type: "str",
        default: "categorical_crossentropy",
        options: [
          {
            name: "categorical_crossentropy",
          },
          {
            name: "binary_crossentropy",
          },
          {
            name: "poisson",
          },
          {
            name: "kl_divergence",
          },
        ],
      },
      {
        name: "learning_rate",
        type: "float",
        range: [0, 0.2],
        default: 0.01,
        description: "The learning rate to apply during training",
      },
      {
        name: "tensorflow_optimizer",
        type: "str",
        default: "adam",
        options: [
          {
            name: "adam",
          },
          {
            name: "SGD",
          },
        ],
      },
      {
        name: "metrics",
        type: "str",
        default: "accuracy",
        options: [
          {
            name: "accuracy",
          },
        ],
        description: "The metric reported during the training.",
      },
      {
        name: "input_type",
        type: "str",
        default: "int8",
        options: [
          {
            name: "int8",
          },
        ],
        description: "use int8 as input. Typically Accelerated OPS require int8.",
      },
      {
        name: "estimator_type",
        type: "str",
        default: "classification",
        options: [
          {
            name: "classification",
          },
          {
            name: "regression",
          },
        ],
      },
    ],
    output_contract: [],
    description: "Provides the ability to continue training a TensorFlow model for further epochs.",
    type: "Training Algorithm",
    subtype: "Neural Network",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "fa5a9887-f555-4117-8b1a-27f20355a27c",
    name: "Custom Feature Selection By Index",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "custom_feature_selection",
        type: "dict",
        description: "Describes which features to keep",
      },
      {
        name: "passthrough_columns",
        type: "list",
        description: "List of non sensor columns",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    This is a feature selection method which allows custom feature selection. This takes a dictionary where the key is the\n    feature generator number and the value is an array of the features for the feature generator to keep. All feature generators\n    that are not added as keys in the dictionary will be dropped.\n\n    Args:\n        input_data (DataFrame): Input data to perform feature selection on.\n        custom_feature_selection (dict): A dictionary of feature generators and their corresponding features to keep.\n        passthrough_columns (list):  A list of columns to include in the output DataFrame in addition to the selected\n            features.\n        **kwargs: Additional keyword arguments to pass to the function.\n\n    Returns:\n        Tuple[DataFrame, list]: A tuple containing the selected features and the passthrough columns as a DataFrame, and a list\n        of unselected features.\n\n    Example:\n\n        .. code-block:: python\n\n            client.pipeline.add_feature_selector([{'name': 'Custom Feature Selection By Index',\n                                        'params': {\"custom_feature_selection\":\n                                                {1: [0], 2:[0], 3:[1,2,3,4]},\n                                        }}])\n\n            # would select the features 0 from feature generator 1 and 2, and\n            # features 1,2,3,4 from the generator feature generator 3.\n\n    ",
    type: "Feature Selector",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "0b49d80a-5a6a-4cf3-b5ef-73f125b1991c",
    name: "Max Min Threshold Segmentation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        no_display: true,
      },
      {
        name: "column_of_interest",
        type: "str",
        streams: true,
        display_name: "Column Of Interest",
        number_of_elements: 1,
      },
      {
        name: "group_columns",
        type: "list",
        no_display: true,
        element_type: "str",
      },
      {
        name: "max_segment_length",
        type: "int",
        c_param: 1,
        default: 200,
        description: "maximum number of samples a segment can have",
        display_name: "Maximum Segment Length",
      },
      {
        name: "min_segment_length",
        type: "int",
        c_param: 2,
        default: 50,
        description: "minimum number of samples a segment can have",
        display_name: "Minimum Segment Length",
      },
      {
        name: "threshold_space_width",
        type: "int",
        c_param: 3,
        default: 25,
        description: "the size of the window to transform into threshold space",
        display_name: "Threshold Space Width",
      },
      {
        name: "threshold_space",
        type: "str",
        default: "std",
        options: [
          {
            name: "std",
          },
          {
            name: "absolute sum",
          },
          {
            name: "sum",
          },
          {
            name: "variance",
          },
          {
            name: "absolute avg",
          },
        ],
        description: "space to transform signal into to compare against the vertical thresholds",
        display_name: "Threshold Space",
      },
      {
        name: "first_vt_threshold",
        type: "float",
        c_param: 4,
        default: 1000,
        description: "the segment starts when the threshold space is above this value",
        display_name: "Initial Vertical Threshold",
      },
      {
        name: "second_vt_threshold",
        type: "float",
        c_param: 5,
        default: 1000,
        description: "the segment ends when the threshold space is below this value",
        display_name: "Second Vertical Threshold",
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description:
      "\n    This is a max min threshold segmentation algorithm which transforms a window\n    of the data stream of size threshold_space_width into threshold space. This function\n    transfer the `input_data` and `group_column` from the previous pipeline block.\n\n\n    The threshold space can be computed as standard deviation, sum, absolute sum, absolute\n    average and variance. The vt threshold is then compared against the\n    calculated value with a comparison type of >= for the start of the segment\n    and <= for the end of the segment. This algorithm is a two pass\n    detection, the first pass detects the start of the segment, the second pass\n    detects the end of the segment.\n\n    Args:\n        column_of_interest (str): name of the stream to use for segmentation\n        max_segment_length (int): number of samples in the window (default is 100)\n        min_segment_length: The smallest segment allowed.\n        threshold_space_width (float): number of samples to check for being above the\n          vt_threshold before forgetting segment.\n        threshold_space (std): Threshold transformation space. (std, sum, absolute sum, variance, absolute avg)\n        first_vt_threshold (int):vt_threshold value to begin detecting a segment\n        second_vt_threshold (int):vt_threshold value to detect a segments end.\n        return_segment_index (False): set to true to see the segment indexes for start and end.\n\n    Returns:\n        DataFrame: The segmented result will have a new column called `SegmentID` that\n        contains the segment IDs.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df\n            out:\n                   Subject     Class  Rep  accelx  accely  accelz\n                0      s01  Crawling    1     377     569    4019\n                1      s01  Crawling    1     357     594    4051\n                2      s01  Crawling    1     333     638    4049\n                3      s01  Crawling    1     340     678    4053\n                4      s01  Crawling    1     372     708    4051\n                5      s01  Crawling    1     410     733    4028\n                6      s01  Crawling    1     450     733    3988\n                7      s01  Crawling    1     492     696    3947\n                8      s01  Crawling    1     518     677    3943\n                9      s01  Crawling    1     528     695    3988\n                10     s01  Crawling    1      -1    2558    4609\n                11     s01   Running    1     -44   -3971     843\n                12     s01   Running    1     -47   -3982     836\n                13     s01   Running    1     -43   -3973     832\n                14     s01   Running    1     -40   -3973     834\n                15     s01   Running    1     -48   -3978     844\n                16     s01   Running    1     -52   -3993     842\n                17     s01   Running    1     -64   -3984     821\n                18     s01   Running    1     -64   -3966     813\n                19     s01   Running    1     -66   -3971     826\n                20     s01   Running    1     -62   -3988     827\n                21     s01   Running    1     -57   -3984     843\n\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns=['accelx', 'accely', 'accelz'],\n                            group_columns=['Subject', 'Class', 'Rep'],\n                            label_column='Class')\n\n        >>> client.pipeline.add_transform(\"Max Min Threshold Segmentation\",\n                           params={ \"column_of_interest\": 'accelx',\n                                    \"max_segment_length\": 5,\n                                    \"min_segment_length\": 5,\n                                    \"threshold_space_width\": 3,\n                                    \"threshold_space\": 'std',\n                                    \"first_vt_threshold\": 0.05,\n                                    \"second_vt_threshold\": 0.05,\n                                    \"return_segment_index\": False})\n\n        >>> results, stats = client.pipeline.execute()\n        >>> print results\n            out:\n                      Class  Rep  SegmentID Subject  accelx  accely  accelz\n                0  Crawling    1          0     s01     377     569    4019\n                1  Crawling    1          0     s01     357     594    4051\n                2  Crawling    1          0     s01     333     638    4049\n                3  Crawling    1          0     s01     340     678    4053\n                4  Crawling    1          0     s01     372     708    4051\n                5   Running    1          0     s01     -44   -3971     843\n                6   Running    1          0     s01     -47   -3982     836\n                7   Running    1          0     s01     -43   -3973     832\n                8   Running    1          0     s01     -40   -3973     834\n                9   Running    1          0     s01     -48   -3978     844\n\n\n    ",
    type: "Segmenter",
    subtype: "Sensor",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "10f52ea6-1885-4b45-8e5e-4c74e7e2cddf",
    name: "Change Point Detection",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        no_display: true,
      },
      {
        name: "group_columns",
        type: "list",
        no_display: true,
        element_type: "str",
      },
      {
        name: "threshold",
        type: "float",
        c_param: 1,
        default: 500,
        description: "threshold above which a segment will be identified",
        display_name: "Threshold",
      },
      {
        name: "window_size",
        type: "int",
        default: 250,
        description: "size of your window",
        display_name: "Window Size",
      },
      {
        name: "delta_size",
        type: "int",
        default: 250,
        description: "size of your window slide",
        display_name: "Delta Size",
      },
      {
        name: "coefficients",
        type: "list",
        default: [],
        display_name: "Coefficients",
      },
      {
        name: "distance",
        type: "str",
        default: "L1",
        options: [
          {
            name: "L1",
          },
          {
            name: "LSUP",
          },
        ],
      },
      {
        name: "return_segment_index",
        type: "boolean",
        default: false,
        no_display: true,
      },
      {
        name: "history",
        type: "int",
        default: 2,
        description: "Size of history to store.",
        display_name: "Stored History",
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        metadata_columns: ["SegmentID"],
      },
    ],
    description: " ",
    type: "Transform",
    subtype: "Feature Vector",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "5a179eb6-cf66-47e3-969c-169ffc2d989f",
    name: "AutoGroup Labels",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "combine_labels",
        type: "dict",
        description: "Map of label columns to combine",
        element_type: "list_str",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Finds the optimal grouping of labels such that all labels fall into two groups\n    which are most separable in your feature space.\n\n    Args:\n        input_data (DataFrame): input DataFrame\n            The DataFrame containing the input data.\n        label_column (str): label column name\n            The name of the column containing labels to be grouped.\n        combine_labels (dict): map of label columns to combine\n            A dictionary that maps label columns to be combined.\n\n    Returns:\n        DataFrame\n            A new DataFrame containing only the rows for which the metadata value is\n            in the accepted list.\n    ",
    type: "Sampler",
    subtype: "Feature Grouping",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "637c5b92-aa29-4912-be38-be9e15e4f472",
    name: "Zscore Filter",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "label_column",
        type: "str",
      },
      {
        name: "zscore_cutoff",
        type: "int",
        range: [1, 6],
        default: 3,
        description: "Cutoff for to filter features above z score.",
        display_name: "Z score Cutoff",
      },
      {
        name: "feature_threshold",
        type: "int",
        range: [1, 4],
        default: 1,
        description:
          "The number of features in a feature vector that can be outside of the zscore_cutoff without removing the feature vector.",
        display_name: "Feature Threshold",
      },
      {
        name: "feature_columns",
        type: "list",
        default: [],
        description: "List of features to filter by, if none filters all (default None).",
        display_name: "Feature Columns",
      },
      {
        name: "assign_unknown",
        type: "bool",
        default: false,
        description: "Assign unknown label to outliers.",
        display_name: "Assign Unknown",
      },
    ],
    output_contract: [
      {
        name: "df_out",
        type: "DataFrame",
      },
    ],
    description:
      "\n    A z-score filter is a way to standardize feature vectors by transforming each\n    feature in the vector to have a mean of zero and a standard deviation of one.\n    The z-score, or standard score, is a measure of how many standard deviations\n    a data point is from the mean of the distribution.  This features that have\n    z-score outside of a cutoff threshold are removed.\n\n    Args:\n        input_data (DataFrame): Input DataFrame.\n        label_column (str): Label column name.\n        zscore_cutoff (int): Cutoff for filtering features above z score.\n        feature_threshold (int): The number of features in a feature vector that can be outside of\n                                 the zscore_cutoff without removing the feature vector.\n        feature_columns (list): List of features to filter by. If None, filters all.\n        assign_unknown (bool): Assign unknown label to outliers.\n\n    Returns:\n        DataFrame: The filtered DataFrame containing only the rows for which the metadata value is in\n                   the accepted list.\n\n    Examples:\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> df = client.datasets.load_activity_raw()\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class'],\n                            label_column = 'Class')\n        >>> client.pipeline.add_feature_generator([{'name':'Downsample',\n                                     'params':{\"columns\": ['accelx','accely','accelz'],\n                                               \"new_length\": 5 }}])\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices before the filtering algorithm\n        >>> results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5, 6, 7, 8]\n\n        >>> client.pipeline.add_transform(\"Zscore Filter\",\n                           params={\"zscore_cutoff\": 3, \"feature_threshold\": 1})\n\n        >>> results, stats = client.pipeline.execute()\n        # List of all data indices after the filtering algorithm\n        >>>results.index.tolist()\n            Out:\n            [0, 1, 2, 3, 4, 5]\n\n    ",
    type: "Sampler",
    subtype: "Outlier Filter",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "d1b6b0c9-c935-42fb-8349-1737192f9c63",
    name: "Load Model TF Micro",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "TensorFlow Lite for Microcontrollers",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "model_parameters",
        type: "dict",
        default: {
          tflite: "",
        },
      },
      {
        name: "estimator_type",
        type: "str",
        default: "classification",
        options: [
          {
            name: "classification",
          },
          {
            name: "regression",
          },
        ],
      },
      {
        name: "class_map",
        type: "dict",
        default: null,
        handle_by_set: false,
      },
      {
        name: "threshold",
        type: "float",
        default: 0,
        handle_by_set: false,
      },
      {
        name: "train_history",
        type: "dict",
        default: null,
        handle_by_set: false,
      },
      {
        name: "model_json",
        type: "dict",
        default: null,
        handle_by_set: false,
      },
      {
        name: "input_type",
        type: "str",
        default: "int8",
        options: [
          {
            name: "int8",
          },
        ],
        description: "use int8 as input. Typically Accelerated OPS require int8.",
      },
    ],
    output_contract: [],
    description:
      "\n    Provides the ability to upload a TensorFlow Lite flatbuffer to use as the final classifier step in a pipeline.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        model_parameters (int): The flatbuffer object of your TensorFlow micro model\n        class_map (dict): class map for converting labels to output\n        estimator_type (str): defines if this estimator performs regression or classification, defaults to classification\n        threshold (float):  if no values are greater than the threshold, classify as Unknown\n        train_history (dict): training history for this model\n        model_json (dict): expects the model json file from the tensorflow api tf_model.to_json()\n\n\n    Example:\n\n        SensiML provides the ability to train and bring your own NN architecture to use as the classifier for your pipeline.\n        This example starts from the point where you have created features using the SensiML Toolkit\n\n            >>> x_train, x_test, x_validate, y_train, y_test, y_validate, class_map =             >>>     client.pipeline.features_to_tensor(fv_t, test=0.0, validate=.1)\n\n        Tensorflow Lite Micro only supports a subset of the full tensorflow functions. For a full list of available functions\n        see the `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.\n        Use the Keras tensorflow API to create the NN graph.\n\n            >>> from tensorflow.keras import layers\n            >>> import tensorflow as tf\n            >>> tf_model = tf.keras.Sequential()\n            >>> tf_model.add(layers.Dense(12, activation='relu',kernel_regularizer='l1', input_shape=(x_train.shape[1],)))\n            >>> tf_model.add(layers.Dropout(0.1))\n            >>> tf_model.add(layers.Dense(8, activation='relu', input_shape=(x_train.shape[1],)))\n            >>> tf_model.add(layers.Dropout(0.1))\n            >>> tf_model.add(layers.Dense(y_train.shape[1], activation='softmax'))\n            >>> tf_model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])\n            >>> tf_model.summary()\n            >>> train_history = {'loss':[], 'val_loss':[], 'accuracy':[], 'val_accuracy':[]}\n\n        Train the Tensorflow Model\n\n            >>> epochs=100\n            >>> batch_size=32\n            >>> data  = tf.data.Dataset.from_tensor_slices((x_train, y_train))\n            >>> shuffle_ds = data.shuffle(buffer_size=x_train.shape[0], reshuffle_each_iteration=True).batch(batch_size)\n            >>> history = tf_model.fit( shuffle_ds, epochs=epochs, batch_size=batch_size, validation_data=(x_validate, y_validate), verbose=0)\n            >>> for key in train_history:\n            >>>     train_history[key].extend(history.history[key])\n            >>> import sensiml.tensorflow.utils as sml_tf\n            >>> sml_tf.plot_training_results(tf_model, train_history, x_train, y_train, x_validate, y_validate)\n\n        Qunatize the Tensorflow Model\n\n        *   The ```representative_dataset_generator()``` function is necessary to provide statistical information about your dataset in order to quantize the model weights appropriatley.\n        *   The TFLiteConverter is used to convert a tensorflow model into a TensorFlow Lite model. The TensorFlow Lite model is stored as a `flatbuffer <https://google.github.io/flatbuffers/>`_ which allows us to easily store and access it on embedded systems.\n        *   Quantizing the model allows TensorFlow Lite micro to take advantage of specialized instructions on cortex-M class processors using the `cmsis-nn <http://www.keil.com/pack/doc/cmsis/NN/html/index.html>`_ DSP library which gives another huge boost in performance.\n        *   Quantizing the model can reduce size by up to 4x as 4 byte floats are converted to 1 byte ints in a number of places within the model.\n\n            >>> import numpy as np\n            >>> def representative_dataset_generator():\n            >>>     for value in x_validate:\n            >>>     # Each scalar value must be inside of a 2D array that is wrapped in a list\n            >>>         yield [np.array(value, dtype=np.float32, ndmin=2)]\n            >>>\n            >>> converter = tf.lite.TFLiteConverter.from_keras_model(tf_model)\n            >>> converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_SIZE]\n            >>> converter.representative_dataset = representative_dataset_generator\n            >>> tflite_model_quant = converter.convert()\n\n        Uploading Trained TF Lite model to SensiML\n\n            >>> class_map_tmp = {k:v+1 for k,v in class_map.items()} #increment by 1 as 0 corresponds to unknown\n            >>> client.pipeline.set_training_algorithm(\"Load Model TensorFlow Lite for Microcontrollers\",\n            >>>                                     params={\"model_parameters\": {\n            >>>                                             'tflite': sml_tf.convert_tf_lite(tflite_model_quant)},\n            >>>                                             \"class_map\": class_map_tmp,\n            >>>                                             \"estimator_type\": \"classification\",\n            >>>                                             \"threshold\": 0.0,\n            >>>                                             \"train_history\":train_history,\n            >>>                                             \"model_json\": tf_model.to_json()\n            >>>                                             })\n            >>> client.pipeline.set_validation_method(\"Recall\", params={})\n            >>> client.pipeline.set_classifier(\"TensorFlow Lite for Microcontrollers\", params={})\n            >>> client.pipeline.set_tvo()\n            >>> results, stats = client.pipeline.execute()\n            >>>\n            >>> results.summarize()\n\n    ",
    type: "Training Algorithm",
    subtype: "Load",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "d1b6b0c9-c935-42fb-8349-1737192f9c65",
    name: "Train Fully Connected Neural Network",
    input_contract: [
      {
        name: "dense_layers",
        type: "list",
        range: [1, 256],
        default: [64, 32, 16, 8],
        description: "The size of each dense layer",
        element_type: "int",
      },
      {
        name: "drop_out",
        type: "float",
        range: [0, 0.2],
        default: 0.1,
        description:
          "Apply dropout during training after each layer. The value here specifies how many neurons will be excluded at each layer.",
      },
      {
        name: "batch_normalization",
        type: "bool",
        default: true,
        description: "Apply batch normalization after each dense layer",
      },
      {
        name: "final_activation",
        type: "str",
        default: "softmax",
        options: [
          {
            name: "softmax",
          },
          {
            name: "sigmoid",
          },
        ],
        description:
          "This is the activation of the final layer which is responsible for generating the classification.",
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "TensorFlow Lite for Microcontrollers",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "class_map",
        type: "dict",
        default: null,
        handle_by_set: true,
      },
      {
        name: "epochs",
        type: "int",
        range: [1, 100],
        default: 5,
      },
      {
        name: "batch_size",
        type: "int",
        range: [8, 128],
        default: 32,
      },
      {
        name: "threshold",
        type: "float",
        range: [0, 1],
        default: 0.8,
        description: "Threshold value below which the classification will return Unknown.",
      },
      {
        name: "early_stopping_threshold",
        type: "float",
        range: [0.5, 1],
        default: 0.8,
        description:
          "Early stopping threshold to stop training when the validation accuracy stops improving.",
      },
      {
        name: "early_stopping_patience",
        type: "int",
        range: [0, 5],
        default: 2,
        description:
          "The number of epochs after the early stopping threshold was reached to continue training.",
      },
      {
        name: "loss_function",
        type: "str",
        default: "categorical_crossentropy",
        options: [
          {
            name: "categorical_crossentropy",
          },
          {
            name: "binary_crossentropy",
          },
          {
            name: "poisson",
          },
          {
            name: "kl_divergence",
          },
        ],
      },
      {
        name: "learning_rate",
        type: "float",
        range: [0, 0.2],
        default: 0.01,
        description: "The learning rate to apply during training",
      },
      {
        name: "tensorflow_optimizer",
        type: "str",
        default: "adam",
        options: [
          {
            name: "adam",
          },
          {
            name: "SGD",
          },
        ],
      },
      {
        name: "metrics",
        type: "str",
        default: "accuracy",
        options: [
          {
            name: "accuracy",
          },
        ],
        description: "The metric reported during the training.",
      },
      {
        name: "input_type",
        type: "str",
        default: "int8",
        options: [
          {
            name: "int8",
          },
        ],
        description: "use int8 as input. Typically Accelerated OPS require int8.",
      },
      {
        name: "estimator_type",
        type: "str",
        default: "classification",
        options: [
          {
            name: "classification",
          },
          {
            name: "regression",
          },
        ],
      },
    ],
    output_contract: [],
    description:
      '\n    Provides the ability to train a fully connected neural network model to use as the final classifier step in a pipeline.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        class_map (dict): optional, class map for converting labels to output\n        estimator_type (str): defines if this estimator performs regression or classification, defaults to classification\n        threshold (float):  if no values are greater than the threshold, classify as Unknown\n        dense_layers (list): The size of each dense layer\n        drop_out (float): The amount of dropout to use after each dense layer\n        batch_normalization (bool): Use batch normalization\n        final_activation (str): the final activation to use\n        iteration (int): Maximum optimization attempt\n        batch_size (int): The batch size to use during training\n        metrics (str): the metric to use for reporting results\n        learning_rate (float): The learning rate is a tuning parameter in an optimization algorithm that determines the step size at each iteration while moving toward a minimum of a loss function.\n        batch_size (int): Refers to the number of training examples utilized in one iteration.\n        loss_function (str): It is a function that determine how far the predicted values deviate from the actual values in the training data.\n        tensorflow_optimizer (str): Optimization algorithms that is used to minimize loss function.\n\n\n    Example:\n\n        SensiML provides the ability to train NN architecture to use as the classifier for your pipeline.\n        Tensorflow Lite Micro only supports a subset of the full tensorflow functions. For a full list of available functions\n        see the `all_ops_resolver.cc <https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/micro/all_ops_resolver.cc>`_.\n        Use the Keras tensorflow API to create the NN graph.\n\n        >>> client.project = \'Activity_Detection\'\n        >>> client.pipeline = \'tf_p1\'\n\n        >>> client.pipeline.stop_pipeline()\n\n        >>> sensors = [\'GyroscopeX\', \'GyroscopeY\', \'GyroscopeZ\', \'AccelerometerX\', \'AccelerometerY\', \'AccelerometerZ\']\n\n        >>> client.pipeline.reset()\n\n        >>> client.pipeline.set_input_query("Q1")\n\n        >>> client.pipeline.add_transform("Windowing", params={"window_size":200,\n                                        "delta":200,\n                                        "train_delta":0})\n\n        >>> client.pipeline.add_feature_generator([\n                {\'name\':\'MFCC\', \'params\':{"columns":sensors,"sample_rate":100, "cepstra_count":1}}\n            ])\n\n        >>> client.pipeline.add_transform("Min Max Scale")\n\n        >>> client.pipeline.set_validation_method("Recall", params={})\n\n        >>> client.pipeline.set_training_algorithm("Train Fully Connected Neural Network", params={\n                                "estimator_type":"classification",\n                                "class_map": None,\n                                "threshold":0.0,\n                                "dense_layers": [64,32,16,8],\n                                "drop_out": 0.1,\n                                "iterations": 5,\n                                "learning_rate": 0.01,\n                                "batch_size": 64,\n                                "loss_function":"categorical_crossentropy",\n                                "tensorflow_optimizer":"adam",\n                                "batch_normalization": True,\n                                "final_activation":"softmax,\n            })\n\n        >>> client.pipeline.set_classifier("TensorFlow Lite for Microcontrollers")\n\n        >>> client.pipeline.set_tvo({\'validation_seed\':None})\n\n        >>> results, stats = client.pipeline.execute()\n        >>> results.summarize()\n\n    ',
    type: "Training Algorithm",
    subtype: "Neural Network",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "efffc5cb-2629-4b2e-a787-3ecb127bacb9",
    name: "RBF with Neuron Allocation Optimization",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "remove_unknown",
        type: "boolean",
        default: false,
        description:
          "If there is an Unknown label, remove that from the database of patterns prior to saving the model.",
      },
      {
        name: "number_of_iterations",
        type: "int",
        range: [1, 1000],
        default: 100,
        description: "The number of times to shuffle the training set and rerun the algorithm.",
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "PME",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "turbo",
        type: "bool",
        default: true,
        description:
          "The algorithm will repeatedly runs through the set of unplaced feature vectors until no new neurons are created",
        handle_by_set: false,
      },
      {
        name: "ranking_metric",
        type: "str",
        default: "f1_score",
        options: [
          {
            name: "f1_score",
          },
          {
            name: "accuracy",
          },
          {
            name: "sensitivity",
          },
        ],
        handle_by_set: false,
      },
      {
        name: "number_of_neurons",
        type: "int",
        range: [1, 16384],
        default: 128,
        handle_by_set: false,
      },
      {
        name: "aggressive_neuron_creation",
        type: "bool",
        default: true,
        description:
          "The algorithm will place a pattern even if they are within the influence field of another pattern of the same category",
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [],
    description:
      "\n    RBF with Neuron Allocation Optimization takes as input feature vectors, corresponding\n    class labels, and desired number of iterations (or trials), and outputs a set of\n    models. For each iteration the input vectors are randomly shuffled and presented to\n    the PME classifier which either places the pattern as a neuron or does\n    not. When a neuron is placed, an area of influence (AIF) is determined based on the\n    neuron's proximity to other neurons in the model and their respective classes.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        number_of_iterations (int): the number of times to shuffle the training set;\n        turbo (boolean): a flag that when True runs through the set of unplaced feature\n            vectors repeatedly until no new neurons are placed (default is True)\n        number_of_neurons (int): the maximum allowed number of neurons; when the\n            model reaches this number, the algorithm will stop training\n        aggressive_neuron_creation (bool): flag for placing neurons even if they are within\n            the influence field of another neuron of the same category (default is False)\n        ranking_metric (str): Method to score models by when evaluating best candidate.\n            Options: [f1_score, sensitivity, accuracy]\n\n    Returns:\n        a set of models\n\n    ",
    type: "Training Algorithm",
    subtype: "PME",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "9045c36b-b0e0-4414-8b7c-c04c4e06d1ae",
    name: "Load Neuron Array",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        handle_by_set: true,
      },
      {
        name: "label_column",
        type: "str",
        handle_by_set: true,
      },
      {
        name: "ignore_columns",
        type: "list",
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "classifiers",
        type: "list",
        options: [
          {
            name: "PME",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "validation_methods",
        type: "list",
        options: [
          {
            name: "Stratified K-Fold Cross-Validation",
          },
          {
            name: "Stratified Shuffle Split",
          },
          {
            name: "Set Sample Validation",
          },
          {
            name: "Split by Metadata Value",
          },
          {
            name: "Recall",
          },
          {
            name: "Stratified Metadata k-fold",
          },
          {
            name: "Metadata k-fold",
          },
          {
            name: "Leave-One-Subject-Out",
          },
        ],
        element_type: "str",
        handle_by_set: true,
      },
      {
        name: "neuron_array",
        type: "list",
        default: [],
        element_type: "dict",
        handle_by_set: false,
      },
      {
        name: "class_map",
        type: "dict",
        default: {},
        handle_by_set: false,
      },
    ],
    output_contract: [],
    description:
      "\n    Load Neuron Array takes an input of feature vectors, corresponding class labels,\n    and a neuron array to use for classification.  The neuron array is loaded and\n    classification is performed.\n\n    Note: This training algorithm does not perform optimizations on the provided neurons.\n\n    Args:\n        input_data (DataFrame): input feature vectors with a label column\n        label_column (str): the name of the column in input_data containing labels\n        neuron_array (list): A list of neurons to load into the hardware simulator.\n        class_map (dict): class map for converting labels to neuron categories.\n\n    Returns:\n        a set of models\n\n    ",
    type: "Training Algorithm",
    subtype: "PME",
    has_c_version: false,
    library_pack: null,
    automl_available: false,
  },
  {
    uuid: "bffa231a-2dbc-4b0d-bdab-87b9c8fc09ad",
    name: "Leave-One-Subject-Out",
    input_contract: [
      {
        name: "group_columns",
        type: "list",
        element_type: "str",
      },
      {
        name: "test_size",
        type: "float",
        range: [0, 0.5],
        default: 0,
      },
    ],
    output_contract: [],
    description:
      "\n    A cross-validation scheme which holds out the samples for all but one subject for testing\n    in each fold. In other words, for a data set consisting of 10 subjects, each fold will\n    consist of a training set from 9 subjects and test set from 1 subject; thus, in all, there\n    will be 10 folds, one for each left out test subject.\n\n    Args:\n        group_columns (list[str]): list of column names that define the groups (subjects)\n    ",
    type: "Validation Method",
    subtype: null,
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4f2f95e9-e7e5-4cc9-9272-03721b529e73",
    name: "Zero Crossings",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "threshold",
        type: "numeric",
        range: [-32767, 32766],
        c_param: 0,
        default: 100,
        description: "value in addition to mean which must be crossed to count as a crossing",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the number of times the selected input crosses the mean+threshold and mean-threshold values. The threshold value is specified by the user.\n    crossing the mean value when the threshold is 0 only counts as a single crossing.\n\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n        threshold: value in addition to mean which must be crossed to count as a crossing\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Zero Crossings',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'],\n                                               \"threshold: 5}\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "8adfd68a-8ac9-4b4d-9d45-1b52362d1dfb",
    name: "Standard Deviation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    The standard deviation of a vector V with N items, is the measure of spread\n    of the distribution. The standard deviation is the square root of the average     of the squared deviations from the mean, i.e., std = sqrt(mean(abs(x - x.mean())**2)).\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Standard Deviation',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxStd  gen_0002_accelyStd  gen_0003_accelzStd\n            0     s01            2.280351             1.16619            1.720465\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "8a5d33f7-1041-4270-9027-06f2273df072",
    name: "Time Flip",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "fraction",
        type: "float",
        range: [0.1, 1],
        default: 0.5,
        description: "Fraction of the input data segments that are used for this augmentation.",
        handle_by_set: false,
      },
      {
        name: "flipped_label",
        type: "str",
        default: "Unknown",
        description: "Label of the flipped segment.",
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: false,
        description:
          "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      '\n    Time Flip:\n        Flip the signal along the time axis.\n        This augmentation is used to decrease the false positive rate by increasing the model sensitivity to feed-forward signals.\n        The label of the flipped signal is different than the label of the original signal, usually "Unknown".\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.\n        flipped_label (str): Label of the flipped segment. Most often this label si different than the original label of the segment such as "Unknown" and "Noise".\n        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of the transformed datasegments\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df["segment_uuid"] = df.apply(lambda row: "07baf4b8-21b9-4b98-8927-de1264bb2a92" if row.Class=="Crawling" else "e2a80997-346a-4327-8fa4-2de7de65ac99", axis=1)\n        >>> client.upload_dataframe("toy_data.csv", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data(\'toy_data\',\n                                data_columns=[\'accelx\', \'accely\', \'accelz\'],\n                                group_columns=[\'Subject\', \'Class\', \'Rep\', \'segment_uuid\'],\n                                label_column=\'Class\')\n        >>> client.pipeline.add_transform(\'Windowing\', params={\'window_size\' : 5, \'delta\': 5})\n\n        >>> client.pipeline.add_augmentation(\n                                        [\n                                            {\n                                                "name": "Time Flip",\n                                                "params": {\n                                                    "fraction": 1,\n                                                    "flipped_label": "Unknown",\n                                                },\n                                        },\n                                        ]\n                                    )\n\n        >>> results, stats = client.pipeline.execute()\n\n        >>> print(results)\n            Out:\n                    accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n                0      372     708    4051   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000\n                1      340     678    4053   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000\n                2      333     638    4049   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000\n                3      357     594    4051   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000\n                4      377     569    4019   Unknown    1     s01  07baf4b8-21b9-fff6-de12-007ec13cff00  396000000\n                5      -62   -3988     827   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001\n                6      -66   -3971     826   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001\n                7      -64   -3966     813   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001\n                8      -64   -3984     821   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001\n                9      -52   -3993     842   Unknown    1     s01  e2a80997-346a-fff6-2de7-81605a5ccf00  830000001\n                10     528     695    3988   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001\n                11     518     677    3943   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001\n                12     492     696    3947   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001\n                13     450     733    3988   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001\n                14     410     733    4028   Unknown    1     s01  07baf4b8-21b9-fff6-de12-f0c7faff4f00  351000001\n                15     -48   -3978     844   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000\n                16     -40   -3973     834   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000\n                17     -43   -3973     832   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000\n                18     -47   -3982     836   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000\n                19     -44   -3971     843   Unknown    1     s01  e2a80997-346a-fff6-2de7-d0b32f6dbf00  818000000\n                20     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                21     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                22     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                23     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                24     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n                25     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                26     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                27     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                28     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                29     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n                30     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                31     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                32     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                33     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                34     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n                35     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                36     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                37     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                38     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n                39     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n\n\n    ',
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "c9a0a586-2581-4dca-9ee6-6d874e0f071c",
    name: "25th Percentile",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "segment_size",
        },
      },
    ],
    description:
      "\n    Computes the 25th percentile of each column in 'columns' in the dataframe.\n    A q-th percentile of a vector V of length N is the q-th ranked value in\n    a sorted copy of V. If the normalized ranking doesn't match the q exactly,\n    interpolation is done on two nearest values.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'25th Percentile',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelx25Percentile  gen_0002_accely25Percentile  gen_0003_accelz25Percentile\n            0     s01                         -2.0                          6.0                          5.0\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "1133919d-8d30-4154-bb1b-0ccf7caa2bca",
    name: "100th Percentile",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the 100th percentile of each column in 'columns' in the dataframe.\n    A 100th percentile of a vector V the maximum value in V.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n\n    Returns:\n        DataFrame: Returns feature vector with 100th percentile (sample maximum) of each specified column.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                                [-2, 8, 7], [2, 9, 6]],\n                                columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'100th Percentile',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n              Subject  gen_0001_accelx100Percentile  gen_0002_accely100Percentile  gen_0003_accelz100Percentile\n            0     s01                           3.0                           9.0                           8.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "4f820fff-0f9b-41d9-81c2-4beb213f631c",
    name: "Sum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the cumulative sum of each column in 'columns' in the dataframe.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Standard Deviation',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxSum  gen_0002_accelySum  gen_0003_accelzSum\n            0     s01                 0.0                36.0                29.0\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "be77cfa2-fa93-4d0c-8dc4-14a1caf2e772",
    name: "Absolute Sum",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Computes the cumulative sum of absolute values in each column in 'columns' in the dataframe.\n\n    Args:\n        columns:  list of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame: Returns data frame with specified column(s).\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Absolute Sum',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxAbsSum  gen_0002_accelyAbsSum  gen_0003_accelzAbsSum\n            0     s01                   10.0                   36.0                   29.0\n\n    ",
    type: "Feature Generator",
    subtype: "Statistical",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "b8ccf6a3-35f3-4409-8e62-7af50af69ee4",
    name: "Max Peak to Peak of first half of High Frequency",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "smoothing_factor",
        type: "int",
        range: [1, 32],
        c_param: 0,
        default: 5,
        description:
          "Determines the amount of attenuation for frequencies over the cutoff frequency",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Max Peak to Peak of first half of High Frequency. The high frequency signal\n    is calculated by subtracting the moving average filter output from the original signal.\n\n    Args:\n        smoothing_factor (int); Determines the amount of attenuation for\n          frequencies over the cutoff frequency.\n        columns: List of str; Set of columns on which to apply the feature generator\n\n    Returns:\n        DataFrame of `max p2p half high frequency` for each column and the specified group_columns\n\n    Examples:\n        >>> import numpy as np\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:75].tolist() + df['accely'][75:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Max Peak to Peak of first half of High Frequency',\n                                     'params':{\"smoothing_factor\": 5,\n                                               \"columns\": ['accelx','accely','accelz'] }}])\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelxMaxP2P1stHalfAC  gen_0002_accelyMaxP2P1stHalfAC  gen_0003_accelzMaxP2P1stHalfAC\n            0      0     s01                             1.8                             7.0                             1.8\n            1      1     s01                             1.8                             7.0                            20.0\n\n\n    ",
    type: "Feature Generator",
    subtype: "Amplitude",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "24a2af8f-5347-4add-993f-61472a476be5",
    name: "Zero Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
      },
    ],
    description:
      "\n    Calculates the rate at which zero value is crossed for each specified column.\n    The total number of zero crossings are found and then the number is divided\n    by total number of samples to get the `zero_crossing_rate`.\n\n    Args:\n        columns:  The `columns` represents a list of all column names on which\n                 `zero_crossing_rate` is to be found.\n\n    Returns:\n        A DataFrame of containing zero crossing rate\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject']\n                           )\n        >>> client.pipeline.add_feature_generator([{'name':'Zero Crossing Rate',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz'] }\n                                    }])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxZeroCrossingRate  gen_0002_accelyZeroCrossingRate  gen_0003_accelzZeroCrossingRate\n            0     s01                              0.6                              0.0                              0.0\n\n    ",
    type: "Feature Generator",
    subtype: "Rate of Change",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "e3b0f26c-0508-4a0d-8cab-c706d72bcd97",
    name: "MFCC",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Column on which to apply the feature generator",
        num_columns: 1,
        element_type: "str",
      },
      {
        name: "sample_rate",
        type: "int",
        range: [1, 16000],
        c_param: 0,
        default: 16000,
      },
      {
        name: "cepstra_count",
        type: "int",
        range: [1, 23],
        c_param: 1,
        default: 23,
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        family: true,
        output_formula: "params['cepstra_count']",
        scratch_buffer: {
          type: "fixed_value",
          value: 512,
        },
      },
    ],
    description:
      "\n    Translates the data stream(s) from a segment into a feature vector of Mel-Frequency Cepstral Coefficients (MFCC).\n    The features are derived in the frequency domain that mimic human auditory response.\n\n    Note: The current FFT length is 512. Data larger than this will be truncated. Data smaller than this will be zero padded.\n\n    Args:\n        input_data (DataFrame): The input data.\n        columns (list of strings): Names of the sensor streams to use.\n        sample_rate (int): Sampling rate\n        cepstra_count (int): Number of coefficients to generate.\n\n    Returns:\n        DataFrame: Feature vector of MFCC coefficients.\n\n    Examples:\n        >>> import pandas as pd\n        >>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],\n                               [-2, 8, 7], [2, 9, 6]],\n                               columns= ['accelx', 'accely', 'accelz'])\n        >>> df['Subject'] = 's01'\n        >>> print df\n            out:\n               accelx  accely  accelz Subject\n            0      -3       6       5     s01\n            1       3       7       8     s01\n            2       0       6       3     s01\n            3      -2       8       7     s01\n            4       2       9       6     s01\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject'])\n        >>> client.pipeline.add_feature_generator([{'name':'MFCC', 'params':{\"columns\": ['accelx'],\n                                                              \"sample_rate\": 10,\n                                                              \"cepstra_count\": 23 }}])\n        >>> result, stats = client.pipeline.execute()\n\n        >>> print result\n            out:\n              Subject  gen_0001_accelxmfcc_000000  gen_0001_accelxmfcc_000001 ... gen_0001_accelxmfcc_000021  gen_0001_accelxmfcc_000022\n            0     s01                    131357.0                    -46599.0 ...                      944.0                       308.0\n\n    ",
    type: "Feature Generator",
    subtype: "Frequency",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "f80c4992-b71b-4a67-a141-020c9d0233ce",
    name: "Spectral Entropy",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
        description: "Input signal data",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the feature generator",
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataFrame",
        scratch_buffer: {
          type: "fixed_value",
          value: 512,
        },
      },
    ],
    description:
      "\n    Calculate the spectral entropy for each specified signal. For each column,\n    first calculate the power spectrum, and then using the power spectrum, calculate\n    the entropy in the spectral domain. Spectral entropy measures the spectral\n    complexity of the signal.\n\n    Note: the current FFT length is 512, data larger than this will be truncated.\n    Data smaller than this will be zero padded\n\n    Args:\n        columns: List of all columns for which `spectral_entropy` is to be calculated\n\n    Returns:\n        DataFrame of `spectral_entropy` for each column and the specified group_columns\n\n    Examples:\n        >>> import matplotlib.pyplot as plt\n        >>> import numpy as np\n\n        >>> sample = 100\n        >>> df = pd.DataFrame()\n        >>> df = pd.DataFrame({ 'Subject': ['s01'] * sample ,\n                    'Class': ['0'] * (sample/2) + ['1'] * (sample/2) })\n        >>> x = np.arange(sample)\n        >>> fx = 2; fy = 3; fz = 5\n        >>> df['accelx'] = 100 * np.sin(2 * np.pi * fx * x / sample )\n        >>> df['accely'] = 100 * np.sin(2 * np.pi * fy * x / sample )\n        >>> df['accelz'] = 100 * np.sin(2 * np.pi * fz * x / sample )\n        >>> df['accelz'] = df['accelx'][:25].tolist() + df['accely'][25:50].tolist() + df['accelz'][50:].tolist()\n\n\n        >>> client.pipeline.reset(delete_cache=False)\n        >>> client.pipeline.set_input_data('test_data', df, force=True,\n                            data_columns = ['accelx', 'accely', 'accelz'],\n                            group_columns = ['Subject','Class']\n                           )\n\n        >>> client.pipeline.add_feature_generator([{'name':'Spectral Entropy',\n                                     'params':{\"columns\": ['accelx', 'accely', 'accelz' ]}\n                                    }])\n\n\n        >>> result, stats = client.pipeline.execute()\n        >>> print result\n            out:\n               Class Subject  gen_0001_accelxSpecEntr  gen_0002_accelySpecEntr  gen_0003_accelzSpecEntr\n            0      0     s01                  1.97852                 1.983631                 1.981764\n            1      1     s01                  1.97852                 2.111373                 2.090683\n\n    ",
    type: "Feature Generator",
    subtype: "Frequency",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "877a55c6-54b9-40ec-863d-4c08f9e34567",
    name: "Cross Column Correlation",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "sample_frequency",
        type: "int",
        range: [1, 10],
        c_param: 0,
        default: 1,
        description: "Sampling frequency for correlation comparison",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Compute the correlation of the slopes between two columns.\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use\n        sample_frequency (int): frequency to sample correlation at. Default 1 which is every sample\n\n    Returns:\n        DataFrame: feature vector mean difference\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "5fd2f3fb-ad13-4d1f-9e6c-f103c9ba927c",
    name: "Cross Column Mean Crossing Rate",
    input_contract: [
      {
        name: "input_data",
        type: "DataFrame",
      },
      {
        name: "columns",
        type: "list",
        description: "Set of columns on which to apply the transform",
        num_columns: 2,
        element_type: "str",
      },
      {
        name: "group_columns",
        type: "list",
        description: "Set of columns by which to aggregate",
        element_type: "str",
        handle_by_set: true,
      },
    ],
    output_contract: [
      {
        name: "data_out",
        type: "DataFrame",
        family: false,
      },
    ],
    description:
      "Compute the crossing rate of column 2 of over the mean of column 1\n\n    Args:\n        input_data (DataFrame): input data\n        columns (list of strings): name of the sensor streams to use (requires 2 inputs)\n\n    Returns:\n        DataFrame: feature vector mean crossing rate\n    ",
    type: "Feature Generator",
    subtype: "Column Fusion",
    has_c_version: true,
    library_pack: null,
    automl_available: true,
  },
  {
    uuid: "0b402a96-8ff1-43c7-8087-e1608a2d4a96",
    name: "Time Shift",
    input_contract: [
      {
        name: "input_data",
        type: "DataSegment",
      },
      {
        name: "target_labels",
        type: "list",
        default: [],
        description:
          "List of labels that are affected by the augmentation. The augmentation function is applied on ALL labels if this list is empty or not provided.",
        handle_by_set: false,
      },
      {
        name: "filter",
        type: "dict",
        default: {},
        no_display: true,
        description:
          "A Dictionary to define the desired portion of the input data for augmentation.",
        handle_by_set: false,
      },
      {
        name: "selected_segments_size_limit",
        type: "list",
        range: [1, 100000000],
        default: [1, 100000],
        description: "Range of the allowed segment lengths for augmentation.",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "fraction",
        type: "float",
        range: [0.1, 5],
        default: 2,
        description: "Fraction of the input data segments that are used for this augmentation.",
        handle_by_set: false,
      },
      {
        name: "shift_range",
        type: "list",
        default: [-100, 100],
        description:
          "The range of allowed shifts along the time axis. Use integer values. Negative (positive) values shift the signal to the left (right).",
        element_type: "int",
        max_elements: 2,
        min_elements: 2,
        handle_by_set: false,
      },
      {
        name: "averaging_window_size",
        type: "int",
        default: 10,
        description:
          "The window size on the opposite side of the shifting direction, within which the signal average is calculated and used for padding the signal.",
        handle_by_set: false,
      },
      {
        name: "replace",
        type: "boolean",
        default: false,
        description:
          "Replacing the data segments with the augmented versions. If set to True, augmented segments are replaced with newer versions. The original segments are always kept in the set unless they are cropped.",
        handle_by_set: false,
      },
    ],
    output_contract: [
      {
        name: "output_data",
        type: "DataSegment",
      },
    ],
    description:
      "\n    Time Shift:\n        Shifting segments along the time axis. The segment is padded with the signal average within the window of specified size.\n\n        If the UUID of the input segment has the augmented format, the UUID of the output segment would have the augmented format as well.\n        If the input segment is an original segment, the UUID of the output segment follows the UUID of a semi-original segment.\n\n    Args:\n        input_data [DataSegment]: Input data\n        target_labels [str]: List of labels that are affected by this augmentation.\n        filter {str:[]}: A Dictionary that defines the desired portion of the data to be used in the augmentation process. Keys are metadata names and values are lists of desired values.\n        selected_segments_size_limit [int, int]: A list of two integers to specify the range of acceptable segments lengths for the augmentation.\n        fraction [float]: A positive value that represents the fraction of the input data to be augmented. Examples: use 0 for no augmentation, use 1 for 100% augmentation. Any values larger than 1 increases the chances of augmenting a segment more than once.\n        shift_range [int, int]: The range of allowed shifts along the time axis. Use integer values. Negative (positive) values shift the signal to the left (right).\n        averaging_window_size (int): The window size on the opposite side of the shifting direction, within which the signal average is calculated and used for padding the signal.\n        replace (boolean): False: original segments are included in the output dataset, True: the original segments in the input list that meet the filter condition are removed from the output dataset.\n\n    Returns:\n        DataSegment: A list of randomly shifted segments.\n\n    Example:\n        >>> client.pipeline.reset()\n        >>> df = client.datasets.load_activity_raw_toy()\n        >>> df[\"segment_uuid\"] = df.apply(lambda row: \"07baf4b8-21b9-4b98-8927-de1264bb2a92\" if row.Class==\"Crawling\" else \"e2a80997-346a-4327-8fa4-2de7de65ac99\", axis=1)\n        >>> client.upload_dataframe(\"toy_data.csv\", df, force=True)\n        >>> client.pipeline.reset()\n        >>> client.pipeline.set_input_data('toy_data',\n                                data_columns=['accelx', 'accely', 'accelz'],\n                                group_columns=['Subject', 'Class', 'Rep', 'segment_uuid'],\n                                label_column='Class')\n        >>> client.pipeline.add_transform('Windowing', params={'window_size' : 5, 'delta': 5})\n        >>> client.pipeline.add_augmentation(\n                                        [\n                                {\n                                    \"name\": \"Time Shift\",\n                                    \"params\": {\n                                        \"fraction\": 1,\n                                        \"shift_range\": [-2,2],\n                                        \"averaging_window_size\": 2,\n                                    },\n                                },\n                            ], overwrite=False,\n                        )\n        >>> results, stats = client.pipeline.execute()\n        >>> print(results)\n            Out:\n                accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID\n            0      -64   -3966     813   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001\n            1      -66   -3971     826   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001\n            2      -62   -3988     827   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001\n            3      -64   -3979     826   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001\n            4      -64   -3979     826   Running    1     s01  e2a80997-346a-fff5-2de7-9dbf469ebf00  630000001\n            5      -43   -3973     832   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000\n            6      -40   -3973     834   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000\n            7      -48   -3978     844   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000\n            8      -44   -3975     839   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000\n            9      -44   -3975     839   Running    1     s01  e2a80997-346a-fff5-2de7-efb62ecf2f00  236000000\n            10     430     733    4008  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001\n            11     410     733    4028  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001\n            12     450     733    3988  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001\n            13     492     696    3947  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001\n            14     518     677    3943  Crawling    1     s01  07baf4b8-21b9-fff5-de12-965d3a5dcf00  645000001\n            15     377     569    4019  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000\n            16     357     594    4051  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000\n            17     333     638    4049  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000\n            18     340     678    4053  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000\n            19     372     708    4051  Crawling    1     s01  07baf4b8-21b9-fff5-de12-fdfc0e3f1f00  402000000\n            20     377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n            21     357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n            22     333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n            23     340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n            24     372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0\n            25     410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n            26     450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n            27     492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n            28     518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n            29     528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1\n            30     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n            31     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n            32     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n            33     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n            34     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0\n            35     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n            36     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n            37     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n            38     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n            39     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1\n\n\n    ",
    type: "Augmentation",
    subtype: "Supervised",
    has_c_version: false,
    library_pack: null,
    automl_available: true,
  },
];
