.. meta::
   :title: Knowledge Packs / Model Firmware - Reading BLE Characteristics
   :description: How to read BLE characteristics from a Knowledge Pack

=======================================================
Reading SensiML BLE Characteristics in your application
=======================================================

BLE Characteristic UUIDs
------------------------

SensiML Knowledge Packs with BLE enabled will print a class id and model id over the following BLE characteristic UUIDs. If you have your own application to read these characteristics all you need are the UUIDs below.

    ``SENSIML_EVENT_SERVICE_UUID = 534D1100-9B35-4933-9B10-52FFA9740042``
    ``SENSIML_EVENT_CHARACTERISTIC_UUID = 534D1101-9B35-4933-9B10-52FFA9740042``

**Note:**

If you are using a QuickAI device, the UUIDs are different from the standard SensiML Classifier BLE UUIDs. See the QuickAI UUIDs below.

    ``SENSIML_EVENT_SERVICE_UUID = 42421100-5A22-46DD-90F7-7AF26F723159``
    ``SENSIML_EVENT_CHARACTERISTIC_UUID = 42421101-5A22-46DD-90F7-7AF26F723159``


Example Android Applications
----------------------------


**SensiML TestApp**

The SensiML Toolkit includes the SensiML TestApp. The SensiML TestApp is an Android application that reads the SensiML classification values from the BLE characteristics above and displays them to the user. You can find the SensiML TestApp in the Google Play store at the link below:

https://play.google.com/store/apps/details?id=com.sensiml.suite.testapp


**SensiML OpenApp Project**

If you want to create your own Android application similar to the SensiML TestApp, we provide the source code in a repository called the SensiML OpenApp Project. Download the source code from the repository below:

https://bitbucket.org/sensimldevteam/sensiml_android_open_project/


**SensiML Classifier onCharacteristicChanged Event**


A SensiML classification will return a Model_ID and Class_ID from the BLE
``onCharacteristicChanged`` event. These values correspond to your Knowledge Pack class map and model.

The class map can be found inside the Analytics Studio 'Download Model' page or by running the following commands in a new cell through the SensiML Python SDK:

.. code-block:: python

    kp = client.get_knowledgepack('<ENTER-UUID>')
    kp.class_map


See the reference code below for how to read the live classification ModelID and ClassID from the
onCharacteristicChanged BLE event in Android. This code is found inside the activity
``DeviceStatusBaseActivity.java`` in the SensiML OpenApp Project repository above

.. code-block:: java

    final int MODEL_NUM_INDEX = 0;
    final int CLASSIFICATION_INDEX = 2;
    byte[] data = intent.getByteArrayExtra(BluetoothLeService.EXTRA_DATA_EVENT_CLASSIFICATION);
    ByteBuffer wrapBuffer = ByteBuffer.wrap(data);
    wrapBuffer.order(ByteOrder.LITTLE_ENDIAN);
    int modelId = (int) wrapBuffer.getChar(MODEL_NUM_INDEX);
    int classId = (int) wrapBuffer.getChar(CLASSIFICATION_INDEX);

Next Steps: Knowledge Pack Library Integration
----------------------------------------------

If you have your own firmware application and want to make calls directly to Knowledge Pack APIs you can do this using the Knowledge Pack Library format. See more details at the link :doc:`building-a-knowledge-pack-library`