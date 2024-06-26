.. meta::
   :title: Analytics Studio - Generating a Knowledge Pack
   :description: How to generate a Knowledge Pack for your model in the Analytics Studio

Generating a Knowledge Pack
===========================

A Knowledge Pack takes the event detection model you generated in the pipeline and transforms it into a binary or library file that can be run on your hardware device at the edge. Once the Knowledge Pack is on your hardware device, it starts outputting classification IDs that correspond to your events of interest.

.. figure:: /guides/getting-started/img/analytics-studio-download-knowledge-pack.png
   :align: center

A Knowledge Pack can be generated through the **Download Model** page

.. figure:: /knowledge-packs/img/analytics-studio-download-model.png
   :align: center

HW Platform
-----------

SensiML Knowledge Packs are not locked to any specific hardware platform. This feature allows you to choose the platform where you will deploy your Knowledge Pack. Some fields (Processor, Float Options, Compiler) get default values that depend on the selected HW platform.

Arm/GCC Compilers produces binaries with options in regards to floating-point operations:

* **None** -  ``-mfloat-abi=soft`` Full software floating-point. The compiler will not generate any FPU instructions and the ``-mfpu=`` option is ignored. Function calls are generated by passing floating-point arguments in integer registers.

* **Soft FP** -  ``-mfloat-abi=softfp`` Hardware floating-point using the soft floating-point ABI. The compiler will generate FPU instructions according to the -mfpu= option. Function calls are generated by passing floating-point arguments in integer registers. This means ``soft`` and ``softfp`` may be intermixed.

* **Hard FP** -  ``-mfloat-abi=hard`` Full hardware floating-point. The compiler will generate FPU instructions according to the ``-mfpu=`` option. Function calls are generated by passing floating-point arguments in FPU registers. This means hard and softfp cannot be intermixed; neither can hard and soft.

Format
------

.. include:: /knowledge-packs/knowledge-pack-format.rst
   :start-after:  knowledge-pack-format-start-marker

Application
-----------

**Application** - Application is the example application for supported platforms that allows an example binary to be built for testing.

Classification Output
---------------------

**Output** - Output corresponds to how your events get broadcasted from the hardware device and how you want to connect to your device. There are three main outputs: Bluetooth-LE, Serial, and Wi-Fi (TCP/IP).

Debug Output
------------

When building a Knowledge Pack there is a debug option that will log extra information like feature vectors, debug messages, and error messages over a serial connection to help you debug the events of interest on a device. To enable this, set Debug to True in the Advanced Settings when you download your Knowledge Pack.

.. image:: /analytics-studio/img/debug-knowledge-pack.png
  :align: center

After flashing your device with a Knowledge Pack, debug information can be viewed by connecting to the virtual COM port in a terminal application.