
Input Contract
```````````````

The input contract is a list of dictionaries. Each item in the list describes an input parameter that the user can configure. The properties of the dictionary are

* **name**: The name of the parameter
* **display_name**: The name to display in the UI, defaults to name if not included
* **type**: The Type of the parameter (bool, int, float, string)
* **default**: The default value to use for the parameter
* **description**: Description of the parameter that will show up in the UI
* **range**: A tuple of min and max values used to limit the input parameters min and max value, eg [0,100] would mean only values from 0 to 100 would be acceptable
* **options(optional)**: A list of options that can be used to create a dropdown selection 
* **num_columns(Reserved)**: This option is reserved for the “columns” input parameter. It specifies how many input channels are allowed in this function. -1 or empty means unlimited.  A specific number like  1,2,3,4 means that number is required.  
