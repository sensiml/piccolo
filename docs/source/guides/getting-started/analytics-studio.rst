.. meta::
   :title: Analytics Studio - Getting Started
   :description: Get started with the Analytics Studio. Learn how to build a model and generate firmware code using SensiML AutoML.

Analytics Studio
----------------

The Analytics Studio is an application that filters and optimizes your labeled sensor data through machine learning algorithms. It generates a model (SensiML Knowledge Pack) ready to be flashed into the firmware of your device of choice. The most powerful part of the Knowledge Pack is that it will be detecting events on the low memory sensor without ever requiring a connection to the cloud.

.. figure:: /guides/getting-started/img/header-creating-a-model.png

.. analytics-studio-overview-start-marker

SensiML AutoML and the SensiML Python SDK
`````````````````````````````````````````

The Analytics Studio abstracts the complexities of model building and translates them to a user-friendly interface.

Additionally, we provide access to our python library called the SensiML Python SDK. The SensiML Python SDK is a library that provides a programmatic interface to SensiML APIs through python. You can think of the Analytics Studio as the front-end to the SensiML Python SDK. The Analytics Studio uses the APIs in the SensiML Python SDK to generate a model. By using the SensiML Python SDK you have full access the tools you need to customize functions, training algorithms, features, tuning parameters, data augmentation techniques, and classifiers through code. We suggest starting with the Analytics Studio to generate your model, but by using the APIs in the SensiML Python SDK you can do even more with projects that have advanced requirements.

Loading the Analytics Studio
````````````````````````````

1. Open the Analytics Studio by going to https://app.sensiml.cloud/ and log in to your account. You will be taken to the Home page where you can see the projects uploaded to your account

   .. figure:: /guides/getting-started/img/analytics-studio-home.png
      :align: center

.. analytics-studio-overview-end-marker

2. Open your project by clicking the Open Project icon or double clicking on the project name

   .. figure:: /guides/getting-started/img/analytics-studio-home-open-project.png
      :align: center