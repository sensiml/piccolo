Introduction
------------

The SensiML Simple Streaming Interface is a firmware protocol that defines data collection and recognition APIs on third-party embedded devices so that you can use your device in the SensiML Toolkit.

In this guide we will be going over how you can define the functions and APIs in the SensiML Simple Streaming Interface.

    1. :doc:`Describing output data:<simple-describing-output>` Guide to setting up the self-describing JSON output of this interface. The first thing a device does after boot is send a message describing how it is configured. Since this is baked in to the firmware, no command and control is done by the Data Studio.
    
    2. :doc:`Output of Sensor Data:<simple-output-data>` Guide for implementing the data output portion of the firmware with this interface.
    
    3. :doc:`Streaming Data Over Wi-Fi:<simple-wifi-streaming>` Guide for streaming data over Wi-Fi with the Simple Streaming interface.
    
    4. :doc:`Streaming Data Over BLE GATT:<simple-ble-streaming>` Guide for streaming data over BLE connections with the Simple Streaming interface.
    
    5. :doc:`Validating Simple Stream Implementation:<simple-stream-validation>` Guide and script for validating Simple Streaming Interface implementation on a device.