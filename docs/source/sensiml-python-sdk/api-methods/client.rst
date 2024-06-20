.. meta::
   :title: API Methods - SensiML
   :description: How to use the SensiML API Method

SensiML
=======

The SensiML API is the entry point for connecting to the rest of the SensiML API Methods

Examples::

    from sensiml import Client
    client = Client()
    
    client.list_projects()
    client.project = "<Your Project>"

    client.list_captures()

.. automodule:: sensiml.client
    :members: Client
