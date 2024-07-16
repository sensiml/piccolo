# **Adding feature generator transform**
This guide will walk through the steps to add a new feature generator transform. At the end of this, you should be able to add a new transform to the server code. In the embedded SDK [Adding a feature generator](file:///C:/wiki/spaces/SEN/pages/2193391619/Adding+a+feature+generator) we will extend this code to add the corresponding c code so that the transform can be run on the device as well.

We will walk through adding a feature generator **Sum Columns** which will sum the values of all the sensor channels passed into the feature generator.
### **Step 1. Create the database entry**
First step is to create the database, entry. We are adding Sum Columns, which can be categorized as a statistical feature. So I’m going to add it to the fg\_stats.py file. You can see the [Transform Model](file:///C:/wiki/spaces/SEN/pages/2190671875/Transform+Model) for documentation on what the fields mean. Open the file **functions\_prod.yml** and add the following anywhere in the file

\- fields:

`    `name: Sum Columns

`    `core: True

`    `version: 1

`    `type: Feature Generator

`    `subtype: Statistical

`    `path: core\_functions/feature\_generators/fg\_stats.py

`    `function\_in\_file: fg\_stats\_sum\_columns

`    `has\_c\_version: False

`    `c\_file\_name: 

`    `c\_function\_name: 

`    `deprecated: False

`    `dcl\_executable: False

`    `uuid: 5c2a69e3-c831-43d0-8401-1ba46eeddc50

`    `automl\_available: True

`  `model: library.transform
### **Step 2. Create the python function.**
By convention, the name of the function should be the python file its associated with, in this case **fg\_stats** followed by whatever name you give the function. In most cases, we use the name of the transform **sum\_columns**, but is not required.

def fg\_stats\_sum\_columns(input\_data: DataFrame, columns: List[str], \*\*kwargs):



`    `column\_name = f"{''.join(columns)}Sum"

`    `result = input\_data[columns].sum().sum()

`    `return DataFrame({column\_name: result})
### **Step 3. Add the Docstring to your function**
The Docstring typically shows how a user can call it from the Python SDK. In most cases we leave out defining the variables such as input\_data that the user does not need to know about. Docstrings follow google python format. We recommend installing the vscode extension autoDocstring to help with the consistency and formatting <https://marketplace.visualstudio.com/items?itemName=njpwerner.autodocstring>

def fg\_stats\_sum\_columns(input\_data: DataFrame, columns: List[str], \*\*kwargs):

`    `"""

`    `Computes the cumulative sum over all the columns.

`    `Args:

`        `columns:  list of columns on which to apply the feature generator

`    `Returns:

`        `DataFrame: Returns data frame with specified column(s).

`    `Examples:

`        `>>> import pandas as pd

`        `>>> df = pd.DataFrame([[-3, 6, 5], [3, 7, 8], [0, 6, 3],

`                               `[-2, 8, 7], [2, 9, 6]],

`                               `columns= ['accelx', 'accely', 'accelz'])

`        `>>> df['Subject'] = 's01'

`        `>>> print df

`            `out:

`               `accelx  accely  accelz Subject

`            `0      -3       6       5     s01

`            `1       3       7       8     s01

`            `2       0       6       3     s01

`            `3      -2       8       7     s01

`            `4       2       9       6     s01

`        `>>> client.pipeline.reset(delete\_cache=False)

`        `>>> client.pipeline.set\_input\_data('test\_data', df, force=True,

`                            `data\_columns = ['accelx', 'accely', 'accelz'],

`                            `group\_columns = ['Subject']

`                           `)

`        `>>> client.pipeline.add\_feature\_generator([{'name':'Standard Deviation',

`                                     `'params':{"columns": ['accelx', 'accely', 'accelz'] }

`                                    `}])

`        `>>> result, stats = client.pipeline.execute()

`        `>>> print result

`            `out:

`              `Subject  gen\_0001\_accelxaccelyaccelzSum

`            `0     s01                 32

`    `"""

`    `column\_name = f"{''.join(columns)}Sum"

`    `result = input\_data[columns].sum().sum()

`    `return DataFrame({column\_name: result})
### **Step 4. Create the Transform Contract**
The Transform contract must have the same name as the function with the added **\_contracts** on the end. The server code expects this in order to be able to match up functions with input contracts. The contract is a dictionary containing at least the “input\_contract” and “output\_contract” entries. See the documentation for more information [Transform Contract](file:///C:/wiki/spaces/SEN/pages/2190934020/Transform+Contract).

fg\_stats\_sum\_columns\_contracts = {

`    `"input\_contract": [

`        `{"name": "input\_data", "type": "DataFrame"},

`        `{

`            `"name": "columns",

`            `"type": "list",

`            `"element\_type": "str",

`            `"description": "Set of columns on which to apply the feature generator",

`        `},

`        `{

`            `"name": "group\_columns",

`            `"type": "list",

`            `"element\_type": "str",

`            `"handle\_by\_set": True,

`            `"description": "Set of columns by which to aggregate",

`        `},

`    `],

`    `"output\_contract": [{"name": "output\_data", "type": "DataFrame"}],

}
### **Step 5. Load the function into the server**
Now that we have added the function, we can load it into the server for our tests. To load it into the server run the command

cd sml\_server/kbserver/

python manage.py load\_functions

This will reload all of the functions. In the list you should see Loading Sum Columns… If any errors occur they will show up in the logs, but will not stop the load\_functions command from loading other functions.
### **Step 6. Test your function**
You can test your function by reloading the analytic studio UI. Go to the build model tab, edit the feature generator tab, click + new feature generator. You should see your feature generator in the Statistcal Features as Sum Columns. Add it to the pipeline and run it.

You can also use the python SDK to execute your function for testing.
### **Step 7. Add Unit Tests**
Add a unit tests for your function to the library/tests/core\_functions/test\_fg\_stats.py file. Unit tests are run on every pull requests prior to being allowed to merge. The test should be named test\_fg\_stats\_sum\_columns. It should take expected input data and validate that the response is as expected. Typically we will test whatever parameters are passed in.
### **Step 8. Add a Functional Tests**
Finally, we want to add a functional tests for any new transform to the test\_funtions.py functional tests. These test are run after every merge to master and prior to any deployment. The test is run against a live server and allows us to validate that deployed code is working as expected functionally. Functional tests currently take ~2 hours to run.
### **Step 9. Create a Pull Request**
After you have finished testing your transform. Create a PR for it in bitbucket. Make sure to reference the [SDL-#] at the start of the title of the PR. After you create the PR, the unit tests and linters will run. If there are any issues with the build, the PR will be blocked until they are fixed. In addition, you will need to get one person to review and approve the code before you are allowed to merge.
### **Step 10. Adding the C code for the embedded SDK**
To have the Codegeneration generate the embedded firmware with the C you need to add the C code to the embedded SDK. This Tutorial continues in the embedded SDK [Adding a feature generator](file:///C:/wiki/spaces/SEN/pages/2193391619/Adding+a+feature+generator) tutorial, where you will learn how to add the C code for the embedded SDK and then link the two.
