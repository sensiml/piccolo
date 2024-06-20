.. meta::
    :title: Third-Party Integration - Build Scripts
    :description: How to define your hardware platform build scrips

=============
Build Scripts
=============

The final step in adding a platform to SensiML is to provide two scripts that help us build a binary and return a properly configured library.

Configuring Sensors
~~~~~~~~~~~~~~~~~~~

The first script is a script to configure sensors. When using Data Capture Lab to :ref:`configure your device<configuring_device>`, a Sensor Configuration is created that stores the properties of the sensors used during data collection (Sample Rate, Sensor name, etc).

This configuration will be used to generate code to configure your sensors at build time or return a configuration file for setting up your device with a library.

.. literalinclude:: scripts/config_sensor_files.sh
    :language: bash
    :caption: config_sensor_files.sh

The above script takes a ``sample_rate`` to configure your sensors to run at the right speed, as well as sensor-specific ranges to allow a motion sensor to be configured for the right sensitivity.

These work by replacing defines in the ``SML_APP_CONFIG_FILE`` specified in the :doc:`codegen_parameters<hardware-platform>` section of your hardware platform. It is highly suggested to have all of these configurations in one file.

Replacing the variable names of ``SNSR_SAMPLE_RATE`` with those that match your repository will allow SensiML to output proper configuration for your device.

Building a Binary
~~~~~~~~~~~~~~~~~

In order to build a binary on SensiML servers, we need to know the build steps required to build your project.

This will be needed for both a :ref:`custom platform image<custom_platform_image>` and a :ref:`platform using a supported compiler<sdk_code_dockerfile>` Docker image to properly build a binary.

.. literalinclude:: scripts/build_binary.sh
    :language: bash
    :caption: build_binary.sh

The ``build_binary`` script will reference many of the parameters in the :doc:`codegen_parameters<hardware-platform>` section of your hardware platform definition.

The commented sections of the build script should be the only items changed, so that your build steps perform, and the desired output files are included in a downloaded zip file.

