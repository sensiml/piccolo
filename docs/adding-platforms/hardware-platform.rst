.. meta::
  :title: Third-Party Integration - Hardware Platform
  :description: How to define a Hardware Platform

=================
Hardware Platform
=================

Hardware Platform defines properties about your device. It includes the :doc:`processor` and :doc:`compiler` that your device will use.

.. code:: yaml

   - fields:
        uuid: 00000000-0000-0000-0000-000000000000
        name: My Platform Name For Display
        description: Build libraries for My Platform boards/addons.
        processors: [00000000-0000-0000-0000-000000000000]
        can_build_binary: true
        codegen_parameters:
          {
            "uses_simple_streaming": True,
            "app_environment":
              {
                "SML_APP_BUILD_DIR": "/build/firmware/project",
                "SML_APP_DIR": "/build/firmware/src",
                "SML_APP_CONFIG_FILE": "/build/firmware/src/app_config.h",
                "SML_APP_LIB_DIR": "/build/firmware/knowledgepack/libsensiml",
                "SML_APP_OUTPUT_BIN_DIR": "/build/firmware/output/dist/",
              },
          }
        applications:
          {
            "SensiML AI Simple Stream":
              {
                "description": "Provides an application binary (or example code) that implements SensiML Simple Streaming interface for reporting Knowledge Pack results",
                "supported_outputs": [["Serial"], ["BLE"], ["Serial", "BLE"]],
              },
          }
        supported_compilers: [00000000-0000-0000-0000-000000000000]
        hardware_accelerators: {}
        default_selections:
          {
            "processor": "00000000-0000-0000-0000-000000000000",
            "compiler": "00000000-0000-0000-0000-000000000000",
            "float": "Hard FP",
          }
     model: platform


+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **uuid**                   | UUID4        | Unique UUID for your platform                                                                                                                                                                                                                                          |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **name**                   | string       | Name for your platform to be displayed in Analytics Studio                                                                                                                                                                                                             |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **description**            | string       | Description of your platform/it's capabilities                                                                                                                                                                                                                         |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **processors**             | list(uuid4)  | Processor(s) your hardware platform supports. See the :doc:`Processor Documentation <processor>` for how to define a processor                                                                                                                                         |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **can_build_binary**       | boolean      | Indicates whether or not the platform being added supports building a full binary example. In order to build a binary a :doc:`Custom Compiler<compiler>` must be provided                                                                                              |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **codegen_parameters**     | dictionary   |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | ``uses_simple_streaming`` - Default parameter - Must be set to True. If you would like to build for MQTT-SN contact SensiML Support                                                                                                                                    |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | ``app_environment`` - Defines file path information for generating build scripts, properly compiling a binary, or modifying sensor configuration files. See more on how the properties get used in the :doc:`Build Scripts Documentation <build-scripts>`.             |
|                            |              | Contains the following properties:                                                                                                                                                                                                                                     |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | * ``SML_APP_BUILD_DIR`` - File location(s) to run your build commands                                                                                                                                                                                                  |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | * ``SML_APP_DIR`` - File location of your application source code                                                                                                                                                                                                      |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | * ``SML_APP_CONFIG_FILE`` - File location used to configure sensors for recognition (Sample rate, sensor range, etc.)                                                                                                                                                  |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | * ``SML_APP_LIB_DIR`` - File location of your platform Knowledge Pack libraries                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | * ``SML_APP_OUTPUT_BIN_DIR`` - File location of the output of a build on successful compilation                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **applications**           | dictionary   | Applications define properties about your hardware platform outputs based on your codegen_parameter ``app_environment`` and :doc:`build-scripts` properties                                                                                                            |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | ``dictionary key`` - Application name. Used for display in the Analytics Studio                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | ``description`` - Description of the application, interfaces, outputs, etc. Used for display in the Analytics Studio                                                                                                                                                   |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | ``supported_outputs`` <List of Lists> - Defines available output combinations for model data. Current supported outputs: Serial, BLE, WiFi. Additional supported_outputs can be added by working with the SensiML team for integration                                 |
|                            |              |                                                                                                                                                                                                                                                                        |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_compilers**    | list(uuid)   | Compiler(s) your hardware platform supports. See the :doc:`Compiler Documentation<compiler>` for how to define a compiler                                                                                                                                              |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **default_selections**     | dictionary   | Defines the default selected :doc:`processor` and :doc:`compiler` options in the Knowledge Pack download screen in the Analytics Studio.                                                                                                                               |
|                            |              |                                                                                                                                                                                                                                                                        |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **hardware_accelerators**  | dictionary   | Hardware accelerator properties are custom properties that are defined on a device by device basis by working with the SensiML team to integrate into the build process                                                                                                |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | Use a simple ``"name" : True`` format per accelerator.                                                                                                                                                                                                                 |
|                            |              |                                                                                                                                                                                                                                                                        |
|                            |              | **Example:** ``{ "hardware_distance" : True }``                                                                                                                                                                                                                        |
+----------------------------+--------------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
