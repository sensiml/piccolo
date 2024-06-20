.. meta::
   :title: Analytics Studio - Building a Model
   :description: How to build a model in the Analytics Studio

.. include:: /guides/getting-started/building-a-model.rst
   :end-before:  build-model-pipeline-end-marker

.. include:: /analytics-studio/pipeline-create.rst

.. include:: /analytics-studio/pipeline-templates.rst

.. include:: /guides/getting-started/building-a-model.rst
   :start-after:  build-model-pipeline-properties-start-marker
   :end-before:  build-model-pipeline-properties-end-marker

1. Click **Run Pipeline** and the Analytics Studio will automatically build you a model to detect your events. This is where SensiML's AutoML finds the features needed to build an algorithm that will run on your device.

.. figure:: /analytics-studio/img/analytics-studio-build-model-run-pipeline-button.png
   :align: center

2. Once the pipeline is complete it will display 5 models in the AutoML Results view.

.. figure:: /guides/getting-started/img/analytics-studio-automl-results.png
   :align: center

There are several summary statistics for each model. You can use this information to select a model that supports your device's resources while providing the level of accuracy your application needs. Keeping in mind that typically, there is an accuracy vs resource usage trade off, where the more resources you allocate to modeling, the higher accuracy of a model that can be built.   