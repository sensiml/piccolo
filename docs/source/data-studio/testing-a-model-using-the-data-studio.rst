.. meta::
   :title: Testing a Model Using the Data Studio
   :description: How to test a model using the Data Studio

Testing a Model Using the Data Studio
==========================================

.. running-a-model-in-the-data-studio-start-marker

.. figure:: /data-studio/img/dcl-test-model-mode.png
   :align: center

The Data Studio has two ways to test a model on your dataset:

1. **Running a Model During Data Collection:** Connect to a model during data collection and get the model results in real-time

2. **Running a Model in the Project Explorer:** Run a model on any previously collected CSV or WAV files in your project


This lets you see how your model will perform on real data before flashing it to a device. After getting the results from the model you can then save the results to your project and re-train your model using the new results. This is a powerful feature that we will go over in detail below.

Running a Model During Data Collection
--------------------------------------

.. running-a-model-during-data-collection-start-marker

The Data Studio has an option to connect to your Knowledge Pack during data collection and see the model results in real-time. You can then save the results to your project and use them for re-training your model. *Note - This feature is only supported on devices that implement the Simple Streaming capture protocol*

1.	Click on the *Test Model* button in the left navigation bar

.. figure:: /data-studio/img/dcl-navigation-bar-left-test-model-button.png
   :align: center

2. Connect to your device

.. figure:: /data-studio/img/dcl-sensor-connect.png
   :align: center

3. If you are not connected to a Knowledge Pack, click **Connect** in the Test Model tab

.. figure:: /data-studio/img/dcl-test-model-knowledge-pack-connect.png
   :align: center

4. Select a Knowledge Pack

.. figure:: /data-studio/img/dcl-knowledge-pack-select-screen.png
   :align: center

5. Connect to the Knowledge Pack

.. figure:: /data-studio/img/dcl-test-model-knowledge-pack-connected.png
   :align: center

6. You will now see your model results in real-time in the graph

.. figure:: /data-studio/img/dcl-test-model-mode.png
   :align: center

7. *(Optional)* You can click **Start Recording** and the Data Studio will save the Knowledge Pack results to your project. This lets you quickly add additional training data to your project

.. figure:: /data-studio/img/dcl-test-model-start-recording.png
   :align: center


8. *(Optional)* In the Save Confirmation screen you can edit or delete the Knowledge Pack results before saving the results to your project

.. figure:: /data-studio/img/dcl-test-model-results-save-confirmation.png
   :align: center

.. running-a-model-during-data-collection-end-marker

Running a Model in the Project Explorer
---------------------------------------

The Project Explorer has an option to connect to a Knowledge Pack and run a model on any previously collected files you have added to your project. You can then save the results to your project and use them for re-training your model.

.. testing-model-project-explorer-start-marker

1. Open the Project Explorer

.. figure:: /data-studio/img/dcl-open-project-explorer.png
   :align: center

2. Select the files you want to use by holding *(Shift + Click)* or *(Ctrl + Click)*

3. *Right-Click* and select Segments → Run Model

.. figure:: /data-studio/img/dcl-project-explorer-run-model.png
   :align: center

4. Select a Knowledge Pack

.. figure:: /data-studio/img/dcl-knowledge-pack-select-screen.png
   :align: center

5. Select a Session. This is where the Knowledge Pack results will be saved

.. image:: /guides/getting-started/img/dcl-session-management.png
   :align: center

6. Save the results. *(Optional: You can edit or delete the Knowledge Pack results before saving)*

.. figure:: /data-studio/img/dcl-project-explorer-review-results.png
   :align: center

.. testing-model-project-explorer-end-marker

Automated Labeling Using a Model
--------------------------------

By using the model results from either of the two methods above you can re-train your model with new data. By repeating this process you can quickly improve/augment your model training data with more robust and accurate results.