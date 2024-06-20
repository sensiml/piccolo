.. meta::
   :title: API Methods - Projects
   :description: How to use the Project API Method

Projects
========

A project is the collection of your labeled sensor data and algorithms used to build your application.

Examples::

    client.projects = 'My Project'

    client.project.columns()

    client.project..metadata_columns()
    
    client.project.labels()

.. automodule:: sensiml.datamanager.projects
    :members: Projects

.. automodule:: sensiml.datamanager.project
    :members: Project
