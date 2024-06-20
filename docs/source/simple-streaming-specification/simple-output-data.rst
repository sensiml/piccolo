===================
Sending Output Data
===================


Sensor Data Output Format
-------------------------

The SensiML toolkit expect data to be sent as 16-bit signed integers. This is usually the raw output format for most ADCs and sensors.

The data coming out of the device should also match the order described in :doc:`the device description <simple-describing-output>`.

As with the JSON description, the following code from the `GitHub repository for the Nano33 <https://github.com/sensiml/nano33_data_capture/>`_ reads the IMU data in the order given, based on configuration at compile-time.

.. code-block:: cpp

    int update_imu(int startIndex)
    {
        int sensorRawIndex = startIndex;
        if (ENABLE_ACCEL)
        {
            IMU.readRawAccelInt16(sensorRawData[sensorRawIndex++],
                                sensorRawData[sensorRawIndex++],
                                sensorRawData[sensorRawIndex++]);
        }

        if (ENABLE_GYRO)
        {
            IMU.readRawGyroInt16(sensorRawData[sensorRawIndex++],
                                sensorRawData[sensorRawIndex++],
                                sensorRawData[sensorRawIndex++]);
        }

        if (ENABLE_MAG)
        {
            IMU.readRawMagnetInt16(sensorRawData[sensorRawIndex++],
                                sensorRawData[sensorRawIndex++],
                                sensorRawData[sensorRawIndex++]);
        }
        return sensorRawIndex;
    }


Sending Data over Serial
------------------------

Data should be sent over serial after a "connect" string is received while sending the JSON description. The serial port does not need to be read again on the device after this, until a system reset. However, the device can also listen for a "disconnect" string to do a soft restart of collection. If a "disconnect" is received, the device should start sending :doc:`the device description <simple-describing-output>`.

**Samples Per Packet**

Data should be sent in chunks of data, using the specified number of samples per packet used in :doc:`the device description <simple-describing-output>`. This can be done by filling a buffer until the number of samples is reached. In the case of audio, a single chunk of data is used as the number of samples.

.. _ssi-version-1-ref:

**Version 1**

On a serial port, data is output in chunks, depending on the sensor being used. For IMU data, multiple sensor readings are sent per chunk of data. For audio and higher sample rate data, the data is directly written out as it is sampled. There is no data integrity checking, and no sync of lost bytes/packets.

Data should be sent in chunks of data, using the specified number of samples per packet used in :doc:`the device description <simple-describing-output>`. This can be done by filling a buffer until the number of samples is reached. In the case of audio, a single chunk of data is used as the number of samples.

.. _ssi-version-2-ref:

**Version 2**


Version 2 data adds a small amount of overhead (10 bytes per transmission) in order to better sync data. The data will be placed in fields:

+-----------+---------+----------+---------+----------+--------------------------+----------------+
| Sync Byte | Length  | Reserved | Channel | Sequence | Channel Data             | 8-Bit Checksum |
+===========+=========+==========+=========+==========+==========================+================+
| S         | LL      | R        | C       | NNNN     | {D[0], D[1], ..., D[LL]} | CC             |
+-----------+---------+----------+---------+----------+--------------------------+----------------+
| 1 byte    | 2 bytes | 1 byte   | 1 byte  | 4 bytes  | Length bytes             | 1 byte         |
+-----------+---------+----------+---------+----------+--------------------------+----------------+

Data format for the above fields:

+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Item         | Length(bytes) | Data Format                                 | Notes                                                                           |
+==============+===============+=============================================+=================================================================================+
| Sync         | 1             |                                             | Constant Value 0xFF                                                             |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Length       | 2             | 16-bit Unsigned int in Little-Endian format | Length of channel data + 6 (Reserved, Channel, and Sequence header fields are   |
|              |               |                                             | included in the data packet Length calculation)                                 |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Reserved     | 1             | Unsigned 8-bit                              | Constant value 0x00                                                             |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Channel      | 1             | Unsigned 8-bit                              | Number indicates the type of data being transferred. Example: audio,            |
|              |               |                                             | IMU, recognition results, etc.                                                  |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Sequence     | 4             | 32-bit Unsigned int in Little-Endian format | Sequence Number is per channel                                                  |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Channel Data | Length        | 16-bit signed integer values                | Contains Samples Per Packet as described in device description                  |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+
| Checksum     | 1             |                                             | XOR of the LL bytes of data following the length field. Checksum =              |
|              |               |                                             | Reserved ^ Channel ^ Seq0 ^ Seq1 ^ Seq2 ^ Seq3 ^ D[0] ^ D[1] ^ D[2] ^ … ^ D[LL] |
+--------------+---------------+---------------------------------------------+---------------------------------------------------------------------------------+

.. note:: Length of the payload sensor data block should be equal to samples_per_packet (as defined in the JSON Output Format Description) x number of sensor data columns per sample x 2 bytes/data value  (example: a 6 sample data packet with 3-axes of accelerometer data would produce 6 x 3 x 2 = 36 bytes of channel data).

The sync byte allows the Data Studio to recover from dropped bytes or serial driver bit flipping that can sometimes occur, with little loss of data.

The channel will specify which channel data is coming through. This leaves open the possibility of sending recognition data or data of various sample rates through different channels. Currently, channel will default to 0

The sequence will be the number of packets sent on the current channel.

The length will be the length of the payload only, plus the reserved, channel, and sequence header fields which occupy an additional 6 bytes. Thus the length should be defined as the Channel Data size + 6.

The payload should contain the same samples per packet as described above.

The 8-bit checksum is computed as the XOR of the reserved header byte, channel header byte, four byte sequence number, and LL length data bytes CC = D[0] ^ D[1] ^ D[2] ^ … ^ D[LL]. This will also verify data integrity for the Data Studio. When there is a mismatch, the packet is dropped/not recorded.
