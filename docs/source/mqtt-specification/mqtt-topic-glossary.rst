===================
Topic Glossary
===================

The Topic glossary goes into detail covering the implementation of specific MQTT Topics. There are three main types of TOPICS

•	**SYS**: Handles system level configuration, reporting, error messages
•	**SENSOR**: List, Add, configuration from available sensors.
•	**LIVE**: Stream raw data from configured sensors to the host application for data collection



Topic Schema
----------------------

MQTT Topic **Namespace/Major/Minor**

All MQTT topic strings are prefixed with **sensiml/**. This defines a namespace for use by the SensiML tools and allows the extension of protocol by prefixing commands.

Customers, partners, or third-party vendors can create additional commands within their own namespace.

The **sensiml/** name space is divided into **sensiml/<MAJOR>/<MINOR>** subtopics.

If a topic change is required, either (a) a new topic name will be created, or (b) a digit will be added to the end of the MINOR topic name.

    For example:  /sensiml/sys/status/req might become /sensiml/sys/status2/req

+----------------+-----------------+-----------------------------------------------------------------+
| Major  Section | Topic String    | Description / Notes                                             |
+================+=================+=================================================================+
| TOPIC_SYS      | sensiml/sys/    | Software version, date/time, status                             |
+----------------+-----------------+-----------------------------------------------------------------+
| TOPIC_LIVE     | sensiml/live/   | Transmitting raw sensor data over the air (or wire) to the DS.  |
+----------------+-----------------+-----------------------------------------------------------------+
| TOPIC_SENSOR   | sensiml/sensor/ | Configure and control the sensors.                              |
+----------------+-----------------+-----------------------------------------------------------------+


Request & Responses (REQ/RSP)
------------------------------

The MQTT/MQTT-SN protocol is a publish/subscribe protocol. To create a command response pattern, we overlay the publish topics with a pair of **REQ** and **RSP** packets.
For example, the message **TOPIC_SENSOR_LIST_REQ** requests the target device publish **TOPIC_SENSOR_LIST_RSP** listing the available **SENSORIDs** that are currently supported by the target firmware.

Protocol Byte Order
-------------------------

At the protocol level, MQTT and MQTT-SN use network byte order. Therefore, all parameters for all topics are transmitted Big Endian, MSB First, also known as the network byte order.
Sensor values are 16-bit signed integers. The live-streaming sensor data should be sent in the same order as that of the target device.
An Arm Cortex M3 MCU uses little endian, LSB first - therefore, it transmits data in the little-endian order. See the device specific JSON file for details.


Topic documentation Convention
--------------------------------

MQTT-SN Publish topic is an addressing format that allows MQTT-SN clients to share information through an MQTT broker. The publish message format is as follows:

    Length (1 or 3), MsgType(1), Flags(1), TopicId(2), MsgId(2), Payload(x).

    If the total length is less than 256 bytes, the Length field is exactly 1 byte.

    If the total length is more than 256 bytes, the length field is exactly 3 bytes.

The Fields in the format described below is referred to the payload of the publish message. Each topic command, or response is described in the format, in a way similar to the Unix man page, as follows:

:**TOPIC_NAME**:
    :**NAME**:        Symbolic name for the message used in documentation.
    :**DIRECTION**:   HOST->TARGET, or TARGET->HOST
    :**REPLY**:       The name of the reply (if this is a request)
    :**REQUEST**:     The name of the request (if this is a response)
    :**MQTT_URL**:    URI string used in the MQTT transaction
    :**TOTAL**:	      <value> The total or maximum length of the packet in bytes. The Total/Max row is not part of the fields that will be included in the payload.
    :**FIELDS**:      Same as: <Other Name/Command> or Empty Or a table that is similar to the following table

    +------------+--------------------------------------+--------------------------------------------------------------------------------------------------------------------+
    | Field Name | Type                                 | Description                                                                                                        |
    +============+======================================+====================================================================================================================+
    | Name Here  | U8, S8, U16, S16, U32, S32, U64, S64 | * signed S, or unsigned U.                                                                                         |
    |            |                                      | * Always transmitted BIG ENDIAN (MSB first)                                                                        |
    +------------+--------------------------------------+--------------------------------------------------------------------------------------------------------------------+
    | Name Here  | * BYTES(N)                           |                                                                                                                    |
    |            | * ASCII(N)                           |                                                                                                                    |
    +------------+--------------------------------------+--------------------------------------------------------------------------------------------------------------------+

    :**DESCRIPTION**:  Paragraph describing the purpose of the packet.
    :**THER HEADINGS**: As required by the specific item.
    :**ALSO SEE**:  List of other messages that are related to this message.


.. include:: mqtt-topic-sys.rst
.. include:: mqtt-topic-sensor.rst
.. include:: mqtt-topic-live.rst
