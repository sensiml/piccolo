.. meta::
   :title: Firmware - Microchip Technology SAMD21 Machine Learning Evaluation Kit (SAM-IoT WG)
   :description: Guide for flashing Microchip Technology SAMD21 Machine Learning Evaluation Kit firmware for data collection and recognition

====================================================
Microchip Technology SAMD21 ML Eval Kit (SAM-IoT WG)
====================================================

.. figure:: img/microchip-technology-samd21-ml-eval-kit-hardware.png
    :align: center
    :alt: Microchip Technology SAMD21 Machine Learning Evaluation Kit Hardware


Data Collection Firmware
------------------------

.. list-table:: Microchip Technology SAMD21 ML Eval Kit (SAM-IoT WG) pre-built Data Collection Firmware
   :widths: 35 25 35 10
   :header-rows: 1

   * - Sensors
     - Protocol
     - Download
     - Build Version
   * - (BMI160) Accelerometer & Gyroscope (400 Hz)
     - Simple Stream V2.0 (Serial)
     - :download:`microchip-ss-imu-data-collection-bmi.bin <file/microchip-ss-imu-data-collection-bmi-400hz.hex>`
     - `8.17.2021 <https://github.com/MicrochipTech/ml-samd21-iot-imu-data-logger/tree/main>`_ 
   * - (ICM-42688-P) Accelerometer & Gyroscope (4 KHz)
     - Simple Stream V1.0 (Serial)
     - :download:`microchip-ss-imu-data-collection-icm.bin <file/microchip-ss-imu-data-collection-icm-4khz.hex>`
     - `8.17.2021 <https://github.com/MicrochipTech/ml-samd21-iot-imu-data-logger/tree/main>`_  


.. note:: We provide the binaries above for testing data collection quickly. You can build your own binary from the data collection source code for IMU data collection using the SensiML Simple Streaming Interface. The source code is located in the Microchip Technology github repository at at `<https://github.com/MicrochipTech/ml-samd21-iot-imu-data-logger>`_.


Building & Flashing Firmware Tutorial
-------------------------------------

A tutorial for building and flashing firmware on the Microchip Technology SAMD21 Machine Learning Evaluation Kit can be found at `<https://microchipdeveloper.com/machine-learning:gesturerecognition-with-sensiml>`_


Knowledge Pack/Recognition Firmware Source Code
-----------------------------------------------

Example source code for recognition firmware using a SensiML Knowledge Pack can be found in the Microchip Technology github repository at `<https://github.com/MicrochipTech/ml-samd21-iot-sensiml-gestures-demo>`_