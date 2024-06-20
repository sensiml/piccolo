.. meta::
   :title: Knowledge Packs / Model Firmware - Knowledge Pack Format
   :description: Overview of the available Knowledge Pack format options

Knowledge Pack Format
=====================

.. knowledge-pack-format-start-marker

We provide three formats to interface with your model when you generate a Knowledge Pack. The available format options depend on the device or compiler that you are using. See details about each of the three formats below.

**1. Binary**

Generates application firmware that is ready to flash to your device. Includes the application, Knowledge Pack, sensor configuration/drivers, and classification output for the target device.

**2. Library**

Generates a library and header files with function APIs that can be linked into your application firmware. See the links below for useful information on the Library format.

* :doc:`/knowledge-packs/knowledge-pack-functions` : Describes the available Knowledge Pack APIs in a Knowledge Pack Library
* :doc:`/knowledge-packs/building-a-knowledge-pack-library` : Tutorial for linking Knowlede Pack APIs into your application firmware

**3. Source**

Generates a Makefile and the C/C++ source code files for the Knowledge Pack APIs. See the :doc:`SensiML Embedded SDK Documentation</knowledge-packs/sensiml-embedded-sdk>` for more information on the Source format.

    .. important:: **Source** is only available to specific subscription plans. See more details at `<https://sensiml.com/plans/>`_