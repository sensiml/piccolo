.. meta::
   :title: Data Studio - Automated Labeling Tools
   :description: Overview of the automated labeling tools in the Data Studio

Automated Labeling Tools
========================

This guide is a continuation of the :doc:`Labeling Events of Interest Documentation </data-studio/labeling-events-of-interest>`. Now that you've learned the basics of how to add **segments** to a **session** let's go over some of the automated labeling tools within the Data Studio. There are two main tools you can use to automate the labeling process.

1. Using a model/Knowledge Pack from the Analytics Studio
2. Using a segmentation algorithm in an auto-session

Using a Model/Knowledge Pack from the Analytics Studio
------------------------------------------------------

After you build a model/Knowledge Pack to recognize your events in the Analytics Studio you can use that model within the Data Studio to label your events on any previously collected file in your project. This is a powerful tool that greatly speeds up the time to label a project and also lets you see how your model will perform without needing to re-collect new data.

.. include:: /data-studio/testing-a-model-using-the-data-studio.rst
   :start-after: testing-model-project-explorer-start-marker
   :end-before: testing-model-project-explorer-end-marker

Using a Segmentation Algorithm in an Auto-Session
-------------------------------------------------

In the :doc:`Labeling Events of Interest Documentation </data-studio/labeling-events-of-interest>` we went over how to manually place a segment around your event of interest. However, you can setup a segmentation algorithm in an auto-session to automate labeling your events of interest without needing to manually place segments.

1. Create a new session by clicking the **+ icon** at the bottom of the Project Explorer and clicking **Create New**

.. figure:: /data-studio/img/dcl-project-explorer-create-new-session.png
   :align: center

2. Select the **Auto** setting type and click **Add**

.. figure:: /data-studio/img/dcl-session-auto-new-session-2.png
   :align: center

3. Select an **Algorithm**. The Data Studio has access to five segmentation algorithms

.. figure:: /data-studio/img/dcl-session-auto-select-segmentation-algorithm.png
   :align: center

4. Learn more about how to use the segmentation algorithm by hovering over the **info icon**

.. figure:: /data-studio/img/dcl-session-auto-info-button.png
   :align: center

5. Enter your **Session Parameters** and click **Save**

.. figure:: /data-studio/img/dcl-session-auto-edit-parameters-2.png
   :align: center

6. Select the files you want to use by holding *(Shift + Click)* or *(Ctrl + Click)*

7. *Right-Click* and select Segments → Run Segmenter Algorithm

.. figure:: /data-studio/img/dcl-session-auto-add-from-segmenter-algorithm.png
   :align: center

8. Select your session and click **Select**

.. figure:: /data-studio/img/dcl-session-auto-select-session-2.png
   :align: center

9. The Data Studio will use the algorithm in your session to create segments in the files you selected. Edit the labels and click **Save**

.. figure:: /data-studio/img/dcl-session-auto-edit-label-menu.png
   :align: center