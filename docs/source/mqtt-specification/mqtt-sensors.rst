
Adding Sensors
--------------------

 The Specification allows for flexibility in defining sensor configurations and sensor grouping. A developer must define the available sensors in the firmware as well as in the SSF plugin. The sensor is identified by a **SENSOR_ID** which is the id for a single **sensor cluster**. **sensor clusters** are groups of one or more **sensor channels**. The developer will also have the ability to define the parameters for the sensor in the specification.


Sensor Channel
````````````````

A **sensor channel** is defined as a single sensor data stream of 16-bit signed integers.

Examples:
	The left only channel of a stereo audio data stream.
	The x-axis value from a 3D accelerometer (ignoring the y and z axis values)

We are the three types of values used in a sensor channel:

    * **Raw** The raw count value from the sensor.
    * **Cooked**  The raw sensor value is transformed in some way, ie calibration or clipping.
    * **Engineering Value** ie. Converting Accelerometer to units of Force(m/s^2)

**Examples:**

A pressure sensor that outputs – 0 to 3.3V.

	* ID(A): The raw count as a 12-bit number. The 0 to 3.3V would be reported as 0x0000 to 0x0ffff
	* ID(B): The calibration corrected ADC count. The analog circuit may introduce an offset or scale error. Software may correct for this.
	* ID(C): A scaled pressure value. The software might “clamp” the signal value at some max or min value. For example, the software might clamp sensor that reports a percentage exactly in the range of 0% to 100% and not allow negative values.
	* ID(D): Engineering value in PSI.

Sensor Cluster
````````````````

The **sensor cluster** is defined as one or more sensor channels in a group and sampled at the same rate. Multiple Sensor channels may grouped, transformed, or manipulated to create useful SENSOR CLUSTERs.

SENSOR_ID
````````````````
A SENSOR_ID is defined as a 32-bit number that identifies one SENSOR CLUSTER.
For example, the Bosch BMI160 is a combined accelerometer and gyroscope sensor. In total, there are six sensor channels.  The implementation defines the number of SENSOR CLUSTERS and therefore SENSOR_IDs are used for this sensor.

In this case, the following combinations can be used:

	* Sensor ID (A) – All 6 sensor channels (accel X/Y/Z plus gyro X/Y/Z)
	* Sensor ID (B) – The accel X/Y/Z values – without the gyro values.
	* Sensor ID (C) - The gryo X/Y/Z values – without the accel values.
	* An implementation might also create other combinations ie: X&Y no Z.

Sensor Settings
````````````````
Every sensor must have a sample rate (ODR) set and can have one or more secondary settings.

.. note::

	All sensors within one **SENSOR_CLUSTER** must use the same data rate.

The secondary settings typically includes information about the range for the sensor but can include any other necessary property for your sensor.

**Examples:**

Secondary configuration may include:

    * The input data range, example: Accelerometers often have +/-2G, +/-4G, etc.
    * Input configuration: ADCs may operate in unipolar (0...+V) or bi-polar (-V to +V)
    * Input values may be raw or cooked. For an ADC, raw means the actual binary value from the ADC, in contrast cooked is the converted value. For example, if the sensor measures pressure in kilopascals, the raw ADC count is cooked, giving kilopascal values.

During development, the engineer collecting data to create models often needs to experiment, change settings, try something else. In addition, sometimes different, or additional sensors may be added to the mix. Therefore, for collecting data, sensor configuration is highly variable. Its important to spend time talking with your team about what sort of settings they will need beforehand to make sure you are supporting their use case.


Create a sensor configuration
``````````````````````````````

A Sensor Configuration initializes and configures the sensor that you will be streaming data from. We provide implementations specific to the sensors available on the SensorTile.box `here <https://bitbucket.org/sensimldevteam/sensortile_box/src/master/ST-Apps/sensortilebox_ai_mqttsn_app/src/sensor_config.c>`__. You will need to implement the drivers for your specific sensor.


Create a Device Plugin for the Data Studio
``````````````````````````````````````````

To interface with the SensiML Data Studio, a developer needs to define a **Device Plugin** via a **.SSF** file. The .SSF file is a JSON-formatted file, which the Data Studio uses to create an interface for configuring the device. This **.SSF** plugin describes the available sensors and how to connect to your board.

The documentation for creating the **.SSF** plugin file is `here <https://sensiml.com/documentation/data-studio/adding-custom-device-firmware.html>`__. The Data Studio parses this to create a custom user-interface from which you can configurate your sensor prior to data collection.


Required Sensor Commands
````````````````````````


TOPIC_SENSOR: Sensor configuration and management

*	TOPIC_SENSOR_LIST: Return list of available sensors
*	TOPIC_SENSOR_CLR: Clear all loaded sensors
*	TOPIC_SENSOR_ADD: Add a sensor from list of available sensors
*   TOPIC_SENSOR_DONE:


Configuration Sequence
```````````````````````

The configuration information is be provided to the SensiML applications. On connecting the SensiML Applications will:

	1. Use **TOPIC_SYS_UUID_REQ** to obtain the **DCLASS_UUID** for the device.
	2. Use the **TOPIC_SENSOR_LIST_REQ**, to obtain a list of supported **SENSOR_IDs**.
	3. Using the above – locate the specific .SSF plugin file for the selected device.
	4. The content of the .SSF plugin file – are used by the host applications to create dialog boxes so that the engineer can configure sensors supported by the board.



