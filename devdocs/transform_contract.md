# **Transform Contract**
The Transform contract describes what data and parameters are expected by a transform as well as what the output data and format of the transform is. The information in the contract is used by the webui to generate the user input forms, by the python sdk to generate the function snippets, by the server to do input parameter validation, and by the code generation engine to generate parameters and SRAM needed.

The contract has both an input contract and output contract.
### **Input Contract**
The input contract describes the parameters that can be passed to a functions API by the user. Each parameter in the input contract can be described by several parameters which define how it is rendered to the user through the webui and python SDK as well as how it is validated by the server. The following describe the input contract parameter options



**name** (required) : the name that will be used for the form shown for this parameter

**type** (required): the expected type for this parameter


Expected types are:

```
    [int][int16\_t][numeric][float]: Number

    [str]: String

    [list]: List

    [dict]: Dictionary
    

**element\_type** (required for [list] or [dict]), this is the expected type inside as values

- [int][int16\_t][numeric][float]: Number
- [str]: String
- [list][list\_str]: only for [dict] List of strings

**min\_elements**: a limit of minimum count of elements for a list. Used for an editable list where a user can add custom elements

**max\_elements**: a limit of maximum count of elements for a list used for an editable list where a user can add custom elements

**lookup** (optional): Instruction about what options will be extracted from a query

- used for dynamic parameters that depend on a query (group_columns, etc.)
- overwrites options provided by this parameter

webui handle values:

**query\_columns** - columns at query

**query\_metadata\_columns** - metadata columns at query

**query\_label\_column** - label\_column at query

**query\_combine\_labels** - combine\_labels at query

**label\_values** - label\_values at labels

**metadata\_names** - list of names from metadata array

**metadata\_label\_values** - list of values from metadata object

**options**: the options that are available for this variables, these are a list of dictionaries with the same properties as the input contract

- used for [list] type
- if not provided list should be editable

**default**: the default value for this parameter which will be set if nothing is passed by the user

**is_ignored**: don't use this field for building pipeline

**is_hidden**: hide from user, but use with default value

**range:** the range of values that are acceptable

**description:** the description will be shown in the documentation

**handle_by_set**: This parameter will be set by the Parent function that this transform is part of

**no_display**: do not display this to the user

**c_param**: the index of the parameter for the c function

**display_name**: the display name to be used in a GUI

**c_param:** Index of the parameter in the c functions parameter array

**num\_columns**:

`      `**-2**: any amount of columns, they will be split up and the feature generator will be called on each column individually

`      `**-1**: any amount of columns, all will be used by the feature generator

`       `**1,2..n**: takes exactly n input columns

`   `"input\_contract": [

`                    `{"name": "input\_data", "type": "DataFrame"},

`                    `{"name": "columns",

`                              `"type": "list",

`                              `"element\_type": "str",

`                              `"description": "Set of columns on which to apply the transform",

`                              `"num\_columns": -1},

`                    `{"name": "group\_columns",

`                     `"type": "list",

`                     `"element\_type": "str",

`                     `"handle\_by\_set": True,

`                     `"description": "Set of columns by which to aggregate"}

`                        `],
### **Output Contract**
The output contract is used to describe the output of a function.

**name (required):** the name of the output data

**type (required)**: The format of the output (Typically DataFrame)

**family** (Optional - defaults to False): Family equals true is used for feature generators that have more than one output. An example would be histogram, which generates “number\_of\_bins” as the number of outputs. None family transforms will always generate a single output

**output\_formula:** This allows us to calculate how many outputs this function will use. This is used by the code generation engine and the internal engine to keep track of where features are coming from. It is evaluated as a literal eval.

**scratch\_buffer:** For functions that require a scratch buffer to store extra data, we have the scratch buffer field. This is a dictionary that can take multiple forms. The following types are currently implemented. See the output contracts in the code for more examples of how these are used.

- **segment\_size** - Scratch buffer of the size of the input segment is needed
- **ring\_buffer** - Scratch buffer of the size ring buffer is needed
- **fixed\_value -** Scratch buffer of a fixed value size is needed
- **parameter -** The Scratch buffer of a size of some input parameter is needed

`    `"output\_contract": [

`        `{

`            `"name": "output\_data",

`            `"type": "DataFrame",

`            `"family": True,

`            `"output\_formula": "params['number\_of\_bins']",

`            `"scratch\_buffer": {"type": "parameter", "name": "number\_of\_bins"},

`        `}

`    `],
### **Example Transform Contract**
fg\_cross\_column\_max\_column\_contracts = {

`        `"input\_contract": [

`                    `{"name": "input\_data", "type": "DataFrame"},

`                    `{"name": "columns",

`                              `"type": "list",

`                              `"element\_type": "str",

`                              `"description": "Set of columns on which to apply the transform",

`                              `"num\_columns": -1},

`                    `{"name": "group\_columns",

`                     `"type": "list",

`                     `"element\_type": "str",

`                     `"handle\_by\_set": True,

`                     `"description": "Set of columns by which to aggregate"}

`                        `],

`        `"output\_contract": [

`                `{"name": "data\_out",

`                 `"type": "DataFrame",

`                 `"family": False}

`                  `]

