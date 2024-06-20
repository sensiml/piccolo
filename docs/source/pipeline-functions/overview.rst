.. meta::
   :title: Machine Learning / Digital Signal Processing
   :description: Get started using pipeline functions

Overview
--------

The SensiML Pipeline is a set of instructions for transforming sensor data into feature vectors which can be classified
using an algorithm trained using machine learning techniques. A pipeline must consist of a Segmenter, Feature Generator, Feature Transform and
Train Validate Optimize step. There are additional processing steps that can also be used, Such as Sensor Transforms, Sensor Filters,
Segment Transforms, Segment Filters, Samplers, Feature Selectors.

The following are description of functions that are translated to edge optimized code when you deploy a Knowledge Pack:

* **Sensor Transforms:** Act on a single sample of sensor data directly as a pre-processing step. Can create a new source that
  is fed as input to the next step in the pipeline. ie Ax,Ay,Az can become MagnitudeAxAyAz.


* **Sensor Filters:** Modifies a sensor in place and performs some sort of filtering (ie. moving average). This acts on a Sensor source
  that was either input or created using a sensor transform. This does not create a new source.


* **Segmentation:** Takes input from the sensor transform/filter step and buffers the data until a segment is found.


* **Segment Transforms:** Perform manipulations on an entire segment of data. Segment transforms modify the data in place, so if you use a
  segment transform be aware that your data will be modified.


* **Feature Generators:** A collection of feature generators work on a segment of data to extract meaningful information. The combination
  of the output from all feature generators becomes a feature vector.


* **Feature Transforms:** Perform row wise operations on a single feature vector. The most common feature transform in the pipeline is
  Min Max Scale, which translates the output of the feature generation step into 1byte feature values.


* **Classifier:** Takes a feature vector as an input and returns a classification based on a pre-defined model.


The following is a description of functions that are available as part of the SensiML Analytics cloud model optimization:


* **Feature Selectors:** Used to optimally select a subset of features before training a Classifiers


* **Samplers:** Used to remove outliers and noisy data before classification. Samplers are useful in improving the robustness of the model.


* **Training Algorithms:** Training algorithms are used to select the optimal parameters of a model.


* **Validation Methods:** Validation methods are used to check the robustness and accuracy of a model and diagnose if a model
  is overfitting or underfitting.

