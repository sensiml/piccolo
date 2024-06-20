.. meta::
   :title: Firmware - Arduino Nicla Sense ME
   :description: Guide for flashing Arduino Nicla Sense ME firmware for data capture and recognition

======================
Arduino Nicla Sense ME
======================

.. image:: /firmware/arduino-nicla-sense-me/img/nicla-sense-me-hardware.jpg
    :align: center
    :alt: The Nicla Sense ME Hardware

The Arduino Nicla Sense ME board is physically small and comes with a 64 MHz 32-bit Arm® Cortex-M4 processor along with motion, environmental, pressure, and magnetic sensors from Bosch. Additional sensors can be easily added using the built-in SPI or I2C interfaces. The ultra-low power consumption and tiny size (less than one square inch) of the Nicla Sense ME board enables IoT developers to install complete, intelligent endpoints right at the sensing point.

This guide will go over how to setup the Arduino Nicla Sense ME firmware for data collection or recognition. Once your device is setup, you can find a tutorial on how to use the SensiML Toolkit software in the :doc:`Getting Started Tutorial</guides/getting-started/overview>`.

.. include:: /firmware/arduino-nano33/arduino-nano33.rst
   :start-after:  platformio-start-marker
   :end-before:  platformio-end-marker

Example Firmware
----------------

You can find examples of data collection or recognition firmware below.

**Data Collection Firmware**

.. list-table:: Arduino Nicla Sense ME pre-built Data Collection Firmware
   :widths: 35 25 35 10
   :header-rows: 1

   * - Sensors
     - Protocol
     - Download
     - Version
   * - Accelerometer/Gyroscope (200 Hz)
     - Simple Stream V1.0 (BLE)
     - `nicla-sense-me-ble-200hz-imu.hex <https://github.com/sensiml/nicla-sense-me-data-capture/releases/download/1.0/nicla-sense-me-ble-200hz-imu.hex>`_
     - `1.0 <https://github.com/sensiml/nicla-sense-me-data-capture/releases/tag/1.0>`__
   * - Accelerometer/Gyroscope (200 Hz)
     - Simple Stream V1.0 (USB Serial)
     - `nicla-sense-me-serial-200hz-imu.hex <https://github.com/sensiml/nicla-sense-me-data-capture/releases/download/1.0/nicla-sense-me-serial-200hz-imu.hex>`_
     - `1.0 <https://github.com/sensiml/nicla-sense-me-data-capture/releases/tag/1.0>`__

.. note:: We provide the binaries above for testing data collection quickly. You can build your own binaries for additional sample rates by building from source code in the SensiML GitHub at `<https://github.com/sensiml/nicla-sense-me-data-capture>`__.

**Knowledge Pack/Recognition Firmware**

Knowledge Pack recognition firmware can be found in the SensiML GitHub at `<https://github.com/sensiml/nicla-sense-me-recognition/>`__.

.. include:: /firmware/arduino-nano33/arduino-nano33.rst
   :start-after:  flash-instructions-start-marker
   :end-before:  flash-instructions-end-marker

Using TensorFlow Lite for Microcontrollers in a Knowledge Pack
--------------------------------------------------------------

When running a model built using TensorFlow Lite, another environment is provided in the Knowledge Pack code base. The environment ``env:nicla_sense_me_tensorflow`` will automatically link this in with the same code base.

Changing IMU Frequency/Sample Rate
----------------------------------

The frequency/sample rate that IMU data collection firmware outputs is set at compile-time.

1. Open ``include/sensor_stream.h``.

2. Update ``#define ODR_IMU`` to set the frequency. *Note: The supported frequencies are 25, 50, 100, 200, and 400 Hz.*

Adding New Sensors to the Data Studio
-------------------------------------

The Data Studio includes a built-in device plugin for the Nicla Sense ME *IMU* sensors. You can add additional sensors to your board and use them for data collection in the Data Studio by creating a custom device plugin. You can create a device plugin by defining your sensor information in an SSF file and importing it to the Data Studio. We provide an example SSF file for your device plugin named ``nicla-sense-me.ssf`` in the SensiML GitHub repository at `<https://github.com/sensiml/nicla-sense-me-data-capture/>`__.

For more details on defining SSF file properties and implementing the Simple Streaming specification in your firmware see the :doc:`Adding Custom Device Firmware Documentation</data-studio/adding-custom-device-firmware>`.


More Information
----------------

More information can be found on the Arduino documentation site for the Nicla Sense ME: https://docs.arduino.cc/hardware/nicla-sense-me
