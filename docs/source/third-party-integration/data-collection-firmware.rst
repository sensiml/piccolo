.. meta::
    :title: Third-Party Integration - Data Collection Firmware
    :description: How to interface your device with SensiML data collection firmware

========================
Data Collection Firmware
========================

Data Studio Integration
----------------------------

The SensiML Analytics Toolkit uses an AutoML approach to build smart applications by using sensor data files to train a model to detect the events in your application. The SensiML Data Studio is an application that is used for collecting training data directly from your device, importing external CSV/WAV files, and labeling the data to be used for training your model.

Building Data Collection Firmware
---------------------------------

The Data Studio can collect sensor data from any third-party hardware that implements the Simple Streaming Interface. See more on how to integrate your device into the Data Studio in the :doc:`Adding Custom Device Firmware Documentation<../data-studio/adding-custom-device-firmware>`.

Importing External Data
-----------------------

If you have your own means of collecting sensor data from your device, the Data Studio can import CSV/WAV datasets from any source. See more on the various import formats described in the :doc:`Importing External Sensor Data Documentation<../data-studio/importing-external-sensor-data>`.