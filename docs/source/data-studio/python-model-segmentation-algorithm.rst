.. meta::
   :title: Data Studio - Python Model Segmentation Algorithm Example
   :description: How to build a segmentation algorithm Python model in the Data Studio

Python Model - Segmentation Algorithm
-------------------------------------

Segmentation Algorithm Overview
```````````````````````````````

The following example goes over building a Python model for segmentation algorithms. You can find another example of building a Python model for a classifier algorithm in the :doc:`Classifier Algorithm Documentation </data-studio/python-model-classifier-algorithm>`. Segmentation algorithms identify the start and end of events based on customizable properties like signal threshold and window size.


Example Code
````````````

1. Download the zip file

 :download:`sliding-window.zip </data-studio/file/sliding-window.zip>`

2. Unzip the file and open ``sliding-window.py`` to view and edit the source code

3. Import the Python file through the Data Studio

.. figure:: /data-studio/img/ds-project-explorer-import-model-python.png
   :align: center

API Overview
`````````````

The Data Studio allows you to import Python algorithms as models. Python models must implement two APIs:

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

Here is an example of the get_info API for a Sliding Window Segmentation algorithm Python algorithm that you can import as a model into the Data Studio.

.. code:: ipython3
      
   def get_info_json() -> str:
      return json.dumps(get_info())
      
   def get_info() -> dict:
      return {
         "name": "Sliding Window",
         "type": "Python",
         "subtype": "Segmentation",
         "description": "This algorithm will segment data using a sliding window approach",
         "input_contract": [
               {
                  "name": "window_size",
                  "type": "int",
                  "default": 400,
                  "range": [200, 1000],
               },
               {
                  "name": "delta",
                  "type": "int",
                  "default": 400,
                  "range": [200, 1000],
               },
         ],
         "output_contract": [],
      }


And here is a screenshot of the UI that is generated.

.. figure:: /data-studio/img/sliding-window-params.png
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
`````````````````````

When the Data Studio runs the model is will call the **recognize_capture** API of the imported Python function to apply to the sensor data. The Data Studio passes two parameters, the data object and the parameters object. The SensiML Python library includes helper functions for converting the objects passed-int from the Data Studio into standard Python objects. Let's look at an example.

This is the main ``recognize_capture`` function for the sliding window algorithm that the Data Studio calls. We use the built-in ``convert_to_datasegments`` function call on the data to turn that into a ``data_segments`` object. This allows us to cast the objects created in the Data Studio to Python types that are easy to work with. Then we run the built-in ``validate_params`` function to validate the input contract and the passed in parameters. After that, we use pass the data_segment and params variables to the ``segment_data`` function which does the segmentation. Finally, we return data to the Data Studio passing it through the to_data_studio function which converts data segments into the appropriate datastudio format.

.. code:: ipython3
      
         
   def recognize_capture(data, params):    
      data_segments = convert_to_datasegments(data)
      
      params = validate_params(get_info()['input_contract'], params)
      
      data_segments = segment_data(data_segments, params['window_size'], params['delta'])

      return to_data_studio(data_segments)


The **segment_data** function is here. This takes then input data, and creates data segments that have the new sizes defined by the windowing parameters

.. code:: ipython3
      
   def segment_data(
      input_data: DataSegments, window_size: int, delta: int
   ) -> DataSegments:
      new_segments = []
      for segment in input_data:
         for segment_id, start_index in enumerate(
               range(0, segment.data.shape[1] - (window_size - 1), delta)
         ):
               tmp_segment = DataSegment(
                  segment_id=segment_id,
                  columns=segment.columns,
                  capture_sample_sequence_start=start_index,
                  capture_sample_sequence_end=start_index + window_size,
               )
               tmp_segment._data = segment.data[
                  :, start_index : start_index + window_size
               ]
               new_segments.append(tmp_segment)

      return DataSegments(new_segments)


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