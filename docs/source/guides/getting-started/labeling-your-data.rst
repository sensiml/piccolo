.. meta::
   :title: Label Your Data
   :description: How to label your data using the SensiML Toolkit

Labeling Your Data
------------------

Next, we are going to go over how to label events of interest in the Data Studio. How you do this depends on the type of event you are detecting (described in :doc:`data-collection-planning`). First let's see how to open a file.

Viewing Your Sensor Data Files
``````````````````````````````

.. label-explorer-start-marker

1. Open your project in the Data Studio

2. Click the **Project Explorer** button in the top left navigation bar

.. figure:: /guides/getting-started/img/dcl-navigation-bar-left-open-project-explorer.png
   :align: center

3. **Double-Click** on a file name to open the file

4. Depending on the project you have loaded, the file will open and look similar to this

.. figure:: /guides/getting-started/img/dcl-data-explorer-segment.png
   :align: center

5. If you are working with a project that has Accelerometer and Gyroscope data, you will notice the Data Studio has split the data into two tracks. These tracks can be customized to display as many sensor columns as you need.

   *(Optional)* Click on the track menu options to view options for the way your tracks are displayed. You can also add more tracks, update columns, or remove tracks. This is a powerful feature that allows you to visualize your data easier.

.. figure:: /guides/getting-started/img/dcl-track-menu-options.png
   :align: center

6. *(Optional)* Click and drag the area between tracks to adjust a track height

.. figure:: /guides/getting-started/img/dcl-track-height.png
   :align: center

Segments
````````

**Segments** are how we define where an **event** is located in your sensor data file. A segment is displayed as a transparent label within the graph of your sensor data. See a screenshot of a segment below.

.. figure:: /guides/getting-started/img/dcl-data-explorer-segment-graph.png
   :align: center
   :scale: 50%

Sessions
````````

A session separates your labeled events (segments) into a group. Every segment is inside a session. Sessions allow you to work on multiple branches
of the same dataset. Sessions can be useful when collaborating with a team or if you want to experiment with different segmentation methods on the same dataset.

.. figure:: /guides/getting-started/img/dcl-session-management.png
   :align: center

**Managing Sessions**

1. You can see the session you are currently working in and how many segments are in that session at the bottom of the Project Explorer. Hover over the segments to see your session label distribution

.. figure:: /guides/getting-started/img/dcl-project-explorer-session-segments-tooltip.png
   :align: center

2. Open the session management screen from the Project Explorer by clicking on the session name

.. figure:: /guides/getting-started/img/dcl-session-project-explorer-change.png
   :align: center

3. Alternatively, if you have a file open you can switch sessions by right + clicking on the session name in the Segments control

.. figure:: /guides/getting-started/img/dcl-session-segment-explorer-change.png
   :align: center

4. In the session management screen you can see details about your session like how many files have been labeled and how many segments are in each session

.. figure:: /guides/getting-started/img/dcl-session-management-details.png
   :align: center

5. You can add new sessions by clicking **+ Add New Session**

.. figure:: /guides/getting-started/img/dcl-session-management-add-new-session.png
   :align: center

6. You can Edit, Delete, and Copy sessions by right-clicking on any session

.. figure:: /guides/getting-started/img/dcl-session-management-menu-options.png
   :align: center


**Adding Segments to a Session**

1. Open a file from the Project Explorer

2. Next, we will add a segment to identify our event of interest. To do this, move your mouse onto the graph of your sensor data and **right-click + drag** your mouse over the area that you want to label as an event. This will place a new **segment** in the file

.. figure:: /guides/getting-started/img/dcl-segment-create-new-4.png
   :align: center

3. Label your segment with an event by clicking the **Edit button** or use the keyboard shortcut **Ctrl + E**

.. figure:: /guides/getting-started/img/dcl-segment-edit-label-2.png
   :align: center
   :scale: 80%

4. Select a label and click **Done**

.. figure:: /guides/getting-started/img/dcl-segment-select-labels-2.png
   :align: center

5. Click **Save**. This will save the segment to your session and upload it to the cloud

.. figure:: /guides/getting-started/img/dcl-save-button-2.png
   :align: center


.. label-explorer-end-marker

6. Add segments to all of the files in your project. The :doc:`Slide Demo dataset</guides/getting-started/quick-start-project>` has already been labeled, so if you are using this dataset you can move to the next step
