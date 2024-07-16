# **Adding a feature generator**
This tutorial continues [Transform Contract](file:///C:/wiki/spaces/SEN/pages/2190934020/Transform+Contract) but now also implements the c version of the feature extractor. If you haven’t done that first part of the tutorial go and do that now.

At the end of the previous tutorial we created the feature generator transform **Sum Columns.** We created the Python code, and the transform contract, added it to our database, added a unit test, and added a functional test. In this tutorial, we are going to write the corresponding C code that will run on the embedded device. After that we will add it to our fg\_algorithms.so library and replace the Python code we wrote in the first tutorial with a call to the C function. We will also add a [gtest](https://github.com/google/googletest) to our embedded SDK testing suite.

## Step 1. Update the Model Transform To Include the C code

Update the fields

```yaml
has_c_version: True
c_file_name: fg_stats_sum_columns
c_function_name: fg_stats_sum_columns
```

by convention we keep the file name and the function name the same as the function_in_file for the Python code. Setting the has_c_version to True, lets the code generation know it can use the c code when generating firmware.

Your database table should now look like this.

```yaml
fields:
  name: Sum Columns
  core: True
  version: 1
  type: Feature Generator
  subtype: Statistical
  path: core_functions/feature_generators/fg_stats.py
  function_in_file: fg_stats_sum_columns
  has_c_version: True  
  c_file_name: fg_stats_sum_columns
  c_function_name: fg_stats_sum_columns
  deprecated: False
  dcl_executable: False
  uuid: 5c2a69e3-c831-43d0-8401-1ba46eeddc50
  automl_available: True
model: library.transform
```

## **Step 2. Write our C function**

In the folder

**sensiml\_embedded\_sdk/src/**

create the file

**fg\_stats\_sum\_columns.c**

```c
// FILL_EMBEDDED_SDK_LICENSE

#include "kbalgorithms.h"
int32_t fg_stats_sum_columns(kb_model_t *kb_model,
                            int16_data_t *cols_to_use,
                            float_data_t *params,
                            FLOAT *pFV)
{
    int32_t icol;
    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        pFV[0] += sum(kb_model->pdata_buffer->data + cols_to_use->data[icol],
                     kb_model->sg_index,
                     kb_model->sg_length);
    }
    return 1;
}
```

Let's walk through the above code step by step.

// FILL_EMBEDDED_SDK_LICENSE

Lines with the key // FILL_<XXXX> will be replaced by the code generation engine when the firmware is being generated. In this case, we are replacing the license for the code, this allows us to easily switch license in a single place. As you look into the code, you will see we use the // FILL keyword often to dynamically generate many parts of the final firmware code.

#include "kbalgorithms.h"

The include **kbalgorithms.h** where all of our utility functions are stored. Whenever we generated firmware, all of the kbalgorithms are copied into the generated folder, so you can access any of them. These are where we put helper functions that are reused by multiple pieces of code. Feel free to add additional functions to kbalgorithms that would be helpful.

```c
int32_t fg_stats_sum_columns(kb_model_t *kb_model,
                            int16_data_t *cols_to_use,
                            float_data_t *params,
                            FLOAT *pFV)
```

There is a lot to unpack here. All feature generators have the same function signature and input parameters. They also all return an int32\_t. The return value is the number of features that were generated. Using the return value, the pointer feature vector buffer **pFV** is incremented before being passed into the next feature generator.

**kb_model_t** *kb_model

The **kb_model_t** struct contains all of the information about the current state of the model. In this function, we use it to access the sensor data buffer pdata_buffer as well as information about the index of the start of the segment in the data bufer **sg_index** and the length of the segment in the data buffer **sg_length**.

cols_to_use** 

stores the index to the columns in the models ring buffer to use for the sensor data. The indexes are stored in the data array, and the number of columns in the struct are stored in the size variable. For our example, if we were storing the columns AccX, AccY, AccZ in the ring buffer in indexes, 0,1,2. And we wanted to sum across AccX and AccZ. The cols_to_use.data={0,2} and the cols_to_use.size=2.

```c
typedef struct
{
    int16_t *data; // Array to columns to use
    int size;  // Total number of columns
} int16_data_t;
```

**params**

The params for any c function are passed in as an array in the fload\_data\_t struct. This function doesn’t actually use params, but we still include it for all functions.

```c
typedef struct
{
    float *data; // Array to params to use
    int size;  // Total number of params
} float_data_t;
```

**Float \*pFV** 

This is a pointer to a the raw feature vectors buffer that the feature extractors put their data output. After each new value is stored we increment the pointer to the buffer, and continue writing the next data point.

Finally, the actual function itself. We loop through the cols\_to\_use indexes which gives the columns that we want to sum. The sum function is part of our kbalgorithms.h functions which is designed to efficiently sum data inside the ring buffer. For each data buffer we add it to the same location in the feature vector. The result is the sum across each column is stored in pFV[0].

```c
 for (icol = 0; icol < cols_to_use->size; icol++)
    { 
        pFV[0] += sum(kb_model->pdata_buffer->data + cols_to_use->data[icol],
                     kb_model->sg_index,
                     kb_model->sg_length);
    }
```

## Step 3. Writing the unit test
Now that we have created our C code, the next thing to do is write the corresponding unit test. create the file **sensiml_embedded_sdk/utest/test_fg_stats_sum_columns.cpp** and put the following code in.

```c++
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#define NUM_ROWS 5
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 1
static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    -3, 3, 0,
    -2, 2, 6,
    7, 6, 8,
    9, 5, 8,
    3, 7, 6};
static float fg_stats_sum_columns_outputs[NUM_FG_OUTPUTS] = {29.0f};
class FGStatsSumColumns : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);
        ret = 0;
    }
};
TEST_F(FGStatsSumColumns, generate_features_test)
{
    cols_to_use.data[0]=0;
    cols_to_use.data[1]=2;
    cols_to_use.size=2;
    ret = fg_stats_sum_columns(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(1, ret);
    float tolerance = 0.001f;
    ASSERT_NEAR(pFV[0], fg_stats_sum_outputs[0], tolerance);
}
```

for more information on the testing frame see [gtest unit test overview](file:///C:/wiki/spaces/SEN/pages/197918894/gtest+unit+test+overview) .

## Step 4. Update the CMAKE test file
Open the file **sensiml_embedded_sdk/utest/CmakeLists.txt** and ../src/fg_stats_sum_columns.c as the last item in the SENSIML_SDK list

```c++
set( SENSIML_SDK

…

../src/fg_stats_sum_columns.c,

)
```

After that add the unit test to KB\_UTEST

```c++
set( KB_UTEST

...

test_fg_stats_sum_columns.cpp,

)
```

## Step 4. Run the code generation for the embedded sdk
The files kbalgorithms.h, fg\_algorithms.c, fg\_algorithms.py and pywrapper/Makefile
are generated off the templates, the src, and the functions\_to\_loads.csv files. After you have added a new file, its best to rerun the codegeneration instead of manually updating those files yourself. To run the codegeneration

```bash
cd sensiml_embedded_sdk/codegen

python generate_fg_algorithms.py
```
This will also create the code to link your c function to the python SDK.

## Step 5. Rebuild fg_algorithms.so
fg_algorithms contains all of the algorithms that can called from python. To rebuild the file after running codegen,

```bash

cd sensiml_embedded_sdk/pywrapper

make clean
make -j
```

## Step 5. Update the Python function to call your c code
We will now replace the Python code that we had with our fg_algorithms.run_feature_generator_c function. This takes the c function and data and executes it. You can look into the details, but all you really need to know is that if you have followed everything so far, it will work. You can test this by running you Python unit test we wrote earlier. It should still pass.

```python
def fg_stats_sum_columns(input_data: DataFrame, columns: List[str], **kwargs):
   """
   ...
   """
    return fg_algorithms.run_feature_generator_c(
        input_data, columns, "SumColumns", [], fg_algorithms.fg_stats_sum_columns_w
    )
```

## Step 6. Reload the functions into the database

```bash
cd src/server

python manage.py load_functions
```

## Step 7. Restart the server

```bash
docker compose reload
```

## Step 8. Build a Pipeline and Run Test mode to see if everything works
Test model will compile the firmware and execute it against some test data. We typically use this as a first step to verify everything is working correctly with codegen. It is also automatically run as part of our functional tests.
