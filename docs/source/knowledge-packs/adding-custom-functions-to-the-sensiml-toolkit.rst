.. meta::
   :title: Knowledge Packs / Model Firmware - Adding Custom Functions to the SensiML Toolkit
   :description: How to add custom functions to the SensiML Toolkit

Adding Custom Functions to the SensiML Toolkit
==============================================
 
In this tutorial, you will learn how to create your own custom feature generator in the SensiML Toolkit. 

.. note:: You will need to have the library developer permission added to your account to be able to create/modify library packs and custom functions. Contact your team admin for the permissions.
 
.. important:: This feature is currently in Beta. Contact SensiML to enable it on your account.

To start, we will look at an example of a simple feature generator. Then, we will modify that function and upload it to the SensiML servers. From there any member of your team will be able to use that feature generator as part of their ML pipelines.
 
Download the SensiML Embedded SDK

::

    git clone *url-to-sensiml-embedded-sdk* 


Open the file *sensiml\_embedded\_sdk/src/fg\_stats\_sum.c* and you will see the following code.

fg\_stats\_sum.c
~~~~~~~~~~~~~~~~

::

    #include "kbutils.h"

    int fg_stats_sum(kb_model_t * kb_model, int *cols_to_use, int num_cols, float* params, int num_params, float *pFV)
    {
        int icol;
 
        for(icol=0; icol < num_cols; icol++)
        {
            pFV[icol] = utils_buffer_sum(kb_model->pringb + cols_to_use[icol], kb_model->sg_index, kb_model->sg_length);
        }
        return num_cols;
    }

Feature Generator Explanation
-----------------------------

The function signature for the sum feature generator is

::
 
    int fg_stats_sum(kb_model_t * kb_model, int *cols_to_use, int num_cols, float* params, int num_params, float *pFV)

This is the function signature for all feature generators in the SensiML Embedded SDK.

The parameter definitions are

-  kb_model_t: Defines the kb_model for the model we are computing the feature generator on
-  num_cols: Defines the number of columns we are going to compute the features on
-  cols_to_use: Defines the index of cols that should be used to compute the sum
-  params: Defines the param that should be used, in this case this feature generator doesn't use params
-  num_params: Defines the number of params that should be used
-  pFV: Defines a pointer to the feature vector array where the feature vector should be stored

So What is This Function Doing?
```````````````````````````````

The kb_model_t object is passed into the feature generator along with the parameters for how to operate on the kb_model_t object.

cols_to_use is an array which has indexes into the kb\_model ring buffer.

num_cols tells us how many of the columns are going to be used.

The parameters are always passed in as an array of floats and can be cast internally to the appropriate value.

The final parameter float *pFV* is a pointer to the current location of the models feature vectors. Features generated by the feature generator will be added to this array. Once the function finishes, it returns the number of feature vectors that are added to pFV.

kb_model object:

1. **kb_model->pringb** this is a pointer to the ring buffer we want to act on. we add cols\_to\_use[icol] as that will index into the correct internal buffer
2. **kb_models->sg_index** this is a pointer to the index of the start of the segment for this model as identified by the segmentation algorithm
3. **kb_models->sg_length** this is a pointer to the index of the length of the segment in the ring buffer.

We pass these three objects to the utils\_buffer\_sum function, which is designed to take the sum of a ring buffer given, the pointer to the buffer the index of the start, and the length of the buffer to sum over.

Utilities
`````````

The utils_buffer_sum function is part of our kb_utils function libraries that operate on a ring buffer. These functions perform common tasks that are used by many feature generators. They typically take a pointer to the ring buffer and instructions about where to start and how many samples to process

Create a New Feature Generator
------------------------------

Let's modify this function to create a new feature generator to use with SensiML Cloud. Create a new file called

::
 
    fg_stats_sum_threshold.c

and copy the following code. This function creates a new sum function that will only sum values if they are below a specified threshold.

.. important:: The name of the feature generator file and the name of the function must be the same, IE fg_stats_sum_threshold.c is the file and fg_stats_sum_threshold is the function that will be called in the file.

::
 
    #include "kbalgorithms.h"
 
    int32_t utils_threshold_sum(ringb *pringb, int base_index, int num_rows, int threshold)
    {
        int32_t sum = 0.0;
        int irow;
        int16_t value = 0;
 
        sum = 0;
 
        for (irow = base_index; irow < num_rows + base_index; irow++)
        {
            value = get_axis_data(pringb, irow)
            if (value < threshold)
            {
            sum += value; // 16-bit elements, added to 32-bit accumulator
            }
        }
 
        return sum;
    }
 
 
    int fg_stats_sum_threshold(kb_model_t *kb_model, int *cols_to_use, int num_cols, FLOAT *params, int num_params, FLOAT *pFV)
    {
        int icol;
        int threshold = (int)params[0];
 
        for (icol = 0; icol < num_cols; icol++)
        {
            pFV[icol] = (float)utils_threshold_sum(kb_model->pringb + cols_to_use[icol], kb_model->sg_index, kb_model->sg_length, threshold);
        }
        return num_cols;
    }

Testing Locally
---------------

You can see the documentation for adding new test cases if you want to write and test functions locally in the :doc:`Adding Unit Tests with GoogleTest Documentation <adding-unit-tests-with-googletest>`.

Upload fg_stats_sum_threshold.c
-------------------------------

Now that we have created a new feature generator, it is time to upload it to the SensiML Cloud.

1. Open a Jupyter Notebook and initalize the SensiML Python SDK. If you do not have the SensiML Python SDK installed, see the :doc:`SensiML Python SDK Documentation <../sensiml-python-sdk/overview>`

.. code:: ipython3
 
    from sensiml import SensiML
    client = SensiML()

2. Create a library pack if one has not been created yet. The library pack is used to group functions together that can be used by you and your team. To see a list of the current library packs, run the following.
 
.. code:: ipython3
 
    from sensiml.datamanager.library_pack import LibraryPack, LibraryPackSet
    lps = LibraryPackSet(client._connection)
    lps.to_dataframe()

If no library pack has been created yet, you can create a new one

.. code:: ipython3
 
    lp = LibraryPack(client._connection)
 
    lp.name="SensiML Test Library Pack"
    lp.description = "A library pack used for testing purposes"
    lp.maintainer = "chris.knorowski@sensiml.com"
 
    lp.insert()

Now that we have created a library pack, we will add our custom feature generator to the library pack. *Note: You will also need to reference the library pack when including the feature generator as part of the pipeline code.*

Instantiate a Custom Function Class
-----------------------------------

.. code:: ipython3
 
    from sensiml.datamanager.custom_functions import CustomFunction,CustomFunctionSet
    c = CustomFunction(client._connection)

Custom Function Properties
--------------------------

Next, we are going to go over the properties of a custom function.

**library_pack** Defines the UUID of the library pack to add the function to.
 
**c_function_name** Defines the name that you will use to call the function. It must be a unique name when compared with the default SDK functions and your own team's functions.

**subtype** Defines a label that lets you group functions into a particular category (ie. Statistical, Physical)
 
**description** Defines a description of your function.
 
**input contract** Defines the input contract. The input contract will describe the parameters that a user can input into the function. This is a list of dictionaries with the following values in each dictionary.

-  **name**: name of the parameter (letters and _ only)
-  **type**: type of the parameter ("int" or "float")
-  **default**: default value for the parameter
-  **description**: text description of the parameter
-  **c_param**: index of the parameter
-  **range**: (list) the range of [left_right, right_range]
 
**output_contract** Defines how to calculate the number of features that will be generated by your function

**unit_tests** Defines tests to validate that the function is working correctly. Must provide at least one test. This is a list of dictionaries, with each element in the list describing a unit test.
 
-  **test_data**: dictionary where each key describes input data {'column1':[1,4..n], 'column2':[4,2...n], ..}
-  **expected_output**: list containing the expected output for the feature generator
-  **params**: dictionary of parameters including input_columns
-  **tolerance**: the tolerance for how close the expected_output and test results should be

**Example Custom Function**

Let's take a look at an example function with the properties filled in below.

Set the function name, subtype and description

.. code:: ipython3

    c.name = "Sum Under Threshold"
    c.subtype = "Custom"
    c.description = "This function takes the sum of all the values of a segment that are below a specific threshold value."
    c.c_function_name = "fg_stats_sum_threshold"
    c.library_pack = lp.uuid

Next, we create the input contract. This function takes a single a parameter called threshold. We also set a default value so that if a user doesn't enter any value this one will be chosen. The c_param specifies the index of the parameter in the parameter dictionary. And finally, the range allows us to validate user input is correct for this parameter.

In addition to the parameters, the input contract also needs to have a "column" entry which fills in "num_columns" with the number of channels this feature generator takes. For example, if you were calculating the difference in mean between two channels, then num_columns = 2. In this case, this feature generator can accept any number of columns, so we set the num_columns variable to -1, which is a placeholder and means any number of columns is ok.

.. code:: ipython3
 
    MIN_INT_16=-32000
    MAX_INT_16=32000
 
    c.input_contract = [
            {
                "name": "threshold",
                "type": "int",
                "default": 0,
                "description": "values below this threshold will be included in the sum.",
                "c_param":0,
                "range":[MIN_INT_16, MAX_INT_16]
            },
            {
                "name": "columns",
                "num_columns": 1,
            },
    
    ]

The output contract tells us if this is a family feature generator (it creates more than one feature) and how to calculate the number of features it emits. This is a regular feature generator, so we only add

.. code:: ipython3
 
    c.output_contract= [{"name": "output_data", "type": "DataFrame"}]

Additional fields for feature generators that use the scratch buffer or create more than one feature are described below. 

* **family** (bool): False if only returns single feature generator, True otherwise
* **output_formula** (str): A formula describing how to calculate the number of features this function will return
* **scratch_buffer** (str): The size of the buffer this function needs, you can access this buffer as a global called sortedData. You can assume this can be overwritten between functions.

If *family* is True, you need to add an output_formula. This can be some combination of numbers, math operations, len(), and stored params:

For example, a histogram which returns a feature based on the number of bins in its params would be

.. code:: ipython3

    c.output_contract["family"] = True
    c.output_contract["output_formula"] = "params['number_of_bins']"

You could also create one that returns the number of features it has as input columns

.. code:: ipython3

    c.output_contract["family"] = True
    c.output_contract["output_formula"] = "len(params['columns'])"

or a combination of parameters and columns

.. code:: ipython3

    c.output_contract["family"] = True
    c.output_contract["output_formula"] = "params['new_length']*len(params['columns'])"

The params argument must be one of the parameters that is part of the input contract

If no scratch_buffer size is provided, it is assumed this function does not use it. There are a number of ways you can specify the scratch buffer

* The scratch_buffer type **segment_size**, will be set to the size of a single ring buffer, so if you a have window size 512 and have 6 channels. The size will be 512.
* The scratch_buffer type **ring_buffer**, will be set to the size of the entire ring buffer, so if you a have window size 512 and 6 channels the size will be 6*512 which is 3072.
* The scratch_buffer type **fixed_value**, will set the value of the extra buffer to 512.
* The scratch_buffer type **parameter**, will set the value of the extra buffer to the value of a parameter.

.. code:: ipython3

    c.output_contract["scratch_buffer"] = {"type":"segment_size"}
    c.output_contract["scratch_buffer"] = {"type":"ring_buffer"}
    c.output_contract["scratch_buffer"] = {"type":"fixed_value", "value":512}
    c.output_contract["scratch_buffer"] = {"type":"parameter", "name":"number_of_bins"}


For this feature generator, we are creating two unit tests. The first one has input data with one channel **Ax** that has 5 samples of data. The input params set the threshold and input columns to the feature generator. We can also add a tolerance for how close the expected result should be the actual result.

The second unit test has two channels of data **Ax** and **Ay**. We set the input parameters to be two columns this time. For this feature generator, the number of outputs is equal to the number of input channels, so we expect to have two outputs.

Any unit tests you create here will be validated after building your c function. Additionally, we will create some other tests using the input data and parameter ranges to validate the bounds of your function. If all of the tests pass, the function will be added to your teams library of custom feature generators.

.. code:: ipython3
 
    c.unit_tests = [
        {'test_data':{'Ax':[1]*5},
        "expected_output":[0],
        "params":{'input_columns':['Ax'], 'threshold':0},
        "tolerance":0.001
        },
        {'test_data':{'Ax':[10]*5,'Ay':[1]*5},
        "expected_output":[5, 0],
        "params":{'input_columns':['Ay','Ax'], 'threshold':5},
        "tolerance":0.001
        }
    ]

Uploading the Function to SensiML Cloud
---------------------------------------

In the following step we will upload the function to SensiML Cloud. The cloud will run the unit tests supplied and if everything passes make it available as a function to use as part of your pipeline.

.. important:: The filename must be the same as the function name in the file, so if the file is named fg_stats_zero_crossing.c, then the function that will be called in the file must be fg_stats_zero_crossing.

.. code:: ipython3
 
    c._to_representation()

.. parsed-literal::

    {
        "name": "Sum Under Threshold",
        "type": "Feature Generator",
        "description": "This function takes the sum of all the values of a segment that are below a specific threshold value.",
        "input_contract": [
            {
                "name": "threshold",
                "type": "int",
                "default": 0,
                "description": "values below this threshold will be included in the sum.",
                "c_param": 0,
                "range": [-32000, 32000],
            },
            {"name": "columns", "num_columns": 1},
        ],
        "output_contract": [{"name": "output_data", "type": "DataFrame"}],
        "subtype": "Custom",
        "unit_tests": [
            {
                "test_data": {"Ax": [1, 1, 1, 1, 1]},
                "expected_output": [0],
                "params": {"input_columns": ["Ax"], "threshold": 0},
                "tolerance": 0.001,
            },
            {
                "test_data": {"Ax": [10, 10, 10, 10, 10], "Ay": [1, 1, 1, 1, 1]},
                "expected_output": [5, 0],
                "params": {"input_columns": ["Ay", "Ax"], "threshold": 5},
                "tolerance": 0.001,
            },
        ],
        "c_file_name": "",
    }

.. code:: ipython3

    r = c.insert(path="fg_stats_sum_threshold.c")
    r.json()

.. parsed-literal::

    {'uuid': '772f4f69-feff-4c63-9b55-dd13fbc5d92c',
     'name': 'Sum Under Threshold',
     'c_file_name': 'fg_stats_sum_threshold.c',
     'input_contract': [{'name': 'threshold',
       'type': 'int',
       'default': 0,
       'description': 'values below this threshold will be included in the sum.',
       'c_param': 0,
       'range': [-32000, 32000]},
      {'name': 'columns',
       'num_columns': 1,
       'type': 'list',
       'element_type': 'str',
       'description': 'Set of columns on which to apply the transform'},
      {'name': 'input_data', 'type': 'DataFrame'},
      {'name': 'group_columns',
       'type': 'list',
       'element_type': 'str',
       'handle_by_set': True,
       'description': 'Set of columns by which to aggregate'}],
     'output_contract': [{'name': 'output_data', 'type': 'DataFrame'}],
     'description': 'This function takes the sum of all the values of a segment that are below a specific threshold value.',
     'type': 'Feature Generator',
     'subtype': 'Custom',
     'task_state': 'SENT',
     'task_result': 'SENT',
     'created_at': '2021-07-06T17:23:51.889906Z',
     'last_modified': '2021-07-06T17:23:52.978570Z',
     'unit_tests': [{'test_data': {'Ax': [1, 1, 1, 1, 1]},
       'expected_output': [0],
       'params': {'input_columns': ['Ax'], 'threshold': 0},
       'tolerance': 0.001},
      {'test_data': {'Ax': [10, 10, 10, 10, 10], 'Ay': [1, 1, 1, 1, 1]},
       'expected_output': [5, 0],
       'params': {'input_columns': ['Ay', 'Ax'], 'threshold': 5},
       'tolerance': 0.001}]}

The endpoint is asynchronous, check the status by calling the refresh api for the custom function and looking at the task\_state response. You will see either SUCCESS or FAILURE when it is finished.

.. code:: ipython3

    c.refresh().json()['task_state']

.. code:: bash

    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/fftr.o ../src/fftr.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/imfcc.o ../src/imfcc.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/fixlog.o ../src/fixlog.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/fg_algorithms.o ../src/fg_algorithms.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/rb.o ../src/rb.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/crossing_rate.o ../src/crossing_rate.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/std.o ../src/std.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/mean.o ../src/mean.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/sorted_copy.o ../src/sorted_copy.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/sortarray.o ../src/sortarray.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/sum.o ../src/sum.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/stat_mean.o ../src/stat_mean.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/stat_moment.o ../src/stat_moment.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/fftr_utils.o ../src/fftr_utils.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_array.o ../src/utils_array.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_buffer_mean.o ../src/utils_buffer_mean.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_buffer_median.o ../src/utils_buffer_median.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_buffer_argmax.o ../src/utils_buffer_argmax.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_buffer_std.o ../src/utils_buffer_std.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_buffer_min_max.o ../src/utils_buffer_min_max.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/utils_buffer_max.o ../src/utils_buffer_max.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/dsp_dtw_distance.o ../src/dsp_dtw_distance.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/ma_symmetric.o ../src/ma_symmetric.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/array_contains.o ../src/array_contains.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/ratio_diff_impl.o ../src/ratio_diff_impl.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/max_min_high_low_freq.o ../src/max_min_high_low_freq.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/stats_percentile_presorted.o ../src/stats_percentile_presorted.c
    cc -std=c99 -fPIC -fno-builtin -Werror -I../include -I.   -c -o ../src/fg_stats_sum_threshold.o ../src/fg_stats_sum_threshold.c
    making lib
    #   ex1 := 
    #   ex1 += 
    for of1 in  ../src/fftr.o  ../src/imfcc.o  ../src/fixlog.o  ../src/fg_algorithms.o  ../src/rb.o  ../src/crossing_rate.o  ../src/std.o  ../src/mean.o  ../src/sorted_copy.o  ../src/sortarray.o  ../src/sum.o  ../src/stat_mean.o  ../src/stat_moment.o  ../src/fftr_utils.o  ../src/utils_array.o  ../src/utils_buffer_mean.o  ../src/utils_buffer_median.o  ../src/utils_buffer_argmax.o  ../src/utils_buffer_std.o  ../src/utils_buffer_min_max.o  ../src/utils_buffer_max.o  ../src/dsp_dtw_distance.o  ../src/ma_symmetric.o  ../src/array_contains.o  ../src/ratio_diff_impl.o  ../src/max_min_high_low_freq.o  ../src/stats_percentile_presorted.o  ../src/fg_stats_sum_threshold.o; do mv $of1 ./; done
    
    ar rcs /home/sml-app/install/server/datamanager/custom_transforms/c320b13f-35f0-4770-8355-ad5546fb141d/sensiml_embedded_sdk/pywrapper/fg_algorithms.a fftr.o imfcc.o fixlog.o fg_algorithms.o rb.o crossing_rate.o std.o mean.o sorted_copy.o sortarray.o sum.o stat_mean.o stat_moment.o fftr_utils.o utils_array.o utils_buffer_mean.o utils_buffer_median.o utils_buffer_argmax.o utils_buffer_std.o utils_buffer_min_max.o utils_buffer_max.o dsp_dtw_distance.o ma_symmetric.o array_contains.o ratio_diff_impl.o max_min_high_low_freq.o stats_percentile_presorted.o fg_stats_sum_threshold.o
    cc -shared -Wl,-soname,libfg_algorithms.so -o libfg_algorithms.so *.o

.. parsed-literal::

    'SUCCESS'

If there are any errors, you can get full details from the logs to determine why the feature generator creation failed.
 
.. code:: ipython3

    c.logs

You can also delete the function using ``c.delete()``

Using the Function in the Pipeline
----------------------------------

Now that we have uploaded our function, lets check to see that it has been added to the function list

.. code:: ipython3

    client.functions.build_function_list()
    client.list_functions(qgrid=False, functype='Feature Generator', subtype="Custom")

.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th>NAME</th>
          <th>TYPE</th>
          <th>SUBTYPE</th>
          <th>DESCRIPTION</th>
          <th>KP FUNCTION</th>
          <th>UUID</th>
          <th>AVAILABLE</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Sum Under Threshold</td>
          <td>Feature Generator</td>
          <td>Custom</td>
          <td>This function takes the sum of all the values ...</td>
          <td>True</td>
          <td>a4c70ea3-9272-4a5c-a5cc-4563d43ac90e</td>
          <td>True</dt>
        </tr>
      </tbody>
    </table>
    </div>

We will build some test data and create a simple pipeline to test the functionality. 

.. note:: If you upload a function and it fails, the AVAILABLE field will show False until you fix the issues with it. 

.. note:: It is also possible that your new function has function definitions that collide with other functions in your library pack already. So even if it passes its unit tests, we will prevent it from becoming available as it would fail when you compile a Knowledge Pack with two of those functions.

.. code:: ipython3

    client.project='TestProject'
    client.pipeline = 'binary classes'
    sensor_columns = ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ']
    window_size = 200
    num_classes = 3
    num_iterations = 5
    
    df = client.datasets.generate_step_data(
        window_size=window_size, num_classes=num_classes, noise_scale=1, num_iterations=num_iterations)
    for index, column in enumerate(sensor_columns):
        df[column] = client.datasets.generate_step_data(
            window_size=window_size, num_classes=num_classes, noise_scale=1, scale_factor=(index+1)*10, num_iterations=num_iterations)['Data']
    df.drop('Data', axis=1, inplace=True)
    df['Subject'] = 0
    
    client.upload_dataframe('window_test', df, force=True)
    
    rmap = {1: 'A', 2: 'B', 3:'C'}
    df['Label'] = df["Label"].apply(lambda x: rmap[x])
    df.plot(figsize=(16,4))
 
 
.. parsed-literal::

    Uploading file "window_test" to SensiML Cloud.


Create a Pipeline that Includes the New Feature Generator
---------------------------------------------------------

Execute the following steps and to include the data from your own custom feature generator as part of the input to the training algorithm

.. code:: ipython3
 
    client.pipeline.reset(delete_cache=True)
    
    sensor_columns = ['AccelerometerX', 'AccelerometerY', 'AccelerometerZ']
    
    # set our test csv as input into the pipeline
    client.pipeline.set_input_data('window_test.csv', data_columns=sensor_columns,
                                group_columns=['Subject', 'Label'],
                                label_column='Label')
    
    
    client.pipeline.add_transform("Windowing", params={"window_size":window_size, "delta":50, "train_delta":0})
    
    client.pipeline.add_feature_generator([
                                        {'name':'Sum Under Threshold', 
                                         'params':{"columns":['AccelerometerX', 'AccelerometerY', "AccelerometerZ"],
                                                   'threshold':30, 
                                                   "library_pack":lp.uuid}},
                                        {'name':'Sum',
                                             'params':{"columns":['AccelerometerX','AccelerometerY',"AccelerometerZ"]}},
                                       ])
    
    client.pipeline.add_transform("Min Max Scale")
    
    client.pipeline.set_training_algorithm('Random Forest', params={'max_depth':1, 'n_estimators':50})
    client.pipeline.set_classifier('Decision Tree Ensemble', params={})
    
    client.pipeline.set_validation_method("Recall")
    
    client.pipeline.set_tvo({'validation_seed':0})
    
    results, stats = client.pipeline.execute()

.. parsed-literal::

    Warning:: You have cache set to delete, this will cause your pipelines to run slower!

    Executing Pipeline with Steps:

    ------------------------------------------------------------------------
     1.     Name: window_test.csv                   Type: featurefile              
    ------------------------------------------------------------------------
    ------------------------------------------------------------------------
     1.     Name: Windowing                         Type: segmenter                
    ------------------------------------------------------------------------
    ------------------------------------------------------------------------
     1.     Name: generator_set                     Type: generator set             
    ------------------------------------------------------------------------
    ------------------------------------------------------------------------
     1.     Name: Min Max Scale                     Type: transform                
    ------------------------------------------------------------------------
    ------------------------------------------------------------------------
     1.     Name: tvo                               Type: tvo                      
    ------------------------------------------------------------------------
        Classifier: Decision Tree Ensemble
    
    
        Training Algo: Random Forest
            max_depth: 1
            n_estimators: 50
    
        Validation Method: Recall
    
    
    ------------------------------------------------------------------------
    
    
    
    Results Retrieved... Execution Time: 0 min. 15 sec.

.. code:: ipython3
 
    results.feature_vectors.head()

.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th>Label</th>
          <th>SegmentID</th>
          <th>Subject</th>
          <th>gen_0001_AxSumUnder..</th>
          <th>gen_0002_AySumUnder..</th>
          <th>gen_0003_AzSumUnder..</th>
          <th>gen_0004_AxSum</th>
          <th>gen_0005_AySum</th>
          <th>gen_0006_AzSum</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td>0</td>
          <td>0</td>
          <td>3</td>
          <td>254</td>
          <td>221</td>
          <td>1</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>1</td>
          <td>1</td>
          <td>0</td>
          <td>2</td>
          <td>255</td>
          <td>237</td>
          <td>1</td>
          <td>1</td>
          <td>0</td>
        </tr>
        <tr>
          <td>1</td>
          <td>2</td>
          <td>0</td>
          <td>3</td>
          <td>255</td>
          <td>255</td>
          <td>1</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>1</td>
          <td>3</td>
          <td>0</td>
          <td>2</td>
          <td>254</td>
          <td>237</td>
          <td>1</td>
          <td>0</td>
          <td>0</td>
        </tr>
        <tr>
          <td>1</td>
          <td>4</td>
          <td>0</td>
          <td>2</td>
          <td>254</td>
          <td>239</td>
          <td>1</td>
          <td>0</td>
          <td>0</td>
        </tr>
      </tbody>
    </table>
    </div>

Model Validation
----------------
 
Now that we have a trained model, we can test the model using recognize_signal API. This will give us the emulated results for this model using your custom feature generator.

.. code:: ipython3

    model = results.configurations[0].models[0]

.. code:: ipython3

    rr, ss = model.knowledgepack.recognize_signal(datafile='window_test.csv')
    rr.head()

.. raw:: html

    <div>
    <style scoped>
        .dataframe tbody tr th:only-of-type {
            vertical-align: middle;
        }
    
        .dataframe tbody tr th {
            vertical-align: top;
        }
    
        .dataframe thead th {
            text-align: right;
        }
    </style>
    <table border="1" class="dataframe">
      <thead>
        <tr style="text-align: right;">
          <th>Classification</th>
          <th>ClassificationName</th>
          <th>FeatureVector</th>
          <th>FeatureLength</th>
          <th>ModelName</th>
          <th>SegmentEnd</th>
          <th>SegmentID</th>
          <th>SegLength</th>
          <th>SegStart</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>1</td>
          <td>1</td>
          <td>[2, 254, 220, 1, 0, 0]</td>
          <td>6</td>
          <td>0</td>
          <td>199</td>
          <td>0</td>
          <td>200</td>
          <td>0</td>
        </tr>
        <tr>
          <td>1</td>
          <td>1</td>
          <td>[65, 191, 163, 32, 32, 32]</td>
          <td>6</td>
          <td>0</td>
          <td>249</td>
          <td>1</td>
          <td>200</td>
          <td>50</td>
        </tr>
        <tr>
          <td>1</td>
          <td>1</td>
          <td>[128, 127, 125, 64, 63, 63]</td>
          <td>6</td>
          <td>0</td>
          <td>299</td>
          <td>2</td>
          <td>200</td>
          <td>100</td>
        </tr>
        <tr>
          <td>2</td>
          <td>2</td>
          <td>[190, 63, 56, 95, 95, 95]</td>
          <td>6</td>
          <td>0</td>
          <td>349</td>
          <td>3</td>
          <td>200</td>
          <td>150</td>
        </tr>
        <tr>
          <td>2</td>
          <td>2</td>
          <td>[253, 0, 0, 127, 127, 127]</td>
          <td>6</td>
          <td>0</td>
          <td>399</td>
          <td>4</td>
          <td>200</td>
          <td>200</td>
        </tr>
      </tbody>
    </table>
    </div>

Model Download
--------------

Now that you have validated the Knowledge Pack is working, it's time to download it and flash to your firmware. You can download as either a library, source, or binary. In this example we will download for x86 GCC using the SensiML Python SDK, but you can download for any of our supported platforms. You can download using the SensiML Python SDK or the Analytics Studio

.. code:: ipython3

    config = client.platforms_v2.get_platform_by_name("x86 GCC Generic").get_config()
    model.knowledgepack.download_library_v2(config=config)

.. parsed-literal::

    Generating lib with configuration
    target_platform : 26eef4c2-6317-4094-8013-08503dcd4bc5
    test_data : 
    debug : False
    output_options : ['serial']
    application : SensiML AI Model Runner
    target_processor : 822581d2-8845-4692-bcac-4446d341d4a0
    target_compiler : 62aabe7e-4f5d-4167-a786-072e468dc158
    float_options : 
    selected_platform_version : 
    ....

.. parsed-literal::
 
    ('/home/sml-app/notebooks/kp_a3b4198f-44b8-4408-a63a-51d4a14f735f_x86-GCC-Generic_lib_7.2.1_p.zip',
     True)

Summary
-------
 
In summary, we have created a new feature generator, uploaded it to the SensiML cloud and used that to train our model. Once we have trained the model, validated that our custom feature generator was producing the correct results for the pipeline by running the pipeline emulation. Now that you have worked through this tutorial, you will be able to add your own custom functions using the SensiML Embedded SDK.