
MQTT-SN Introduction
--------------------

.. important:: The MQTT-SN Interface has been replaced with the new Simple Streaming format. We still support the MQTT-SN interface, but we will not be maintaining or adding any new features going forward. Find more information on the Simple Streaming Interface in the :doc:`Simple Streaming Interface Documentation<../simple-streaming-specification/introduction>`

SensiML provides an end-to-end software solution for data capture, data modeling, and firmware generation for on-device inference for low-power resource-constrained devices. To support this effort, it is necessary to have a robust framework to remotely command and control sensor devices. Typically, most OEMs implement their own method for their specific HDK kits which has led to fragmentation in the industry. To support a seamless experience across a variety of hardware platforms we needed a hardware-agnostic specification to manage sensors across an IoT stack.

This document describes a communication interface protocol for sensor device command and control implemented over MQTT-SN (MQTT-SN is an open-source framework that can be implemented over BLE/Wi-Fi/LoRa/serial/etc.). This document also describes implementation details for using this protocol to live stream raw sensor data, collect sensor data to on-device resources (sd card/flash) as well as configure the sensor for application consumption. SensiML host applications use this specification for data collection and on-device Knowledge Pack inference.

Overview
````````

The document can be broken down into 4 main parts:

    1. :doc:`MQTT Basics:<mqtt-basics>` The application messaging for this interface specification uses the well established MQTT and MQTT-SN protocols to interface with host applications or IoT cloud platforms. By using MQTT and MQTT-SN protocols, it is possible to reuse the code and the overall code footprint can be minimized for the devices that have to retain dev-time and run-time protocol functionality. This section provides a brief overview of the MQTT protocol and architecture.
    2. :doc:`Implementation Guide:<mqtt-integration>`  Guide for implementing the portions of the spec necessary for live data streaming, local data collection (coming soon), and Knowledge Pack inference (coming soon).
    3. :doc:`MQTT TOPIC Glossary:<mqtt-topic-glossary>` A comprehensive API documentation for the MQTT Topics defined in the interface specification.
    4. :doc:`Integration Notes:<mqtt-topic-glossary>` Notes and tips from what we have learned working with the protocol.

It is recommended that a new user first review the MQTT Basics and then begin with the implementation guide. The guide walks through adding a sensor, integrating mqtt, and implementing live data streaming. Live data streaming is the minium requirement for integration within SensiML Toolkit. The MQTT TOPIC glossary should be used as a reference where necessary. For some topics, the integration notes include helpful tips as well. There is a reference code available for the SensorTile.box available  `here <https://bitbucket.org/sensimldevteam/sensortile_box/src/master/ST-Apps/sensortilebox_ai_mqttsn_app/src/sensor_config.c>`_.

Objectives
`````````````

The goal of this specification is to define an industry-standard protocol for exposing the hardware capability of sensor devices. At a minimum, this involves basic connectivity for controlling the collection and data logging of sensor data from the hardware platform.

In many EVBs, beyond the processor itself, there can be one or more onboard sensors integrated at the package and/or board level and made integral to the EVB software development kit (SDK) offered.  The specification is designed to be flexible enough so that in these instances, the same firmware can control and configure all sensors.

By implementing this spec, OEMs can offer SensiML as an end-to-end software platform with their HDKs. Also, systems integrators and software application developers who seek to build upon the toolkit to create full solutions for end-users can utilize this specification to incorporate SensiML capability into their embedded IoT products. If you are interested in becoming an officially supported hardware partner of SensiML contact us <https://sensiml.com/contact/>.



