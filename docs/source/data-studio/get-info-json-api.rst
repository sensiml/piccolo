get_info_json API
`````````````````

The get_info_json API returns the input contract, along with some other information about the transform. When the transform is loaded, this function is called to populate the database with information about the transform. The get_info_json will return a JSON serialized string. Typically, we call the get_info function which returns a dictionary. The get_info dictionary typically will have

* **name**: Name of the Function (used in the UI as the default)
* **type**: Specifies the type of object this is
* **subtype**: Specifies a subtype, this is used for organizing transforms
* **description**: A description of the function that will be shown in the UI
* **input_contract**: A description of the parameters and inputs including types, bounds and options
* **output_contract**: Used to include information about the output of the function