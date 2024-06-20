.. meta::
   :title: SensiML Toolkit - Getting Started
   :description: Get started with the SensiML Toolkit. Learn how to label sensor data, generate algorithms, and build firmware code with SensiML.

Overview
--------

Welcome to the SensiML Toolkit
``````````````````````````````

The SensiML Toolkit is a developer environment that you can use to build your own smart applications for IoT devices.

The goal of this guide is to provide a step-by-step tutorial on how to use the SensiML Toolkit. We will walk through a **Hello World** style project for sensor applications.


Prerequisites
`````````````

1. Create your SensiML account at `<https://sensiml.com/plans/community-edition/>`_

2. Download and install the SensiML Data Studio from `<https://sensiml.com/download/>`_


Typical Workflow
````````````````

We use a 'training' approach to build smart applications for IoT devices. You will collect and label sensor data with 'events of interest' for building your application. In short, you will collect examples of the events that you want your application to detect and we will build a model that can detect those events.

In the SensiML Toolkit, we provide several options for doing live data collection from a device or you can import sensor data from external sources.


Data Collection and Quick Start Dataset
```````````````````````````````````````

In this tutorial, we will use Accelerometer and Gyroscope sensors to build our demo. We provide a full dataset for this tutorial that you can use to follow along without needing a device.

Example Dataset
^^^^^^^^^^^^^^^

 1. Download the example dataset

   :download:`Example Dataset </guides/getting-started/file/slide-demo.zip>`

We will go over how to use this dataset in the next part of the tutorial.

Live Data Collection
^^^^^^^^^^^^^^^^^^^^

If you use the dataset above, you do not need a device to follow along in the tutorial. However, we will go over the *Live Data Collection* features in the SensiML Toolkit, so if you want to use your device for doing live data collection you can use the following steps below.

If you are using an embedded device to follow along during live data collection, it must be flashed with data collection firmware.

 **Data Collection Firmware - Supported Devices**

 The SensiML Toolkit has out-of-the-box support for many devices described in the :doc:`Data Collection Firmware Documentation</data-studio/flashing-data-collection-firmware>`.

 **Data Collection Firmware - Other Devices**

 If you have your own embedded device that is not in the list above, we support live data collection from third-party devices if you implement our Simple Streaming Interface firmware as described in the :doc:`Simple Streaming Interface Documentation</simple-streaming-specification/introduction>`.

Importing External Sensor Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

*(Optional)* If you have your own means of doing data collection or labeling, you can import labeled sensor data from external sources if it is in a CSV or WAV format. You can find more on this in the :doc:`Importing External Sensor Data Documentation</data-studio/importing-external-sensor-data>` 

This means that if you have created your own protocols/applications for collecting/labeling sensor data you can continue using your tools for labeling your data without needing to convert to our data collection protocol.
