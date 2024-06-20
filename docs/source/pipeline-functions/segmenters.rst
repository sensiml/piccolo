.. meta::
   :title: Machine Learning / Digital Signal Processing - Segmenters
   :description: How to use segmenter pipeline functions

Segmenters
----------

Takes input from the sensor transform/filter step and buffers the data until a segment is found.

.. automodule:: library.core_functions.segmenters.sg_windowing
    :members:

.. automodule:: library.core_functions.segmenters.sg_manual
    :members:

.. automodule:: library.core_functions.segmenters.sg_windowing_threshold
    :members: windowing_threshold

.. automodule:: library.core_functions.segmenters.sg_max_min_threshold
    :members: max_min_threshold

.. automodule:: library.core_functions.segmenters.sg_general_threshold
    :members: general_threshold

.. automodule:: library.core_functions.segmenters.sg_double_peak
    :members: double_peak_key_segmenter

.. automodule:: library.core_functions.segmenters.sg_p2p_threshold_segmenter
    :members: peak_to_peak_segmenter_with_thresholding