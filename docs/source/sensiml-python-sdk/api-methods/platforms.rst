.. meta::
   :title: API Methods - Platform Description
   :description: How to use the Platform API Method

Platforms
=========

All supported platforms in the SensiML Toolkit can be loaded with a simple function call::

    client.platforms()

There are two ways to select your chosen platform::

    # The first way
    chosen_platform = client.platforms[1]
    # The second way
    chosen_platform = client.platforms.get_platform_by_name('Amulet 4.1')
    # Print out platform information
    chosen_platform()
    # Set the device configuration to the desired platform
    client.pipeline.set_device_configuration(platform=chosen_platform, debug=False)

.. automodule:: sensiml.datamanager.clientplatformdescriptions
    :members: ClientPlatformDescriptions

.. automodule:: sensiml.datamanager.clientplatformdescription
    :members: ClientPlatformDescription

