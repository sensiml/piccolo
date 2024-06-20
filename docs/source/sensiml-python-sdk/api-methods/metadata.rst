.. meta::
   :title: API Methods - Metadata
   :description: How to use the Metadata API Method

Metadata
========

Metadata are custom properties that you can save to your :doc:`Capture <captures>` files that allow you to filter your sensor data based on characteristics of the files. Metadata properties are normally attributes about the subject or object you are recording.

Metadata are used to:

   1. Differentiate the subset of captures that you want to work with for modeling
   2. Perform aggregations for feature generation (i.e. do SQL-like "group by" operations)

Examples::

    client.project.metadata_values()

    client.project.metadata_columns()

.. automodule:: sensiml.datamanager.metadata
    :members: Metadata

