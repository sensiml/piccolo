.. meta::
   :title: Machine Learning / Digital Signal Processing - Feature Generators
   :description: How to use feature generator pipeline functions

Feature Generators
------------------

A collection of feature generators work on a segment of data to extract meaningful information. The combination
of the output from all feature generators becomes a feature vector.



Statistical
^^^^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_stats
    :members:


Histogram
^^^^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_histogram
    :members: fg_fixed_width_histogram, fg_min_max_scaled_histogram

Sampling
^^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_sampling
    :members:  fg_sampling_downsample, fg_sampling_downsample_avg_with_normalization, fg_sampling_downsample_max_with_normalization


Rate of Change
^^^^^^^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_rate_of_change
    :members:

Frequency
^^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_frequency
    :members: fg_frequency_dominant_frequency, fg_frequency_peak_frequencies, fg_frequency_spectral_entropy, fg_frequency_power_spectrum, fg_frequency_mfcc, fg_frequency_mfe


Shape
^^^^^

.. automodule:: library.core_functions.feature_generators.fg_shape_amplitude
    :members:

Time
^^^^

.. automodule:: library.core_functions.feature_generators.fg_time
    :members:

Area
^^^^

.. automodule:: library.core_functions.feature_generators.fg_area
    :members:

Energy
^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_energy
    :members:

Physical
^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_physical
    :members:


Sensor Fusion
^^^^^^^^^^^^^

.. automodule:: library.core_functions.feature_generators.fg_cross_column
    :members:


