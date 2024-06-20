Sensor Data Streaming 
----------------------------------

We provide a sample SDK implementation with the SensorTile.box available `here <https://bitbucket.org/sensimldevteam/sensortile_box/src/master/ST-Apps/sensortilebox_ai_mqttsn_app/src/sensor_config.c>`_. The following steps reference this example. 

Implement Live Streaming TOPICS
````````````````````````````````

Now that you have verified that you can communicate with the host application, it is time to implement the topics that will allow you to stream raw data. To do this you will need to implement the following topics.  Example implementations for each topic are found in our repo. Descriptions of each topic are found bellow in the **TOPIC GLOSSARY**.


Required LIVE Topics
`````````````````````````
TOPIC_LIVE: Data Streaming Control

*	TOPIC_LIVE_SENSOR_LIST: List added sensors
*	TOPIC_LIVE_SET_RATE: Set rate to stream data at
*	TOP_LIVE_START: Start Streaming Data
*	TOP_LIVE_STOP: Stop Streaming Data
*	TOPIC_LIVE_RAW_DATA: Start sending streaming data over MQTT


Other Required Topics
``````````````````````

TOPIC_SYS: System configuration and reporting

* TOPIC_SYS_DEVICE_UUIDS: Get Device Id
* TOPIC_SYS_COMPDATETIME: Get device time
* TOPIC_SYS_VERSION: Get version of software running on firmware
* TOP_SYS_STATUS_CLR: Clear status messages
* TOP_SYS_STATUS: Read status messages

TOPIC_SENSOR: Sensor configuration and management

*	TOPIC_SENSOR_LIST: Return list of available sensors
*	TOPIC_SENSOR_CLR: Clear all loaded sensors
*	TOPIC_SENSOR_ADD: Add a sensor from list of available sensors
*   TOPIC_SENSOR_DONE:


Connect and Stream Data in the Data Studio
``````````````````````````````````````````

Finally, connect from the host application and verify that you able to connect, configure, and stream raw sensor data from your device. If you run into issues during the integration reach out to us as https://sensiml.com/support/
