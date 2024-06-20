.. meta::
    :title: Third-Party Integration - Processor
    :description: How to define a processor

=========
Processor
=========

A processor defines the microcontroller/CPU your hardware platform will use. See how to define a processor below:

.. code:: yaml

   - fields:
       uuid: 00000000-0000-0000-0000-000000000000
       architecture: 1
       display_name: "Cortex M4"
       manufacturer: "Arm"
       compiler_cpu_flag: "-mcpu=cortex-m4"
       float_options:
           {
           "None": "-mfloat-abi=soft",
           "Soft FP": "-mfloat-abi=softfp -mfpu=fpv4-sp-d16",
           "Hard FP": "-mfloat-abi=hard -mfpu=fpv4-sp-d16",
           }
     model: processor

+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
| **uuid**              | uuid4      | Unique UUID for your processor. This will be referenced in the :doc:`Hardware Platform <hardware-platform>` YAML ``processors`` property          |
+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
| **display_name**      | string     | Name for your processor to be displayed in Analytics Studio                                                                                       |
+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
| **manufacturer**      | string     | Name of the processor manufacturer to be displayed in Analytics Studio                                                                            |
+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
| **architecture**      | int        | Architecture number. See the :doc:`Architecture Documentation<architecture>` for supported architectures                                          |
|                       |            |                                                                                                                                                   |
|                       |            |                                                                                                                                                   |
|                       |            |                                                                                                                                                   |
+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
| **compiler_cpu_flag** | string     | *Optional*: Provides CPU/processor flags to compiler based on your architecture                                                                   |
+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+
| **float_options**     | dictionary | *Optional*: Provides floating point information to compiler based on your architecture                                                            |
|                       |            |                                                                                                                                                   |
+-----------------------+------------+---------------------------------------------------------------------------------------------------------------------------------------------------+



