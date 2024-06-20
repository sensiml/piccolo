.. meta::
   :title: Next Steps
   :description: Next steps using the SensiML Toolkit

Where to go next?
-----------------

This guide has walked you through the **Hello World** example of edge sensor detection. Now you should be able to:

1. Collect and annotate sensor data with the Data Studio to build a high-quality curated dataset.
2. Use the Analytics Studio's AutoML engine to build an event detection algorithm suitable for your edge device. 
3. Validate your model is working with the SensiML TestApp in real time.

New Event Exercise
``````````````````

To practice everything you have learned, we recommend adding a new event to the Slide Demo project, such as tapping on the top of the sensor. Keep in mind that this project was created to detect continuous events when you select your gesture. 

SensiML Python SDK
``````````````````

For data scientists we recommend looking into more of the advanced features within the SensiML Toolkit. In this guide we discussed the graphical interface using Analytics Studio, however, through the SensiML Python SDK you can specify the features, transforms, training algorithm, and validation methods that go into your model. You can also specify different sampling, feature selection, and data augmentation techniques. To see how this works, see the :doc:`SensiML Python SDK Documentation</sensiml-python-sdk/overview>`.

Application Library
```````````````````

We provide a variety of more advanced projects outside of this guide which you can find in the `Application Library <https://sensiml.com/resources/app-library/>`_. Here you will find full curated datasets for industrial predictive maintenance, sports wearables, and more. These projects are meant to provide examples to help you get started with your own projects. We are constantly adding new datasets and welcome contributions.

Automated Labeling Tools
````````````````````````

As mentioned in :doc:`data-collection-planning`, the type of event you are trying to detect changes the way you will label your data. The Getting Started Guide shows you how to label **continuous** events.

After completing the Getting Started Guide you can read more about different methods for automating the labeling process in the :doc:`Automated Labeling Tools Documentation</data-studio/automated-labeling-tools>`

Model Rehydration
`````````````````

Using the SensiML Python SDK you can rehydrate a model and see the code/algorithms in a model that was generated using SensiML AutoML. 

1. Copy the Knowledge Pack UUID from the Explore Model page inside the Model Summary tab

.. figure:: /guides/getting-started/img/analytics-studio-knowledge-pack-uuid.png
   :align: center

2. Run the following commands in the SensiML Python SDK to rehydrate the model

.. code-block:: python

  from sensiml import SensiML
  client = SensiML()
  client.project = '<Project Name>'
  client.pipeline = '<Pipeline Name>'
  
  kp = client.get_knowledgepack('<Knowledge Pack UUID>')
  client.pipeline.rehydrate(kp)

  #Replace <Project Name>, <Pipeline Name>, and <Knowledge Pack UUID> with your own project parameters

This will print out the model code. From here you can modify the code and re-train your model hyperparameters to improve the accuracy. For more information on the programmatic approach to model building see the :doc:`SensiML Python SDK Documentation<../../../sensiml-python-sdk/overview>`. 

.. figure:: /guides/getting-started/img/sensiml-python-sdk-rehydrate-result.png
   :align: center
