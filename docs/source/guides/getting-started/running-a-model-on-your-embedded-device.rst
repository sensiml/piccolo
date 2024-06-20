.. meta::
   :title: Running a Model On Your Embedded Device
   :description: How to run a model on your embedded device

Running a Model On Your Embedded Device
=======================================

In this guide we are going to go over how to run your model on your embedded device. In order to do this we will generate a SensiML Knowledge Pack.

Knowledge Packs
---------------

A Knowledge Pack takes the event detection model you generated in your pipeline and transforms it into a file that can be run on your hardware device at the edge. Once the Knowledge Pack is on your device, it starts outputting classification IDs that correspond to your events of interest. You can download a Knowledge Pack for your platform of choice in the **Download Model** page in the Analytics Studio. You can find out more about integrating Knowledge Pack APIs into your firmware by checking the :doc:`Building a Knowledge Pack Library Documentation</knowledge-packs/building-a-knowledge-pack-library>`

.. figure:: /knowledge-packs/img/analytics-studio-download-model.png
   :align: center

Flashing Your Device
--------------------

The SensiML Toolkit supports a broad range of embedded device platforms. Every platform will have different requirements in order to flash a Knowledge Pack. We've provided instructions for each of our supported platforms in the :doc:`SensiML Firmware Documentation</knowledge-packs/flashing-a-knowledge-pack-to-an-embedded-device>`

.. figure:: /knowledge-packs/img/analytics-studio-flash-knowledge-pack.png
   :align: center

Connecting To Your Device
-------------------------

Once your device is flashed you can use either the **SensiML TestApp** or **SensiML Open Gateway** to connect to your device and display the classification results.

**SensiML TestApp**

If your device and model are using a **Bluetooth-LE** connection then you can use the SensiML TestApp through an Android phone or tablet to display classification results from your embedded device.

1. See how to connect to your device in the :doc:`SensiML TestApp Documentation</testapp/running-a-model-on-your-embedded-device>`

.. figure:: /testapp/img/testapp-classifications-with-images.png
   :align: center

**Open Gateway**

If your device and model are using a **Bluetooth-LE, Serial, or Wi-Fi (TCP/IP)** connection you can use the SensiML Open Gateway to display classification results from your embedded device.

1. See how to connect to your device in the :doc:`Open Gateway Documentation</open-gateway/running-a-model-on-your-embedded-device>`

.. figure:: /open-gateway/img/open-gateway-recognition-with-images.png
   :align: center
