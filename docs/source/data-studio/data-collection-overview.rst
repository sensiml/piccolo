.. meta::
   :title: Data Studio - Data Collection Overview
   :description: How to use the Data Studio for doing real-time data collection from your sensor

Data Collection Overview
========================

.. data-collection-overview-start-marker

A large part of building an AI application on the edge is collecting meaningful training data. The Data Studio makes this easy with several useful features including:

* Use any third-party device for real-time data collection over Serial, Bluetooth-LE, and Wi-Fi
* Robust re-training tools on an existing AI application
* Import sensor data (CSV or WAV) from any external source
* Connect to a webcam in combination with your sensor data

.. data-collection-overview-end-marker

Let's go over these features in more detail below.

Real-Time Data Collection
-------------------------

The Data Studio can perform real-time data collection and labeling from any sensor over Serial COM, Bluetooth-LE, or Wi-Fi radios. You can use any third-party device in the Data Studio by updating the device firmware to our open-source Simple Streaming specification.

See more details on how to connect a device for real-time data collection in the :doc:`Real-Time Data Collection Documentation</data-studio/real-time-data-collection>`

.. figure:: /guides/getting-started/img/dcl-live-capture-begin-recording.png
   :align: center

Real-Time Classification Results from a Model/Knowledge Pack
------------------------------------------------------------

After you build a model/Knowledge Pack in the Analytics Studio, the Data Studio can connect to your model to see real-time classification results during data collection.

A major benefit of using the Data Studio is that in addition to viewing the classification results in real-time, you can save the classifications as new labels in your project and re-train your dataset with the newly collected labels. See how to use the Data Studio for viewing real-time results in the :doc:`Running a Model During Data Collection Documentation</data-studio/testing-a-model-using-the-data-studio>`.

.. figure:: /data-studio/img/dcl-test-model-mode.png
   :align: center


Import External Sensor Data
-----------------------------

If you have your own tools for doing data collection, the Data Studio can import external sensor data files (CSV or WAV) from any source. This feature makes it so you can easily migrate your data into the SensiML Analytics Toolkit or continue to use your own tools for data collection without interrupting your workflow. See more details on this feature in the  :doc:`Importing External Sensor Data Documentation</data-studio/importing-external-sensor-data>`.

.. image:: /guides/getting-started/img/dcl-menu-import-files-2.png
   :align: center

Connect to a Webcam
---------------------

The Data Studio can record videos from a webcam during data collection. Videos will stay synced with your sensor data and can be played back later when you label your data. See more details on this feature in the :doc:`Recording Webcam Videos Documentation</open-gateway/recording-webcam-videos>`.

.. image:: /guides/getting-started/img/dcl-webcam-connected.png
   :align: center

