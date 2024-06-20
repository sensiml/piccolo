.. meta::
   :title: API Methods - Capture
   :description: How to use the Capture API Method

Captures
========

The sensor data files you add to a :doc:`Project <projects>` are called Captures. A Capture can contain multiple time series columns corresponding to different devices, sensors, channels, or axes, as long as all of the columns in the capture describe the same period of time.

Examples::

    # to list all capture files
    
    client.list_captures()

    my_capture = client.project.captures.get_capture_by_filename("Capture Name")

    my_capture = client.project.captures.get_capture_by_uuid(uuid)

.. automodule:: sensiml.datamanager.captures
    :members: Captures

.. automodule:: sensiml.datamanager.capture
    :members: Capture
