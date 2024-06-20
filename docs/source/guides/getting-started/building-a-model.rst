.. meta::
   :title: Building a Model
   :description: How to build a model using the SensiML Toolkit

Building a Model
================

The Model Building part of the Analytics Studio uses **SensiML's AutoML** to build a model that gives you control of the features you want in your device. For example, if you build an algorithm that detects your events with 100% accuracy, the algorithm may use more resources. But by tweaking parameters in the AutoML settings you might find you can get an algorithm that uses half as many resources, while still getting 98% accuracy. You can configure SensiML's AutoML process to maximize accuracy while fitting a within a desired memory constraint. This is a powerful concept that can save you a lot of time and money.

The model building process is represented as **Pipelines**. Each pipeline is a sequence of steps representing the process of data transformation during model building.

Pipelines
`````````

A pipeline is a container for a series of data processing steps and contains the blueprint for how your model will be built. It contains the sensor data input parameters, transforms, feature generators, feature selectors, feature transforms and classifiers.

.. build-model-pipeline-end-marker

Let's take a look at the pipeline selection screen

.. figure:: /guides/getting-started/img/analytics-studio-model-building-select-pipeline.png
   :align: center
   :scale: 45%

Create a New Pipeline
`````````````````````

1. Click **Create New Pipeline** to create a new pipeline.

.. figure:: /guides/getting-started/img/analytics-studio-pipeline-create.png
   :align: center

2. Select **Use SensiML AutoML** to automatically find the best machine learning algorithm.

.. figure:: /guides/getting-started/img/analytics-studio-pipeline-create-select-parameters.png
   :align: center

3. Name the pipeline **My Pipeline** and select the **All Classes** query we created in the :doc:`Querying Data tutorial<../getting-started/querying-data>`.

.. figure:: /guides/getting-started/img/analytics-studio-pipeline-create-name.png
   :align: center

4. Click **Create Pipeline**


Building a Model
````````````````

After creating a pipeline a sidebar will pop up prompting you to setup your pipeline parameters.

1. Click **Next**

.. figure:: /guides/getting-started/img/analytics-studio-pipeline-next-steps.png
   :align: center

2. Setup the **Segmenter** step with the Windowing segmenter. Set size to **100** and slide to **100**. Windowing segmentation works well with continuous events.

.. note:: *100 refers to the window size in samples, so by picking Windowing(100) on 100hz data we have a 1 second window size, meaning every 1 second you will get a new classification*.

.. figure:: /guides/getting-started/img/analytics-studio-segmenter-windowing.png
   :align: center

.. figure:: /guides/getting-started/img/analytics-studio-segmenter.png
   :align: center

3. *(Optional)* Open the **Pipeline Settings** step. This lets you set properties that tell the Analytics Studio how to optimize/prioritize the way it builds your model. This lets you prioritize specific training algorithms/features or set a size limit on the classifier if your device is limited on SRAM.

.. figure:: /guides/getting-started/img/analytics-studio-automl-parameters.png
   :align: center

4. Click **Run Pipeline** and the Analytics Studio will automatically build you a model to detect your events. This is where SensiML's AutoML finds the features needed to build an algorithm that will run on your device.

.. figure:: /analytics-studio/img/analytics-studio-build-model-run-pipeline-button.png
   :align: center

5. Once the pipeline is complete it will display 5 models in the AutoML Results view.

.. figure:: /guides/getting-started/img/analytics-studio-automl-results.png
   :align: center

There are several summary statistics for each model. You can use this information to select a model that supports your device's resources while providing the level of accuracy your application needs. Keeping in mind that typically, there is an accuracy vs resource usage trade off, where the more resources you allocate to modeling, the higher accuracy of a model that can be built.   

.. build-model-pipeline-properties-start-marker

Pipeline Properties
```````````````````

Let's take a deeper look at some of the other properties in the Build Model screen.

.. figure:: /guides/getting-started/img/analytics-studio-model-building.png
   :align: center

- The Pipeline Settings step lets you set properties that tell the Analytics Studio how to optimize/prioritize the way it builds your model. This lets you prioritize specific training algorithms/features or set a size limit on the classifier if your device is limited on SRAM. **[1]**.
- Edit the parameters for the a step in the pipeline builder **[2]**.
- Optional steps can be added. Some of them can be added more than 1 time.

.. build-model-pipeline-properties-end-marker