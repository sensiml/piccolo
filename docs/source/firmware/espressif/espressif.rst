.. meta::
   :title: Firmware - Espressif ESP-IDF ESP32
   :description: Guide for Espressif ESP32 firmware for data capture and recognition for machine learning applications

=======================
Espressif ESP-IDF ESP32
=======================

.. figure:: /firmware/espressif/img/espressif.png
   :align: center

We support building Knowledge Pack libraries which can be included as part of your application code for ESP32 processors using the ESP-IDF Xtensa GCC Compiler.

For custom hardware, you will need to implement your own data collection and recognition firmware. 

You can follow our :doc:`Simple Streaming Interface<../../simple-streaming-specification/introduction>` to implement data capture to connect to the Data Studio. You can also import .csv or .wav files directly. 

You can follow our :doc:`Knowledge Pack Library<../../knowledge-packs/building-a-knowledge-pack-library>` for instructions on including the machine learning library in your application. 

To download the library, select ESP-IDF ESP32 in the Download Model page along with the appropriate processor for your platform.

.. figure:: /firmware/espressif/img/download-espressif.png
   :align: center
   :alt: Analytics Studio Download Library screen
