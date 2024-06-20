.. meta::
   :title: Data Studio - Importing Python Models
   :description: Get started using the Data Studio

Importing Python Models
-----------------------

Overview
````````

The Data Studio supports running Python code to identify and classify segments in your project. Below we will go over two examples. The first will show how to generate segments using a sliding window segmentation algorithm. The second will show you how to add a classifier to the sliding window to return classifications. You can download the code for each example and customize it to make your models.

Requirements
````````````

1. Running Python models from source code requires **Python version 3.7 or greater** to be installed on your computer. Install python from `<https://www.python.org/downloads/>`_

2. Install the SensiML Python SDK by running the following command

   .. code-block:: python

      pip install SensiML

Segmentation Algorithm Example
``````````````````````````````

Segmentation algorithms identify the start and end of events based on customizable properties like signal threshold and window size.

View :doc:`Segmentation Algorithm Documentation </data-studio/python-model-segmentation-algorithm>`

Classifier Algorithm Example
````````````````````````````

Classifier algorithms identify events based on a customizable classifier algorithm within the model.

View :doc:`Classifier Algorithm Documentation </data-studio/python-model-classifier-algorithm>`