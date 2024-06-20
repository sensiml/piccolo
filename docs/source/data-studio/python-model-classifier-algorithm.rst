.. meta::
   :title: Data Studio - Python Model Classifier Algorithm Example
   :description: How to build a classifier algorithm Python model in the Data Studio

Python Model - Classifier Algorithm
-----------------------------------

Classifier Algorithm Overview
`````````````````````````````

The following example goes over building a Python model for classifier algorithms. You can find another example of building a Python model for a segmentation algorithm in the :doc:`Segmentation Algorithm Documentation </data-studio/python-model-segmentation-algorithm>`. Classifier algorithms identify events based on a customizable classifier algorithm within the model..

Example Code
````````````

1. Download the zip file

 :download:`classifier.zip </data-studio/file/classifier.zip>`

2. Unzip the file and open ``classifier.py`` to view and edit the source code

3. Import the Python file through the Data Studio

.. figure:: /data-studio/img/ds-project-explorer-import-model-python.png
   :align: center

API Overview
`````````````

The Data Studio allows you to import Python classifiers as models. Imported Python models must implement two APIs

* **get_info_json()**
* **recognize_capture(data, params)**

The **get_info_json** API returns the JSON serialized input contract as a string. The Data Studio UI uses this get_info_json response to dynamically generate a parameters selection screen for the transform. 

The **recognize_capture** API is responsible for taking the input data and parameters from the Data Studio and returning a list of segment label dictionaries which contain the start, end and label name of each segment.

The output should be in the format of a list of dictionaries describing the segments to be added

.. code:: ipython3

      [
       {'SegmentStart': 0,
       'SegmentEnd': 100,
       'ClassificationName': 'Label Name'},
       {'SegmentStart': 50,
        'SegmentEnd': 150,
        'ClassificationName': 'Label Name'},
      ]

Several helper functions demonstrate how to take the input from the Data Studio and turn it into simple Python functions, as well as some helper functions for turning Python objects back into the format the Data Studio will understand.

.. include:: /data-studio/input-contract.rst

.. include:: /data-studio/get-info-json-api.rst

Here is an example of the get_info API for a classification algorithm Python algorithm that you can import as a model into the Data Studio.

.. code:: ipython3
      
   def get_info_json() -> str:
      return json.dumps(get_info())
      
   def get_info() -> dict:
      return {
         "name": "Random Classifier",
         "type": "Python",
         "subtype": "Classifier",
         "description": "This will classify segments as either A or B depending on if the sum of the current segment is greater than the segment before",
         "input_contract": [
               {
                  "name": "columns",
                  "type": "list",
                  "element_type": "str",
                  "description": "Column on which to apply the classifier",
                  "num_columns": 1
               },
               {
                  "name": "window_size",
                  "type": "int",
                  "default": 400,
                  "description": "The size of the sliding window to apply to the sensor data",
                  "range": [200, 1000],
               },
               {
                  "name": "delta",
                  "type": "int",
                  "default": 400,
                  "description": "The size of the slide to apply sensor data",
                  "range": [200, 1000],
               },
         ],
         "output_contract": [],
      }


And here is a screenshot of the UI that is generated.

.. figure:: /data-studio/img/greater-segment-classfier.png
   :align: center

When the user hits save, a model.json file is created inside the imported transforms folder. For this function, here is the model.json file

.. code:: json

   {
      "input_contract": {
         "window_size": 400,
         "delta": 400,
         "columns": [
               "AccelerometerX"
         ]
      }
   }

Whenever the user updates parameters and saves, this model.json file will be updated.

Recognize Capture API
``````````````````````

When the Data Studio runs the model is will call the **recognize_capture** API of the imported Python function to apply to the sensor data. The Data Studio passes two parameters, the data object and the parameters object. The SensiML Python SDK includes helper functions for converting the objects passed in from the Data Studio into standard Python objects. Let's look at an example.

This is the main ``recognize_capture`` function for the sliding window algorithm that the Data Studio calls. We use the built-in ``convert_to_datasegments`` function call on the data to turn that into a ``data_segments`` object. This allows us to cast the objects created in the Data Studio to Python types that are easy to work with. Then we run the built-in ``validate_params`` function to validate the input contract and the passed in parameters. After that, we use pass the data_segment and params variables to the ``segment_data`` function which does the segmentation. Finally, we return data to the Data Studio passing it through the to_data_studio function which converts data segments into the appropriate datastudio format.

.. code:: ipython3
      
         
   def recognize_capture(data, params):
      data_segments = convert_to_datasegments(data)
      
      params = validate_params(get_info()['input_contract'], params)
      
      data_segments = segment_featurize_classify(data_segments, params['window_size'], params['delta'])

      return to_data_studio(data_segments)


The **segment_featurize_classify** function is here. This takes then input data and creates data segments, extracts features, and classifies the features

.. code:: ipython3
         
   def segment_featurize_classify(data_segments: DataSegments, params: None):

   
      data_segments = segment_data(data_segments, get_param(params, "window_size"), get_param(params, "delta"))
      

      data_segments = extract_features(data_segments, params)


      datasegments = classify(data_segments, params)


the **extract_features** function is shown below, it adds a feature vector to the datasegments

.. code:: ipython3
      
   def extract_features(datasegments: DataSegments, params: dict) -> DataSegments:
      for datasegment in datasegments:
         
         col_index = datasegment.get_column_index(params['columns'][0])
         f1 = datasegment.data[col_index, :].sum()
         f2 = datasegment.data[col_index, :].abs()
         f3 = datasegment.data[col_index, :].mean()
         f4 = datasegment.data[col_index, :].min()
         

         datasegment.feature_vector = [f1,f2,f3,f4]

      return datasegments


the **classify** function is shown below, it uses the features in each datasegment to perform a classification. You would replace this function with your model to implement a classifier.

.. code:: ipython3
      
   def classify(datasegments: DataSegments, params: dict) -> DataSegments:

      last = 0
      for datasegment in datasegments:
         
         if datasegment.feature_vector[0] > last:
            datasegment.label_value = "A"
         else:
            datasegment.label_value = "B"

         last = datasegment.feature_vector[0]

      return datasegments


The **to_data_studio** function is below, it converts the datasegments into the return object format defined in the API as a list of dictionaries of the format

.. code:: ipython3

      [
       {'SegmentStart': 0,
       'SegmentEnd': 100,
       'ClassificationName': 'Label Name'},
       {'SegmentStart': 50,
        'SegmentEnd': 150,
        'ClassificationName': 'Label Name'},
      ]

These segments are then stored in the Data Studio and can be edited or saved.