.. meta::
   :title: Firmware - Raspberry Pi
   :description: Guide for Raspberry Pi firmware for data capture and recognition for machine learning applications

============
Raspberry Pi
============

.. figure:: /firmware/raspberry-pi/img/raspberry-pi-hardware.png
   :align: center
   :alt: Raspberry Pi Hardware

We support building Knowledge Pack libraries which can be included as part of your application code for the Raspberry Pi with Cortex A53 and A72 processors using the Arm GCC compiler.  

For custom hardware, you will need to implement your own data collection and recognition firmware. 

You can follow our :doc:`Simple Streaming Interface<../../simple-streaming-specification/introduction>` to implement data capture to connect to the Data Studio. You can also import .csv or .wav files directly. 

You can follow our :doc:`Knowledge Pack Library<../../knowledge-packs/building-a-knowledge-pack-library>` for instructions on including the machine learning library in your application. 

To download the library, select Raspberry Pi in the Download Model page along with the appropriate processor for your platform.

.. figure:: /firmware/raspberry-pi/img/analytics-studio-download-model-raspberry-pi.png
   :align: center
   :alt: Analytics Studio Download Library screen
