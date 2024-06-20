
=================
Error Handling
=================

MQTT v5 has a scheme for reporting errors, however it is not well supported by various solutions, therefore we rely on MQTT V3.1.1 level support.  Protocol errors are handled by the protocol layer, not the MQTT V3.1.1 mechanism.

Application Layer Errors
`````````````````````````

Application layer errors are divided into parameter errors and runtime errors.

Application errors are managed using these commands: TOPIC_SYS_ERROR, and TOPIC_SYS_STATUS_RSP.

Parameter Errors
`````````````````

Application Layer Parameter errors occur as a result of a command. For example, the host may try to select an unsupported sensor configuration.

A typical response might be TOPIC_SYS_ERROR with the error code EINVAL. The exact error number used is implementation-specific.

Runtime Errors
```````````````

Runtime errors occur spontaneously. For example, while collecting (storing) data to the SD Card, the card may fill up resulting in ENOSPC – No available space error. Or perhaps the device is mounted on something that vibrates and the SD CARD vibrates loose resulting in an EIO error.
