.. meta::
   :title: SensiML Toolkit Documentation
   :description: Learn how to label sensor data, generate algorithms, and build firmware code for your devices with SensiML.

=============================
SensiML Toolkit Documentation
=============================

Welcome to the SensiML Analytics Toolkit documentation. The SensiML Toolkit is a software suite for building smart IoT/AI applications on embedded devices at the edge.

Getting Started
---------------

We recommend starting with the :doc:`SensiML Getting Started Guide</guides/getting-started/overview>` which will walk you through how to use each of the tools listed below in a *Hello World* style project for sensor applications.

Included Software
-----------------

 * :doc:`Data Studio</data-studio/overview>` - The Data Studio is an application that helps you capture, organize, and label raw data from the sensor and transform it into the events you want to detect.

 * :doc:`Analytics Studio</analytics-studio/overview>` - The Analytics Studio is an application that filters and optimizes your labeled sensor data through machine learning algorithms. It generates a model (SensiML Knowledge Pack) ready to be flashed into the firmware of your device of choice.

 * :doc:`SensiML TestApp</testapp/overview>` - The SensiML TestApp is an Android application that connects to your embedded device over Bluetooth-LE. It can be used to show real-time event classifications from a model running on your embedded device.

 * :doc:`Open Gateway</open-gateway/overview>` - The Open Gateway is an open-source application that connects to your embedded device over Bluetooth-LE, Serial, or Wi-Fi (TCP/IP). It can be used to display real-time classification results from a model or used as a sensor hub for collecting raw sensor data.

 * :doc:`SensiML Python SDK</sensiml-python-sdk/overview>` - The SensiML Python SDK is a library that provides a programmatic interface to SensiML APIs through python.

.. toctree::
   :maxdepth: 2
   :caption: User Guides

   guides/getting-started/index

.. toctree::
   :maxdepth: 1
   :caption: Application Examples

   application-tutorials/keyword-spotting
   application-tutorials/activity-recognition-boxing-punches
   application-tutorials/canine-activity-recognition-collar
   application-tutorials/robot-motion-recognition
   application-tutorials/industrial-condition-monitoring-tutorial
   application-tutorials/audio-anomaly-detection
   application-tutorials/vibration-anomaly-detection
   application-tutorials/audio-cough-detection
   application-tutorials/guitar-tuning-notes-audio-recognition
   application-tutorials/smart-door-lock-audio-recognition
   application-tutorials/wizard-magic-wand-game

.. toctree::
   :maxdepth: 1
   :caption: Third-Party Devices Integration

   third-party-integration/introduction
   third-party-integration/data-collection-firmware.rst
   third-party-integration/building-recognition-firmware
   third-party-integration/sensiml-test-app

.. toctree::
   :caption: User Documentation
   :maxdepth: 1

   /data-studio/index
   analytics-studio/index
   testapp/index
   open-gateway/index
   sensiml-python-sdk/index
   knowledge-packs/index
   pipeline-functions/index

.. toctree::
   :maxdepth: 1
   :caption: Supported Compilers

   firmware/android-ndk/android-ndk
   firmware/arm-cortex-generic/cortex-arm-generic-platforms
   firmware/espressif/espressif
   firmware/microchip-xc/microchip  
   firmware/x86-processors/x86-platforms

.. toctree::
   :maxdepth: 1
   :caption: Supported Devices

   firmware/arduino-nano33/arduino-nano33
   firmware/arduino-nicla-sense-me/arduino-nicla-sense-me
   firmware/infineon-psoc6/infineon-psoc6-cy8ckit-062s2-43012
   firmware/m5stack-m5stickc-plus/m5stickc-plus
   firmware/microchip-technology-avr128da48-curiosity-nano-evaluation-kit/microchip-technology-avr128da48-curiosity-nano-evaluation-kit
   firmware/microchip-technology-pic-iot-wg-development-board/microchip-technology-pic-iot-wg-development-board
   firmware/microchip-technology-samd21-ml-eval-kit/microchip-technology-samd21-ml-eval-kit
   firmware/nordic-thingy/nordic-thingy
   firmware/onsemi-rsl10-sense/onsemi-rsl10-sense
   firmware/quicklogic-chilkat/quicklogic-chilkat
   firmware/quicklogic-quickai/quicklogic-quickai
   firmware/quicklogic-quickfeather/quicklogic-quickfeather
   firmware/raspberry-pi/raspberry-pi
   firmware/silicon-labs-thunderboard-sense-2/silicon-labs-thunderboard-sense-2
   firmware/silicon-labs-xg24/silicon-labs-xg24
   firmware/sparkfun-thing-plus-quicklogic-eos-s3/sparkfun-thing-plus-quicklogic-eos-s3
   firmware/st-sensortile/st-sensortile
   firmware/st-sensortile-box/st-sensortile-box

.. toctree::
   :maxdepth: 1
   :caption: Simple Streaming Interface

   simple-streaming-specification/introduction
   simple-streaming-specification/simple-describing-output
   simple-streaming-specification/simple-output-data
   simple-streaming-specification/simple-wifi-streaming
   simple-streaming-specification/simple-ble-streaming
   simple-streaming-specification/simple-stream-validation

.. toctree::
   :maxdepth: 1
   :caption: MQTT-SN Interface

   mqtt-specification/index

.. toctree::
   :caption: Resources
   :maxdepth: 1

   SensiML <https://sensiml.com/>
   Try For Free <https://sensiml.com/plans/community-edition/>
   Contact Us <https://sensiml.com/contact/>
   Get Support <https://sensiml.com/support/>
   Dataset Library <https://sensiml.com/resources/app-library/>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

