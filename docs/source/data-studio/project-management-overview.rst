.. meta::
   :title: Data Studio - Project Management Overview
   :description: Overview of the project management tools in the Data Studio

Project Management Overview
===========================

The Data Studio includes several features that help you organize and update the files in your project through the **Project Explorer**.

.. image:: /data-studio/img/dcl-project-explorer-3.png
   :align: center

File Organization
-----------------

At the top of the Project Explorer there are several key columns that help organize your files so that you can better manage your project. You can organize and filter the files in your project by these columns. Let's take a look at how these columns are used.

.. image:: /data-studio/img/dcl-project-explorer-file-organization-2.png
   :align: center

* Status: File server status *(Synced locally and in the cloud, Saved locally, or Saved in the cloud)*
* Video: Indicates if the file has a video file linked
* Time: File length based on sample rate
* Segments: Total number of segments in the current selected session
* Label Distribution: Distribution of labels ranked from high to low
* Uploaded: Date uploaded to SensiML servers


Label Distribution
------------------

The label distribution column provides a quick way for you to view a breakdown of the labels in a file.

Hover over the label distribution icons to see a deeper view of the label distribution in a file.

.. image:: /data-studio/img/dcl-project-explorer-label-distribution-hover.png
   :align: center

Highlight a list of files and *Right + Click → Label Distribution* to see a total label distribution across multiple files in your project.

.. image:: /data-studio/img/dcl-project-explorer-label-distribution-screen.png
   :align: center


Custom Metadata Columns
-----------------------

You can create custom file metadata properties to describe attributes about the subject or object in the file. See more details on how to create metadata in the :doc:`Setting Up Labels and Metadata Documentation</data-studio/setting-up-labels-and-metadata-in-a-project>`.

.. image:: /data-studio/img/dcl-project-explorer-custom-metadata-columns-2.png
   :align: center

File Management Tools
---------------------

In the Project Explorer menu options there are several useful features to manage files, metadata, and labels across your entire project.

.. image:: /data-studio/img/dcl-project-explorer-file-management-2.png
   :align: center

* File Storage: Upload, Download, or Delete files
* Export: Export the selected files into the :doc:`DAI file format</data-studio/dai-import-format>`
* Segments: Add, Edit, Copy, or Clear all segments in the selected files
* Metadata: Add, Edit, or Clear all metadata in the selected files
* Compare Files: Select multiple files to open side-by-side
* Video Management: Link video files (MP4 or MOV) to be played during labeling

Session Management
------------------

The Project Explorer lets you create multiple sessions for labeling the same dataset. For example, you can label your data in one session and then create a brand new session for new labels. This allows you to work on the same set of data without having to re-import your files.

.. image:: /guides/getting-started/img/dcl-session-management.png
   :align: center
