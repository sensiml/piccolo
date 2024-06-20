======================
Simple Stream With BLE
======================

In order to stream data over BLE, we currently implement communication with a BLE GATT Service.

A code example of the service on an embedded device is located on github at https://github.com/sensiml/nano33_data_capture


Simple Stream BLE GATT Service
------------------------------

The BLE GATT service implements two characteristics: the configuration characteristic and the data characteristic.

In the code example for the Nano33 BLE Sense, the service is implemented with UUID ``16480000-0525-4ad5-b4fb-6dd83f49546b``

.. _simple-stream-uuids-ref:

.. list-table:: Simple Stream Service default UUID's
  :widths: 25 75
  :stub-columns: 1

  * - Simple Stream Service UUID
    - default ``16480000-0525-4ad5-b4fb-6dd83f49546b``
  * - Configuration Characteristic UUID
    - default ``16480001-0525-4ad5-b4fb-6dd83f49546b``
  * - Data Characteristic UUID
    - default ``16480002-0525-4ad5-b4fb-6dd83f49546b``

Configuration Characteristic
````````````````````````````

The characteristic will store the :doc:`device configuration JSON<simple-describing-output>`. Applications such as the :doc:`Data Studio<../data-studio/overview>` will only need to read the value of this characteristic once per connection.

An example configuration for a 6-axis IMU sensor at 100Hz would be

.. code-block:: python

    {
        "sample_rate":100,
        "samples_per_packet":6,
        "column_location":{
            "AccelerometerX":0,
            "AccelerometerY":1,
            "AccelerometerZ":2,
            "GyroscopeX":3,
            "GyroscopeY":4,
            "GyroscopeZ":5
        }
    }

.. list-table:: Configuration Characteristic Settings
  :widths: 25 75
  :stub-columns: 1

  * - Configuration Descriptor
    - Read
  * - Characteristic Data
    - JSON string describing output
  * - Characteristic Value Length
    - Variable (string length)



Data Characteristic
```````````````````

When notifications are enabled by applications such as the :doc:`Data Studio<../data-studio/overview>`, data should be sent via BLE GATT notifications, sending unformatted data.

The Data Studio expects the format of the data to be in the order specified by the json in the configuration characteristic.

When notifications are disabled, the data stream should stop.

.. list-table:: Data Characteristic Settings
  :widths: 25 75
  :stub-columns: 1

  * - Configuration Descriptor
    - Notify
  * - Characteristic Value
    - Variable (raw binary in :ref:`Version 1<ssi-version-1-ref>` or :ref:`Version 2<ssi-version-2-ref>` format)
  * - Characteristic Value Length
    - Variable (Up to max MTU size)


SensiML Open Gateway
--------------------

In some cases, you may want to use a gateway device to retrieve sensor data from your device as an intermediary between the Data Studio. We have created the SensiML Open Gateway that communicates with the Data Studio over Wi-Fi and can read sensor data from BLE, TCP/IP, and Serial Connections. It is open-sourced and easily extensible to other data sources.

.. note::

    The Open Gateway will be expecting the :ref:`befault UUID's for the BLE service <simple-stream-uuids-ref>`

This application is intended to run as a simple application on a remote computer (Raspberry Pi or other single-board computers that can run Python included).

Instructions for running and configuring the application can be found in the :doc:`SensiML Open Gateway Documentation <../open-gateway/overview>`.
