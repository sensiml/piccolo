# **Adding a feature generator**
This tutorial continues [Transform Contract](file:///C:/wiki/spaces/SEN/pages/2190934020/Transform+Contract) but now also implements the c version of the feature extractor. If you haven’t done that first part of the tutorial go and do that now.

At the end of the previous tutorial we created the feature generator transform **Sum Columns.** We created the Python code, and the transform contract, added it to our database, added a unit test, and added a functional test. In this tutorial, we are going to write the corresponding C code that will run on the embedded device. After that we will add it to our fg\_algorithms.so library and replace the Python code we wrote in the first tutorial with a call to the C function. We will also add a [gtest](https://github.com/google/googletest) to our embedded SDK testing suite.
### **Step 1. Update the Model Transform To Include the C code**
Update the fields

**has\_c\_version: True**

**c\_file\_name: fg\_stats\_sum\_columns**

**c\_function\_name: fg\_stats\_sum\_columns**

by convention we keep the file name and the function name the same as the function\_in\_file for the Python code. Setting the has\_c\_version to True, lets the code generation know it can use the c code when generating firmware.

Your database table should now look like this.

- fields:

  `  `name: Sum Columns

  `  `core: True

  `  `version: 1

  `  `type: Feature Generator

  `  `subtype: Statistical

  `  `path: core\_functions/feature\_generators/fg\_stats.py

  `  `function\_in\_file: fg\_stats\_sum\_columns

  `  `has\_c\_version: True  

  `  `c\_file\_name: fg\_stats\_sum\_columns

  `  `c\_function\_name: fg\_stats\_sum\_columns

  `  `deprecated: False

  `  `dcl\_executable: False

  `  `uuid: 5c2a69e3-c831-43d0-8401-1ba46eeddc50

  `  `automl\_available: True

  model: library.transform
### **Step 2. Write our C function**
In the folder

**sensiml\_embedded\_sdk/src/**

create the file

**fg\_stats\_sum\_columns.c**

// FILL\_EMBEDDED\_SDK\_LICENSE

#include "kbalgorithms.h"

int32\_t fg\_stats\_sum\_columns(kb\_model\_t \*kb\_model,

`                            `int16\_data\_t \*cols\_to\_use,

`                            `float\_data\_t \*params,

`                            `FLOAT \*pFV)

{

`    `int32\_t icol;

`    `for (icol = 0; icol < cols\_to\_use->size; icol++)

`    `{

`        `pFV[0] += sum(kb\_model->pdata\_buffer->data + cols\_to\_use->data[icol],

`                     `kb\_model->sg\_index,

`                     `kb\_model->sg\_length);

`    `}

`    `return 1;

}

Let's walk through the above code step by step.

// FILL\_EMBEDDED\_SDK\_LICENSE

Lines with the key // FILL\_<XXXX> will be replaced by the code generation engine when the firmware is being generated. In this case, we are replacing the license for the code, this allows us to easily switch license in a single place. As you look into the code, you will see we use the // FILL keyword often to dynamically generate many parts of the final firmware code.

#include "kbalgorithms.h"

The include **kbalgorithms.h** where all of our utility functions are stored. Whenever we generated firmware, all of the kbalgorithms are copied into the generated folder, so you can access any of them. These are where we put helper functions that are reused by multiple pieces of code. Feel free to add additional functions to kbalgorithms that would be helpful.

int32\_t fg\_stats\_sum\_columns(kb\_model\_t \*kb\_model,

`                            `int16\_data\_t \*cols\_to\_use,

`                            `float\_data\_t \*params,

`                            `FLOAT \*pFV)

There is a lot to unpack here. All feature generators have the same function signature and input parameters. They also all return an int32\_t. The return value is the number of features that were generated. Using the return value, the pointer feature vector buffer **pFV** is incremented before being passed into the next feature generator.

**kb\_model\_t** \*kb\_model

The **kb\_model\_t** struct contains all of the information about the current state of the model. In this function, we use it to access the sensor data buffer pdata\_buffer as well as information about the index of the start of the segment in the data bufer **sg\_index** and the length of the segment in the data buffer **sg\_length**.

cols\_to\_use** 

stores the index to the columns in the models ring buffer to use for the sensor data. The indexes are stored in the data array, and the number of columns in the struct are stored in the size variable. For our example, if we were storing the columns AccX, AccY, AccZ in the ring buffer in indexes, 0,1,2. And we wanted to sum across AccX and AccZ. The cols\_to\_use.data={0,2} and the cols\_to\_use.size=2.

typedef struct

{

`    `int16\_t \*data; // Array to columns to use

`    `int size;  // Total number of columns

} int16\_data\_t;

**params**

The params for any c function are passed in as an array in the fload\_data\_t struct. This function doesn’t actually use params, but we still include it for all functions.

typedef struct

{

`    `float \*data; // Array to params to use

`    `int size;  // Total number of params

} float\_data\_t;

**Float \*pFV** 

This is a pointer to a the raw feature vectors buffer that the feature extractors put their data output. After each new value is stored we increment the pointer to the buffer, and continue writing the next data point.

Finally, the actual function itself. We loop through the cols\_to\_use indexes which gives the columns that we want to sum. The sum function is part of our kbalgorithms.h functions which is designed to efficiently sum data inside the ring buffer. For each data buffer we add it to the same location in the feature vector. The result is the sum across each column is stored in pFV[0].

` `for (icol = 0; icol < cols\_to\_use->size; icol++)

`    `{ 

`        `pFV[0] += sum(kb\_model->pdata\_buffer->data + cols\_to\_use->data[icol],

`                     `kb\_model->sg\_index,

`                     `kb\_model->sg\_length);

`    `}
### **Step 3. Writing the unit test**
Now that we have created our C code, the next thing to do is write the corresponding unit test. create the file **sensiml\_embedded\_sdk/utest/test\_fg\_stats\_sum\_columns.cpp** and put the following code in.

#include "gtest/gtest.h"

#include "kbalgorithms.h"

#include "kb\_typedefs.h"

#include "rb.h"

#include "kb\_common.h"

#include "kb\_utest\_init.h"

#define NUM\_ROWS 5

#define NUM\_INPUT\_COLS 3

#define NUM\_FG\_OUTPUTS 1

static int16\_t rb\_inputs[NUM\_INPUT\_COLS \* NUM\_ROWS] = {

`    `-3, 3, 0,

`    `-2, 2, 6,

`    `7, 6, 8,

`    `9, 5, 8,

`    `3, 7, 6};

static float fg\_stats\_sum\_columns\_outputs[NUM\_FG\_OUTPUTS] = {29.0f};

class FGStatsSumColumns : public testing::Test

{

protected:

`    `virtual void SetUp()

`    `{

`        `num\_cols = NUM\_INPUT\_COLS;

`        `num\_rows = NUM\_ROWS;

`        `sg\_index = 0;

`        `sg\_length = num\_rows;

`        `init\_kb\_model(&kb\_model, &rb[0], sg\_index, sg\_length, rb\_inputs, num\_cols, num\_rows);

`        `ret = 0;

`    `}

};


TEST\_F(FGStatsSumColumns, generate\_features\_test)

{

`    `cols\_to\_use.data[0]=0;

`    `cols\_to\_use.data[1]=2;



`    `cols\_to\_use.size=2;



`    `ret = fg\_stats\_sum\_columns(&kb\_model, &cols\_to\_use, &params, pFV);

`    `ASSERT\_EQ(1, ret);

`    `float tolerance = 0.001f;

`    `ASSERT\_NEAR(pFV[0], fg\_stats\_sum\_outputs[0], tolerance);



}

for more information on the testing frame see [gtest unit test overview](file:///C:/wiki/spaces/SEN/pages/197918894/gtest+unit+test+overview) .
### **Step 4. Update the CMAKE test file**
Open the file **sensiml\_embedded\_sdk/utest/CmakeLists.txt** and ../src/fg\_stats\_sum\_columns.c as the last item in the SENSIML\_SDK list

set( SENSIML\_SDK

…

../src/fg\_stats\_sum\_columns.c,

)

After that add the unit test to KB\_UTEST

set( KB\_UTEST

...

test\_fg\_stats\_sum\_columns.cpp,

)
### **Step 4. Run the code generation for the embedded sdk**
The files kbalgorithms.h, fg\_algorithms.c, fg\_algorithms.py and pywrapper/Makefile
are generated off the templates, the src, and the functions\_to\_loads.csv files. After you have added a new file, its best to rerun the codegeneration instead of manually updating those files yourself. To run the codegeneration

cd sensiml\_embedded\_sdk/codegen

python generate\_fg\_algorithms.py

This will also create the code to link your c function to the python SDK.
### **Step 5. Rebuild fg\_algorithms.so**
fg\_algorithms contains all of the algorithms that can called from python. To rebuild the file after running codegen,

cd sensiml\_embedded\_sdk/pywrapper

make clean

make -j
### **Step 5. Update the Python function to call your c code**
We will now replace the Python code that we had with our fg\_algorithms.run\_feature\_generator\_c function. This takes the c function and data and executes it. You can look into the details, but all you really need to know is that if you have followed everything so far, it will work. You can test this by running you Python unit test we wrote earlier. It should still pass.

def fg\_stats\_sum\_columns(input\_data: DataFrame, columns: List[str], \*\*kwargs):

`   `"""

...

`   `"""

`    `return fg\_algorithms.run\_feature\_generator\_c(

`        `input\_data, columns, "SumColumns", [], fg\_algorithms.fg\_stats\_sum\_columns\_w

`    `)
### **Step 6. Reload the functions into the database**
cd kbserver

python manage.py load\_functions
### **Step 7. Restart the server**
cd kbserver

supervistorctl reload
### **Step 8. Build a Pipeline and Run Test mode to see if everything works**
Test model will compile the firmware and execute it against some test data. We typically use this as a first step to verify everything is working correctly with codegen. It is also automatically run as part of our functional tests.
