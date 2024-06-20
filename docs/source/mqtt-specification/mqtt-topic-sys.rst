
TOPIC_SYS
---------

All TOPIC_SYS messages are for system level configuration and reporting.

TOPIC_SYS_ALL_STOP
````````````````````
:NAME:			TOPIC_SYS_ALL_STOP
:DIRECTION:		HOST->TARGET
:REPLY:			no reply
:MQTT_URL:		sensiml/sys/all/stop
:FIELDS:		Empty – there is no payload.

:DESCRIPTION:
    The host can use this command any time to force the device into a known state.
    This is a generic stop command to the device. Upon receipt, the device:
    •	Stop streaming data (TOPIC_LIVE_STOP)
    •	Clears all sensor configuration (TOPIC_SENSOR_CLR)
    •	Stops other implementation specific activities as needed.

    After receiving this message, the device periodically sends MQTT-SN pings as needed when it is connected to the network.

TOPIC_SYS_DEVICE_UUIDS_REQ
```````````````````````````

:NAME:			TOPIC_SYS_DEVICE_UUIDS_REQ
:DIRECTION:		HOST->TARGET
:REPLY:			TOPIC_SYS_DEVICE_UUIDS_RSP
:MQTT_URL:		sensiml/sys/device/uuids/req
:FIELDS:		Empty – there is no payload.
:DESCRIPTION:   This command requests the device publish the two UUID values — DCLASS_UUID and DSPECIFIC_UUID. See Page 24.
:ALSO SEE:
    •	TOPIC_SYS_DEVICE_UUIDS_RSP
    •	TOPIC_SYS_VERSION_RSP
    •	TOPIC_SYS_COMPDATETIME_REQ
    •	TOPIC_SYS_COMPDATETIME_RSP


TOPIC_SYS_DEVICE_UUIDS_RSP
```````````````````````````
:NAME:			TOPIC_SYS_DEVICE_UUIDS_RSP
:DIRECTION:		TARGET->HOST
:REQUEST:		TOPIC_SYS_DEVICE_UUIDS_REQ
:MQTT_URL:		sensiml/sys/device/uuids/rsp
:FIELDS:

+------------------------+-----------+----------------------------------------+
| Field Name             | Type      | Description                            |
+========================+===========+========================================+
| DCLASS_UUID            | BYTES(16) | This UUID is for the device class.     |
+------------------------+-----------+----------------------------------------+
| DUNIQUE_UUID           | BYTES(16) | This UUID is for device specific UUID. |
+------------------------+-----------+----------------------------------------+
| TOTAL                  | BYTES(4)  |                                        |
+------------------------+-----------+----------------------------------------+

:DESCRIPTION:
    This response contains DCLASS_UUID and DUNIQUE_UUID.

    The DUNIQUE_UUID models a board serial number. The combined DCLASS_UUID + DUNIQUE_UUID must be unique.

    For the implementation recommendations, see 15.1 Notes for TOPIC_SYS_DEVICE_UUIDS in PART 2.
:ALSO SEE:
    •	TOPIC_SYS_DEVICE_UUIDS_REQ
    •	TOPIC_SYS_VERSION_RSP
    •	TOPIC_SYS_COMPDATETIME_REQ
    •	TOPIC_SYS_COMPDATETIME_RSP

TOPIC_SYS_VERSION_REQ
``````````````````````
:NAME:			TOPIC_SYS_VERSION_REQ
:DIRECTION:		HOST->TARGET
:REPLY:			TOPIC_SYS_VERSION_RSP
:MQTT_URL:		sensiml/sys/version/req
:FIELDS:		Empty – there is no payload.
:DESCRIPTION:
    This command requests the device publish the SW version.

:ALSO SEE:
    •	TOPIC_SYS_VERSION_RSP
    •	TOPIC_SYS_COMPDATETIME_REQ
    •	TOPIC_SYS_COMPDATETIME_RSP


TOPIC_SYS_VERSION_RSP
`````````````````````
:NAME:			TOPIC_SYS_VERSION_RSP
:DIRECTION:		TARGET->HOST
:REQUEST:		TOPIC_SYS_VERSION_REQ
:MQTT_URL:		sensiml/sys/version/rsp
:FIELDS:

+------------+----------+-------------------------------------------+
| Field Name | Type     | Description                               |
+============+==========+===========================================+
| STRING     | ASCII(N) | This reply should be 10 to 20 bytes long. |
+------------+----------+-------------------------------------------+
| TOTAL      | N        | This UUID is for device specific UUID.    |
+------------+----------+-------------------------------------------+

:DESCRIPTION:
    This command retrieves a short ASCII string identifying the current device firmware version.
    The version string gives the current firmware version information.

:ALSO SEE:
    •	TOPIC_SYS_VERSION_REQ
    •	TOPIC_SYS_COMPDATETIME_REQ
    •	TOPIC_SYS_COMPDATETIME_RSP

TOPIC_SYS_COMPDATETIME_REQ
``````````````````````````
:NAME:			TOPIC_SYS_COMPDATETIME_REQ
:DIRECTION:		HOST->TARGET
:REPLY:			TOPIC_SYS_COMPDATETIME_RSP
:MQTT_URL:		sensiml/sys/compdatetime/req
:FIELDS:		Empty – there is no payload.
:DESCRIPTION:
    This command requests the device publish the compile date and time of the firmware.
:ALSO SEE:
    •	TOPIC_SYS_VERSION_RSP
    •	TOPIC_SYS_COMPDATETIME_RSP

TOPIC_SYS_COMPDATETIME_RSP
``````````````````````````
:NAME:			TOPIC_SYS_COMPDATETIME_RSP
:DIRECTION:		TARGET->HOST
:REQUEST:		TOPIC_SYS_COMPDATETIME_REQ
:MQTT_URL:		sensiml/sys/compdatetime/rsp
:FIELDS:

+------------+----------+-------------------------------------------+
| Field Name | Type     | Description                               |
+============+==========+===========================================+
| STRING     | ASCII(N) | This reply should be 10 to 20 bytes long. |
+------------+----------+-------------------------------------------+
| TOTAL      | N        | This UUID is for device specific UUID.    |
+------------+----------+-------------------------------------------+

:DESCRIPTION:
    This command retrieves the firmware build date and time to help with software identification.
    See the Notes for TOPIC_SYS_COMPDATETIME
:ALSO SEE:
    •	TOPIC_SYS_VERSION_REQ
    •	TOPIC_SYS_COMPDATETIME_REQ


TOPIC_SYS_STATUS_REQ
````````````````````
:NAME:			TOPIC_SYS_STATUS_REQ
:DIRECTION:		HOST->TARGET
:REPLY:			TOPIC_SYS_STATUS_RSP
:MQTT_URL:		sensiml/sys/status/req
:FIELDS:		Empty – there is no payload.
:DESCRIPTION:
    This command requests the device publish TOPIC_SYS_STATUS_RSP
:ALSO SEE:
    •	TOPIC_SYS_STATUS_RSP
    •	TOPIC_SYS_ERROR

TOPIC_SYS_STATUS_RSP
````````````````````
:NAME:			TOPIC_SYS_STATUS_RSP
:DIRECTION:		TARGET->HOST
:REQUEST:		TOPIC_SYS_STATUS_REQ
:MQTT_URL:		sensiml/sys/status/rsp
:FIELDS:
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | Field Name           | Type     | Description                                                                                |
    +======================+==========+============================================================================================+
    | BYTES_SAVED          | U32      | Counts the bytes written to the sensor data file. Sensor data blocks are 4K bytes. Zeroed  |
    |                      |          | using TOPIC_SYS_STATUS_CLR.                                                                |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | BIT_FLAGS            | U32      | See the following table for the list of bits.                                              |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | RX_COUNT             | U16      | Number of messages received (not including duplicates), always increasing, rolls over at 0 |
    |                      |          | xffff.  This value is reset to 0 at power up/reset.                                        |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | TX_COUNT             | U16      | Number of messages transmitted (not including duplicates) always increasing, rolls over at |
    |                      |          | 0xffff. This value is reset to 0 at power up/reset.                                        |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | LIVE_OE_COUNT        | U16      | Number of TOPIC_LIVE_<various> messages dropped because the transport cannot keep up (over |
    |                      |          | run error). Zeroed using TOPIC_SYS_STATUS_CLR                                              |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | COLLECT_OE_COUNT     | U16      | Number of data blocks dropped that could not be saved to the SD card because the total sen |
    |                      |          | sor data rate was too high.  Zeroed using TOPIC_SYS_STATUS_CLR                             |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | STICKY_ERROR_CODE    | U8       | Sticky error code, 0 indicates no error. See the following table for details. Zeroed using |
    |                      |          | TOPIC_SYS_STATUS_CLR to clear status                                                       |
    +----------------------+----------+--------------------------------------------------------------------------------------------+
    | ERROR_COUNT          | U8       | Error counter, always increasing may roll over after 0xFF, TOPIC_SYS_STATUS_CLR. This is a |
    |                      |          | n indication that multiple errors occurred and the STICKY_ERROR_CODE captured only the fir |
    |                      |          | st.                                                                                        |
    +----------------------+----------+--------------------------------------------------------------------------------------------+

:DESCRIPTION:
    Not all values are zeroed by issuing the TOPIC_SYS_STATUS_CLR command. The following table gives additional details of specific fields.

:BIT_FLAGS:

    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    | Bit Number           | Description / Notes                                                                                                      |
    +======================+==========================================================================================================================+
    | 0                    | COLLECT_ACTIVE If 1, then data is being collected/saved to the storage medium (ie., SD card). This bit auto clears       |
    |                      | if storage error occurs. For example, the SD card is removed, not present, or full.Set:  TOPIC_COLLECT_STARTClear: TO    |
    |                      | PIC_COLLECT_STOP, or TOPIC_SYS_ALL_STOP                                                                                  |
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    | 1                    | LIVE_STREAM_ACTIVEIf 1, then LIVE_STREAM sensor messages are active. TOPIC_LIVE_STOP, or                                 |
    |                      | Set:  TOPIC_LIVE_START Clear:  TOPIC_SYS_ALL_STOP                                                                        |
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    | 2                    | LIVE_STREAM_RECOG_ACTIVEIf 1, then recognition results are live streamed.Set: TOPIC_RECOG_STARTClear: TOPIC_RECOG_STOP,  |
    |                      | or TOPIC_SYS_ALL_STOP                                                                                                    |
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+
    | 3..31                | Reserved / Future                                                                                                        |
    +----------------------+--------------------------------------------------------------------------------------------------------------------------+

    :STICKY_ERROR_CODE:
        ZERO indicates no error, non-zero indicates error.
        At startup (or after issuing the **TOPIC_SYS_STATUS_CLR** command) the **STICKY_ERROR_CODE** is zero (0).

        When an error occurs:
            •	Only the first (0 to non-zero) transition is captured.
            •	The status bit **ANY_ERROR** is set.
            •	Depending on the error, other error bits are set. For example, collection and live stream.
            •	The status byte: **ERROR_COUNT** is increased.
        Notes:
            •	If **ERROR_COUNT** is greater than 1, more than 1 error has occurred.
            •	If the error is related to data collection (saving data to the storage medium), the **BITFLAG**: **COLLECT_ACTIVE** auto clears.

    :STICKY_ERROR_CODE Values:

    +----------------------+----------------------+----------------------------------------------------+
    | STICKY_ERROR_CODE    | Unix Symbolic Name   | Description / Notes                                |
    +======================+======================+====================================================+
    | 1                    | EPERM                | Operation not permitted                            |
    +----------------------+----------------------+----------------------------------------------------+
    | 2                    | ENOENT               | File not found (see STORAGE commands)              |
    +----------------------+----------------------+----------------------------------------------------+
    | 5                    | EIO                  | IO error (SD Card or sensor)                       |
    +----------------------+----------------------+----------------------------------------------------+
    | 16                   | EBUSY                | Device is busy                                     |
    +----------------------+----------------------+----------------------------------------------------+
    | 19                   | ENODEV               | No such device/sensor                              |
    +----------------------+----------------------+----------------------------------------------------+
    | 22                   | EINVAL               | Invalid parameter                                  |
    +----------------------+----------------------+----------------------------------------------------+
    | 30                   | EROFS                | Read only file system                              |
    +----------------------+----------------------+----------------------------------------------------+
    | 60                   | ETIMEDOUT            | Timeout                                            |
    +----------------------+----------------------+----------------------------------------------------+
    | 63                   | ENAMETOOLONG         | Filename too long                                  |
    +----------------------+----------------------+----------------------------------------------------+
    | 70                   | ESTALE               | File operation is stale (see STORAGE commands)     |
    +----------------------+----------------------+----------------------------------------------------+
    | 78                   | ENOSYS               | Feature not implemented                            |
    +----------------------+----------------------+----------------------------------------------------+
    | 85                   | ENOMEDIUM            | No medium found                                    |
    +----------------------+----------------------+----------------------------------------------------+
    | 91                   | ENOTSUP              | Not supported                                      |
    +----------------------+----------------------+----------------------------------------------------+

    See Notes for **TOPIC_SYS_STATUS_SP** for an implementation note and example.

:ALSO SEE:
    •	TOPIC_SYS_STATUS_REQ
    •	TOPIC_SYS_ERROR (which has extended error information)

TOPIC_SYS_STATUS_CLR
````````````````````
:NAME:			TOPIC_SYS_STATUS_CLR
:DIRECTION:		HOST->TARGET
:REPLY:			no reply
:MQTT_URL:		sensiml/sys/status/clr
:FIELDS:		Empty – there is no payload.
:DESCRIPTION:
    This command clears all sticky values shown in the **TOPIC_SYS_STATUS_RSP**. For more information, see **TOPIC_SYS_STATUS_RSP**. It clears all error counts and status counts.
:ALSO SEE:
    •	TOPIC_SYS_STATUS_RSP
    •	TOPIC_SYS_ERROR

TOPIC_SYS_REBOOT
`````````````````
:NAME:			TOPIC_SYS_REBOOT
:DIRECTION:		HOST->TARGET
:REPLY:			no reply
:MQTT_URL:		sensiml/sys/reboot
:FIELDS:
    +------------+----------+-----------------------------------------------+
    | Field Name | Type     | Description                                   |
    +============+==========+===============================================+
    | NEWAPP     | ASCII(N) | This string provides instructions for device. |
    +------------+----------+-----------------------------------------------+
    | TOTAL      | N        | This UUID is for device specific UUID.        |
    +------------+----------+-----------------------------------------------+
:DESCRIPTION:
    This command is used to power-cycle or reset or re-flash the device.

    **Requirement:** All devices must support the case of N is 0 (no string). That is, the device must reset if it receives this message.

    **Optional:** If N is not 0 (a string is provided), the NEWAPP string instructs the device to re-flash modify its configuration or re-flash itself with the image specified by the NEWAPP field.
:ALSO SEE:
    •	TOPIC_SYS_ALL_STOP
    •	TOPIC_STORAGE_PUT

TOPIC_SYS_ERROR
````````````````
:NAME:			TOPIC_SYS_ERROR
:DIRECTION:		TARGET->HOST
:REPLY:			no reply
:MQTT_URL:		sensiml/sys/error
:FIELDS:
    +----------------------+-------+----------------------------------------------------------------------------------+
    | Field Name           | Type  | Description                                                                      |
    +======================+=======+==================================================================================+
    | MSG_ID               | U16   | Big Endian MQTT message sequence number associated with this error.              |
    +----------------------+-------+----------------------------------------------------------------------------------+
    | DYN_TOPIC_ID         | U16   | Dynamic MQTT-SN Topic ID for this message.                                       |
    +----------------------+-------+----------------------------------------------------------------------------------+
    | FIXED_TOPIC_ID       | U16   | Fixed device specific MQTT-SN topic ID.                                          |
    +----------------------+-------+----------------------------------------------------------------------------------+
    | STICKY_ERROR_CODE    | U8    | The value of the STICKY_ERROR_CODE.                                              |
    +----------------------+-------+----------------------------------------------------------------------------------+
    | EXTENDED_ERROR       | U32   | Transmitted big Endian that is implementation defined and is used to provide mor |
    |                      |       | e details about the specific error.                                              |
    +----------------------+-------+----------------------------------------------------------------------------------+
    | TOTAL                | 11    |                                                                                  |
    +----------------------+-------+----------------------------------------------------------------------------------+

:DESCRIPTION:
    :PUBLISHED:
        •	In response to a command containing invalid data.
        •	Spontaneously by the device for reporting catastrophic conditions. For example, when the storage medium is full during data collection (saving the SD card).
    :ACTIONS:
        Each time a **TOPIC_SYS_ERROR** is attempted (which may fail to be delivered or get lost), the target must update the **TOPIC_SYS_STATUS_RSP** report fields.

        In this case, the target:
            •	Captures only the first STICKY_ERROR_CODE
            •	Increments the ERROR_COUNT field
            •	Set/Clear other BIT_FIELD bits as appropriate
    :OVERRUN ERRORS:
        Overrun errors (such as storage overrun and live stream) are not reported by this message. Overrun errors set bits only within the status. The host polls periodically using TOPIC_SYS_STATUS_REQ and finds the sticky error bits.

        If the message is NOT related to a specific message, the fields MSGID, DYN_TOPIC_ID and FIXED_TOPIC_ID are zero.

        If the topic is associated with a message, the MSGID field is the MQTT-SN Message ID number of the offending message.

        For example:
            •   **PIC_SENSOR_ADD**, for an invalid sensor id.
            •	**TOPIC_STORAGE_GET_START**, for a non-existing file.

        The **FIXED_TOPIC_ID** and **DYN_TOPIC_ID** represent the topic id of the offending message. The MQTT-SN allows two types of TOPIC ID numbers. See: MQTT-SN REGISTER.

        **DYNAMIC – DYN_TOPIC_ID** and **FIXED** (Predefined) -** FIXED_TOPIC_ID**

        If the device uses predefined topics – then the DYNAMIC and FIXED field hold the same value (the predefined topic id)

        If the device registers topics, then DYNAMIC and FIXED fields will be different. The FIXED field should be a firmware/implementation defined fixed value that can be used to identify the topic. The DYNAMIC field holds the dynamically assigned topic id as assigned by the gateway/broker.

        It is recommended that the **FIXED_TOPIC_ID** is a hard-coded value that is unique to each topic. It is assumed that the device has implementation specific numeric #define for each message that is used internally.  This value must be used for the FIXED_TOPIC_ID.

        This helps in tracing the messages during a debug session.

    :EXCEPTIONS:
        •	Invalid topics and protocol errors are handled at the protocol level, not using this method.
        •	Over run errors related to saving to the SD card are not reported using this method. For more information, see TOPIC_SYS_STATUS_RSP.
:ALSO SEE:
    •	TOPIC_SYS_STATUS_RSP
    •	TOPIC_SYS_STATUS_CLR
