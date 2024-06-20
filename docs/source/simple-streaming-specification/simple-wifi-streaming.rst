========================
Simple Stream With Wi-Fi
========================

In order to stream data over Wi-Fi, we currently offer two bridge applications.

One is an application to relay data using the `ESP32 <https://www.espressif.com/en/products/socs/esp32>`_, namely using the `ESP32 Feather <https://www.adafruit.com/product/3405>`_ board to work with Feather/Wing form factor boards.

The other is implemented as a `Python application <https://github.com/sensiml/open-gateway>`_ to run on a computer or Raspberry Pi.


Simple Stream Wi-Fi Endpoints
-----------------------------

There are four endpoints create by either application: ``/config``, ``/stream``, ``/disconnect``, and ``/results``.

Config Endpoint
```````````````

The ``/config`` endpoint will be set upon receiving the :doc:`device configuration JSON<simple-describing-output>`. Applications such as the :doc:`Data Studio<../data-studio/overview>` will only need to read this endpoint once per connection. An example configuration for a 6-axis IMU sensor at 100Hz would be


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



Stream Endpoint
```````````````

The ``/stream`` endpoint will stream the data to applications such as the as the :doc:`Data Studio<../data-studio/overview>`. It should send data upon getting an open **HTTP/stream GET** request using **application/octet-stream**. 

The Data Studio expects the format of the data to be **int16 byte arrays** in the order specified by the json in the config endpoint.

When the connection is closed, the data stream should stop, freeing the data stream to be started again by a new request.


Disconnect Endpoint (optional)
```````````````````````````````

The ``/disconnect`` endpoint will be called to end the streaming of sensor data.


Results Endpoint (optional)
````````````````````````````

The ``/results`` endpoint will stream out the JSON data from :doc:`Knowledge Pack<../knowledge-packs/overview>` results being processed by the connected device. It will send them out upon receiving an open HTTP GET request for the stream.



ESP32 Feather Application
-------------------------

The `ESP32 Feather <https://www.adafruit.com/product/3405>`_ application is meant to relay data sent over a Feather/Wing UART to simple http endpoints. The firmware code is found in this `GitHub repository <https://github.com/sensiml/esp32_simple_http_uart>`_.

Compiling this application with your Wi-Fi SSID and password, as well as the UART configuration of your Feather/Wing, will allow the data streaming from your Simple Streaming device (such as the :doc:`Arduino Nano 33<../firmware/arduino-nano33/arduino-nano33>` or :doc:`QuickLogic QuickFeather<../firmware/quicklogic-quickfeather/quicklogic-quickfeather>`) to be relayed to the http endpoints.


Data Collection Vs. Recognition
```````````````````````````````

The ESP32 application will currently only work with data collection OR recognition. Because parsing JSON is costly in an embedded system, it will assume recognition mode if results are received from the device first. It will assume data collection mode if the device configuration JSON is received from the device first.


SensiML Open Gateway
--------------------

In some cases, you may want to use a gateway device to retrieve sensor data from your device as an intermediary between the Data Studio. We have created the SensiML Open Gateway that communicates with the Data Studio over Wi-Fi and can read sensor data from BLE and Serial Connections. It is open-sourced and easily extensible to other data sources.

This application is intended to run as a simple application on a remote computer (Raspberry Pi or other single-board computers that can run Python included).

Instructions for running and configuring the application can be found in the :doc:`SensiML Open Gateway Documentation <../open-gateway/overview>`.


