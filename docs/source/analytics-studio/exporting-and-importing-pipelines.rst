.. meta::
   :title: Analytics Studio - Exporting and Importing Pipelines
   :description: How to export and import a pipeline in the Analytics Studio

Exporting and Importing Pipelines
=================================

The pipeline steps and properties from your model can be exported into a JSON format. By using the export feature you can save pipeline details so that you can easily share, copy, or backup pipeline properties in a project.

Exporting a Pipeline
--------------------

Exporting a pipeline will save a JSON file to your computer. This file can then be imported into any project through the import feature. We will go over how to import a pipeline in the next section. You can export a pipeline in two ways:

In the pipeline selection window, you can click the **Export Icon** from any pipeline in the list.

.. figure:: /analytics-studio/img/analytics-studio-pipeline-export-table-button.png
   :align: center

Importing a Pipeline
--------------------

Using the export feature above you can save a pipeline JSON file. The pipeline JSON file can be imported into a new project or can be used to create new pipelines in the same project. This makes it easy to share pipeline properties between projects or models.

1. In the pipeline selection screen, click **Import Pipeline**.

.. figure:: /analytics-studio/img/analytics-studio-pipeline-import-button.png
   :align: center

2. Select your pipeline JSON file.

.. figure:: /analytics-studio/img/analytics-studio-pipeline-import-select.png
   :align: center

3. After selecting your pipeline JSON file, the Analytics Studio will show an overview of the pipeline you are going to import. Click **Confirm Import**

.. figure:: /analytics-studio/img/analytics-studio-pipeline-import-review.png
   :align: center

4. Next, we will verify the pipeline parameters, enter a new **name** for the imported pipeline, and select the matching **query** in your project.

   **[1]** Set a pipeline **name** and select a **query**

   **[2]** Review parameters of the selected **query**

   **[3]** When an imported pipeline and a selected **query** have different sensor columns, you can re-map your columns.

.. figure:: /analytics-studio/img/analytics-studio-pipeline-import-second-step.png
   :align: center
