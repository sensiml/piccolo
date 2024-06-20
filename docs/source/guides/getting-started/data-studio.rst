.. meta::
   :title: Data Studio - Getting Started
   :description: Get started with the Data Studio. Learn how to collect and label your sensor data with SensiML.

Data Studio
----------------

The first step of creating a sensor application is going to be collecting and labeling raw sensor data into events of interest through the **Data Studio** .

The Data Studio is an application that helps you capture and label raw data from the sensor and transform it into the events you want your application to detect.

At SensiML we have designed the Data Studio to speed up the process of collecting and annotating data. The Data Studio will play a key role in helping you to create and curate a high-quality dataset.

.. image:: /guides/getting-started/img/header-collect-training-data-3.png

Projects
````````

A project contains all your collected sensor data and algorithms. Your sensor data is saved to your local computer and synced with the cloud. Only your team has access to your data. This allows you to have multiple people collecting/labeling data on a project at the same time.

Importing a Project
```````````````````

If you downloaded the example :doc:`Slide Demo dataset</guides/getting-started/quick-start-project>` you can upload it to your account by following the steps below.

.. note:: The Slide Demo dataset is a simple **Hello World** style dataset to go through the basics of how to use the SensiML Toolkit. We also provide more interesting datasets including audio, wearable, and predictive maintenance applications which you can find in the `SensiML Application Library <https://sensiml.com/resources/app-library/>`__.

1. Open the **Data Studio** and **Sign in** to your account
2. Click **Import project**

.. figure:: /guides/getting-started/img/dcl-import-project-click.png
   :align: center

3. Select the .DSPROJ file from the dataset and click **Next** 

.. figure:: /guides/getting-started/img/dcl-import-project-file-select-2.png
   :align: center

4. Click **Import** 

.. figure:: /guides/getting-started/img/dcl-import-project-review.png
   :align: center

.. note:: If you want to create a new project click the **New Project** button to create an empty project and add your own files to the project
   
   .. figure:: /guides/getting-started/img/dcl-new-project-click.png
      :align: center