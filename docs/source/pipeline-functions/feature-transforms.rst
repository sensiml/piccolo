.. meta::
   :title: Machine Learning / Digital Signal Processing - Feature Transforms
   :description: How to use feature transform pipeline functions

Feature Transforms
------------------

Perform row wise operations on a single feature vector. The most common feature transform in the pipeline is
Min Max Scale, which translates the output of the feature generation step into 1byte feature values.

.. automodule:: library.core_functions.feature_transforms
    :members: min_max_scale, normalize, quantize_254