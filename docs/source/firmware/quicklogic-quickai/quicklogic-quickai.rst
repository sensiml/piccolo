.. meta::
   :title: Firmware - QuickLogic QuickAI
   :description: Guide for flashing QuickLogic QuickAI firmware

==================
QuickLogic QuickAI
==================

Data Collection Firmware
------------------------

QuickLogic QuickAI binaries and flash instructions can be found at http://quickai.quicklogic.com

.. list-table:: QuickLogic QuickAI pre-built Data Collection Firmware
   :widths: 35 25 35 10
   :header-rows: 1

   * - Sensors
     - Protocol
     - Download
     - Version
   * - Accelerometer (1660, 833, 416, 208, 104, 52, 26), Audio (16KHz), LTC1859 ADC (100Khz, 16Khz, 8Khz, 4Khz, 2Khz, 1Khz)
     - BLE Protocol
     - :download:`quickai-data-collection.bin <file/ble_app_quickAI_merced_v5.hex>`
     - v1.3

Viewing Knowledge Pack Recognition Results
------------------------------------------

When a Knowledge Pack is flashed on the board, the classification results can be viewed by connecting to the virtual COM port in a terminal application. Follow the steps below for viewing the recognition results:

1. Plug in your QuickAI device via serial USB cable
2. Open a terminal emulator (such as Tera Term)
3. Set your serial speed to 115200
4. Create a new connection to your QuickAI COM port

You will now see classification results printed in the terminal