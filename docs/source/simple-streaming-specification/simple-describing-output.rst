======================
Describing Output Data
======================

The Simple Streaming Interface requires only two things:

1. :ref:`Describing the output format <simple-description-output>`
2. :doc:`Sending the output data <simple-output-data>`

We'll cover the first point here.

.. _simple-description-output:

Description Output Format
-------------------------

Describing how your output data will arrive at the Data Studio is done using a simple JSON format. This lays out the sample rate and column order of data that will be streaming from a device.

An example of JSON data for the :doc:`Arduino Nano 33<../firmware/arduino-nano33/arduino-nano33>` configured for IMU streaming is shown below:

.. code-block:: json

    {
        "sample_rate":476,

        "version":1,

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

**Version**

The version should be either 1 or 2. Version 2 supports a sync protocol with a simple CRC for data integrity. If no version is supplied, the Data Studio will assume version 1.

**Sample Rate**

Sample rate is the first item defined. Currently, this specification supports one sample rate at a time. Sensors that run slower, but are included in this list, are expected to be over-sampled to match the highest sample rate.

**Samples Per Packet**

Samples per packet is used to tell the Data Studio how much data will be received in a given packet. The default used by the Data Studio is 6.

.. note::

    The "samples" in "samples_per_packet" refers to a single row of data, where a row contains all of the columns referenced in the column location field of the JSON decription. 
    In the example :ref:`up above<simple-description-output>`, 10 samples of data for a device outputting 6 columns of sensor data would contain all of the following data:
    
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300
        #. -10, -8,-2, 1003, 1020, 1300 

**Column Location**

Column Location describes both the name of the given sensor column and its location in the output data stream. With the above description, we can expect 6-axis IMU data. The Data Studio will assume the column locations are matched to this dictionary description. If they are mismatched, it could lead to incorrect data being represented in a model.

Creating The Description JSON in Firmware
-----------------------------------------

As this interface is intended to target Arduino and similar maker-friendly boards, we intend for existing libraries for JSON creation to be used. The :doc:`Arduino Nano 33 <../firmware/arduino-nano33/arduino-nano33>` code provided uses `ArduinoJson <https://arduinojson.org/>`_ to build a JSON object, and then serialize that data for output.

The code snippet below creates the IMU JSON from our `GitHub repository for the Nano33 <https://github.com/sensiml/nano33_data_capture/>`_, based on what was configured at compile-time. It also sets the sensor up for use.

.. code-block:: cpp

    int setup_imu(JsonDocument& config_message, int column_start)
    {
        int column_index = column_start;
        if (!IMU.begin())  // Initialize IMU sensor
        {
            Serial.println("Failed to initialize IMU!");
            while (1)
                ;
        }
        // Set units.
        IMU.accelUnit  = METERPERSECOND2;
        IMU.gyroUnit   = DEGREEPERSECOND;
        IMU.magnetUnit = MICROTESLA;

    #if ENABLE_ACCEL && (ENABLE_GYRO == 0)
        IMU.setAccelODR(ACCEL_GYRO_DEFAULT_ODR);
        IMU.setGyroODR(ACCEL_GYRO_ODR_OFF);

        config_message["column_location"]["AccelerometerX"] = column_index++;
        config_message["column_location"]["AccelerometerY"] = column_index++;
        config_message["column_location"]["AccelerometerZ"] = column_index++;
        actual_odr                                          = get_acc_gyro_odr();
        config_message["sample_rate"]                       = actual_odr;

    #elif (ENABLE_ACCEL && ENABLE_GYRO)
        IMU.setAccelODR(ACCEL_GYRO_DEFAULT_ODR);
        IMU.setGyroODR(ACCEL_GYRO_DEFAULT_ODR);
        actual_odr                                          = get_acc_gyro_odr();
        config_message["sample_rate"]                       = actual_odr;
        config_message["column_location"]["AccelerometerX"] = column_index++;
        config_message["column_location"]["AccelerometerY"] = column_index++;
        config_message["column_location"]["AccelerometerZ"] = column_index++;
        config_message["column_location"]["GyroscopeX"]     = column_index++;
        config_message["column_location"]["GyroscopeY"]     = column_index++;
        config_message["column_location"]["GyroscopeZ"]     = column_index++;
        actual_odr                                          = get_acc_gyro_odr();
    #else  // gyro only
        IMU.setAccelODR(ACCEL_GYRO_ODR_OFF);
        IMU.setGyroODR(ACCEL_GYRO_DEFAULT_ODR);
        actual_odr                                      = get_acc_gyro_odr();
        config_message["sample_rate"]                   = actual_odr;
        config_message["column_location"]["GyroscopeX"] = column_index++;
        config_message["column_location"]["GyroscopeY"] = column_index++;
        config_message["column_location"]["GyroscopeZ"] = column_index++;
    #endif

    #if ENABLE_MAG
        IMU.setMagnetODR(MAG_DEFAULT_ODR);
        config_message["column_location"]["MagnetometerX"] = column_index++;
        config_message["column_location"]["MagnetometerY"] = column_index++;
        config_message["column_location"]["MagnetometerZ"] = column_index++;
    #else
        IMU.setMagnetODR(0);
    #endif
        IMU.setContinuousMode();
        return column_index;
    }


Sending Description over Serial
-------------------------------

For a serial port, we recommend continuously sending this data out. Upon connection, the Data Studio will send a "connect" string back to the device. This should cause the device to start streaming out data.
