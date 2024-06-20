.. meta::
   :title: Streaming Sensor Data to the Data Studio over Wi-Fi
   :description: How to configure the Open Gateway to stream sensor data over Wi-Fi to the Data Studio

Streaming Sensor Data to the Data Studio over Wi-Fi
---------------------------------------------------

In some cases, you may want to use a gateway to retrieve sensor data from your device as an intermediary between the Data Studio. The SensiML Open Gateway can be used for this.

Configuring the Open Gateway for Sensor Streaming
`````````````````````````````````````````````````

These instructions use the :doc:`Nano33 BLE Sense <../firmware/arduino-nano33/arduino-nano33>` as an example device, but any edge node that implements the protocol can be used. Connections can be made over Serial, TCPIP, and BLE.

We assume you have already followed instructions for installing SensiML Open Gateway found in the :doc:`Open Gateway Setup Guide<installation-setup-instructions>`. After starting the SensiML Open Gateway you will need to configure it to connect to the Nano33 over BLE. To configure the gateway:

1. Open the **Home** page
2. Select **Device Mode: Data Capture**
3. Select **Connection Type: BLE**
4. Click Scan -> Select Nano33 
5. Click the **Connect to Device** Button

.. image:: https://github.com/sensiml/open-gateway/raw/main/img/configure.png


6. Your device should now show connected

.. image:: https://github.com/sensiml/open-gateway/raw/main/img/status.png


7. Open the **Test Mode** page and start streaming

.. image:: https://github.com/sensiml/open-gateway/raw/main/img/stream.png


Connecting the Data Studio to the Open Gateway
``````````````````````````````````````````````

Now that we have configured the SensiML Open Gateway application, we can start streaming data into the SensiML Data Studio. 

.. include:: ../data-studio/streaming-over-wifi-shared.rst