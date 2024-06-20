.. meta::
   :title: SensiML Open Gateway - Adding Classification Images
   :description: How to add images during recognition in the SensiML Open Gateway

Adding Classification Images
============================

The Open Gateway can display images with your classification results by setting the image classification map file path as a command line parameter on start. See the example below for how to create an image classification map file.

*Optional:* :download:`Download Example File <file/image-map.zip>`

.. figure:: /open-gateway/img/open-gateway-recognition-with-images.png
   :align: center

From Test Mode
--------------

1. Switch to Test Mode
2. Click **Upload Class Images JSON**

.. figure:: /open-gateway/img/upload_class_images.png
   :align: center

3. Select the image map file and click open
4. Refresh the UI

This will upload the image map to your Open Gateway server and you will see the images displayed in the image field

Command Line
------------

You can also set image map file path as a command line parameter on start. 

1. Start the Open Gateway with the ``-i`` command to set the image classification map file path.

.. code-block::

    # Run from source
    python app.py -i "<path-to-file>"

    # Run from installer
    .\open-gateway.exe -i "<path-to-file>"
    
    # Replace <path-to-file> with your image classification map file path on your computer

2. *(Optional)* You can add multiple command parameters on start. See example below for how to use the ``-m`` and ``-i`` command parameters together to set your model.json and image map file paths on start.

.. code-block::

    # Run from source
    python app.py -m "<path-to-model-json>" -i "<path-to-image-map>"

    # Run from installer
    .\open-gateway.exe -m "<path-to-model-json>" -i "<path-to-image-map>"

    # Replace <path-to-model-json> and <path-to-image-map> with your own file paths