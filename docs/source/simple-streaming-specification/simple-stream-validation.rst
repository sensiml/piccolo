========================
Validating Device Output
========================

In order to validate that your device is outputting data in the expected format for Simple Streaming, we have written a validation script to verify that the connection string being sent matches a configuration available in your :ref:`SSF file<example_ssf_files>`.

The script is a simple Python script that is used to ensure the device is sending out a proper configuration and can listen for the connect/disconnect strings.

Prerequisites for Python Script
-------------------------------

The script requires Python 3.6 or higher, and requires ``pyserial`` and ``colorama`` to run:

.. code:: bash

    pip install pyserial colorama


Running the Script
------------------

Download the script here: :download:`simple-stream-validator.py <file/simple-stream-validator.py>`

To run the script, it's a simple command:

.. code:: python

    python simple_stream_validator.py -f <SSF_FILE> -p <COM_PORT>
    # Replace <SSF_FILE> with the path to the SSF file used for Data Studio import
    # Replace <COM_PORT> with the COM/serial port of your device (e.g. COM27 on Windows, /dev/ttyACM0 on Linux).


Sample Output
-------------

Running the script will give you a similar output if all checks pass:

.. include:: file/sample-output.txt
    :literal:
    :encoding: utf-16


If there are any errors, each step will stop until the error is corrected.


**Invalid SSF File Error**

.. include:: file/error-ssf-file.txt
    :literal:
    :encoding: utf-16


**Invalid Sample Rate Error**

.. include:: file/error-sample-rate.txt
    :literal:
    :encoding: utf-16


**Invalid Sensor Columns Error**

.. include:: file/error-sensor-columns.txt
    :literal:
    :encoding: utf-16

