.. meta::
   :title: API Methods - Capture Configuration
   :description: How to use the Capture Configuration API Method

Capture Configuration
=====================

A Capture Configuration describes the sensor settings that were used for a :doc:`Capture <captures>` file in your :doc:`Project <projects>`. All of the Captures in your project should have a Capture Configuration associated with them. Capture configurations are used to:

   1. Maintain data providence and help you maintain your data collection strategy. 
   2. Enforce that data used in training a model was collected with consistent methodology.

The Capture Configuration is typically created by the Data Studio when you begin collecting data. However, you can also generate Capture Configurations programmatically using the API methods. 


Examples::

    client.list_capture_configurations()

    client.project._capture_configurations.create_capture_configuration(name, configuration, uuid)

.. automodule:: sensiml.datamanager.capture_configurations
    :members: CaptureConfigurations

.. automodule:: sensiml.datamanager.capture_configuration
    :members: CaptureConfiguration

