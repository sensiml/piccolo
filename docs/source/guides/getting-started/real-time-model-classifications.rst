.. meta::
   :title: Real-Time Model Classifications
   :description: How to use a model to get real-time classifications

Real-Time Model Classifications
===============================

The SensiML Toolkit greatly accelerates the time to market for any device by creating an all-in-one workflow. After building your model, the SensiML Toolkit includes three options to connect to your model and see the classification results running in real-time

.. figure:: /guides/getting-started/img/header-real-time-model-classifications-3.png

1. Data Studio
--------------

The Data Studio is a good option for quickly seeing classification results without the need to flash your device with a Knowledge Pack. It has connection options for Bluetooth-LE, Serial, and Wi-Fi (TCP/IP). A major benefit of using the Data Studio is that in addition to viewing the classification results in real-time, you can save the classifications as new labels in your project and re-train your dataset with the newly collected labels. See how to use the Data Studio for viewing real-time results in the :doc:`Data Studio Documentation</data-studio/testing-a-model-using-the-data-studio>`.

* Connections: Bluetooth-LE, Serial, Wi-Fi
* Connects to model without flashing to embedded device
* Save classification results to project

.. figure:: /data-studio/img/dcl-test-model-mode.png
   :align: center

2. Open Gateway
---------------

The Open Gateway is a good option for seeing classification results from a model running on your embedded device. It has connection options for Bluetooth-LE, Serial, and Wi-Fi (TCP/IP). You can setup pictures and classification names to show within the application and add a post processing buffer for grouping results using a majority vote algorithm. A major benefit of using the Open Gateway is that it is an open-source application that you can modify the source code to meet your organization's needs. See how to use the Open Gateway for viewing real-time results in the :doc:`Open Gateway Documentation<../../open-gateway/running-a-model-on-your-embedded-device>`.

* Connections: Bluetooth-LE, Serial, Wi-Fi
* Connects to model on embedded device
* Open-source code base

.. note:: The Open Gateway requires the embedded device firmware to be flashed with a model. See how to run a model on your embedded firmware in the next section :doc:`Running a Model On Your Embedded Device<running-a-model-on-your-embedded-device>`.

.. figure:: /open-gateway/img/open-gateway-recognition-with-images.png
   :align: center

3. SensiML TestApp
------------------

The SensiML TestApp is an Android application that is a good option for seeing classification results from a model running on your embedded device. It has a connection option for Bluetooth-LE. You can setup pictures and classification names to show within the application and add a post processing buffer for grouping results using a majority vote algorithm. See how to use the SensiML TestApp for viewing real-time results in the :doc:`SensiML TestApp Documentation<../../testapp/running-a-model-on-your-embedded-device>`.

* Connections: Bluetooth-LE
* Connects to model on embedded device
* Android application *(phone or tablet)*
* Event summary panel

.. note:: The SensiML TestApp requires the embedded device firmware to be flashed with a model. See how to run a model on your embedded firmware in the next section :doc:`Running a Model On Your Embedded Device<running-a-model-on-your-embedded-device>`.

.. figure:: /testapp/img/testapp-classifications-with-images.png
   :align: center
