.. meta::
   :title: Testing a Model Using the SensiML Toolkit
   :description: How to test a model using the SensiML Toolkit

Testing Model Results
=====================

After you build a model it is useful to test the model performance before flashing it to a device. The Analytics Studio and Data Studio have several useful features that enable you to see model performance and re-label your dataset based on the results.

.. figure:: /guides/getting-started/img/header-testing-model-results-3.png

Using a Model in the Analytics Studio
-------------------------------------

The Analytics Studio lets you test your model on any file in your project to see how the model performs before flashing it to a device. It gives insight to your model performance by showing the confusion matrix, ground truth vs prediction results, and the feature vector heat map. See more on how to use this feature in the :doc:`Analytics Studio Documentation</analytics-studio/testing-a-model-using-the-analytics-studio>`

.. figure:: /guides/getting-started/img/analytics-studio-test-model.png
   :align: center

Using a Model in the Data Studio
--------------------------------

The Data Studio has two ways to use your model on your dataset:

1. Connect to a model during data collection and get the model results in real-time *(Requires Simple Streaming protocol)*
2. Run a model on any previously collected CSV or WAV files in your project

This lets you see how your model performs before flashing it to a device. After getting the results you can then edit the labels and save the results as new labels in your project to re-train your dataset. See more on how to use this feature in the :doc:`Data Studio Documentation</data-studio/testing-a-model-using-the-data-studio>`

.. figure:: /data-studio/img/dcl-test-model-mode.png
   :align: center