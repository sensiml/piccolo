.. meta::
   :title: SensiML Open Gateway - Adding Classification Names
   :description: How to add class names during recognition in the SensiML Open Gateway

Adding Classification Names
===========================

The Open Gateway can display class names instead of class IDs during recognition. When you download a Knowledge Pack from the Analytics Studio a model.json file is automatically generated for your model and saved to your Knowledge Pack directory that you can use for displaying class names in the Open Gateway.


*Optional:* :download:`Download Example File <file/model.json>`

.. figure:: /open-gateway/img/open-gateway-recognition.png
   :align: center


From Test Mode
--------------

1. Switch to Test Mode
2. Click **Upload Class Map JSON**

.. figure:: /open-gateway/img/upload_class_map.png
   :align: center

3. Select the model.json file and click open

This will upload the model.json to your Open Gateway server and you will see the class names displayed instead of numbers.

Command Line
------------

You can also set the model.json file path as a command line parameter on start. 


1. Start the Open Gateway with the ``-m`` command to set the model.json file path.

.. code-block::

    # Run from source
    python app.py -m "<path-to-file>"

    # Run from installer
    .\open-gateway.exe -m "<path-to-file>"

    # Replace <path-to-file> with your model.json file path on your computer

2. *(Optional)* You can add multiple command parameters on start. See example below for how to use the ``-m`` and ``-i`` command parameters together to set your model.json and image map file paths on start.

.. code-block::

    # Run from source
    python app.py -m "<path-to-model-json>" -i "<path-to-image-map>"

    # Run from installer
    .\open-gateway.exe -m "<path-to-model-json>" -i "<path-to-image-map>"

    # Replace <path-to-model-json> and <path-to-image-map> with your own file paths