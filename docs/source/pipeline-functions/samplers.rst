.. meta::
   :title: Machine Learning / Digital Signal Processing - Samplers
   :description: How to use sampler pipeline functions

Samplers
--------

Used to remove outliers and noisy data before classification. Samplers are useful in improving the robustness of the model.

.. automodule:: library.core_functions.samplers
    :members: sample_by_metadata, sample_combine_labels, sample_zscore_filter, sigma_outliers_filtering, local_outlier_factor_filtering, isolation_forest_filtering, one_class_SVM_filtering, robust_covariance_filtering
    :noindex:

Sampling Techniques for Handling Imbalanced Data sigma_outliers_filtering

.. automodule:: library.core_functions.samplers
    :members:  sample_combine_labels, undersample_majority_classes
    :noindex:

Sampling Techniques for Augmenting Data Sets

.. automodule:: library.core_functions.samplers
    :members: augment_pad_segment, sample_metadata_max_pool
    :noindex: