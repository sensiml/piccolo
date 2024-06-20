.. meta::
   :title: Machine Learning / Digital Signal Processing - Sensor Filters
   :description: How to use sensor filters pipeline functions

Sensor Filters
--------------

Modifies a sensor in place and performs some sort of filtering (ie. moving average). This acts on a Sensor source
that was either input or created using a sensor transform. This does not create a new source.


.. automodule:: library.core_functions.sensor_filters
    :members: streaming_downsample_by_averaging, tr_high_pass_filter, st_moving_average, streaming_downsample_by_decimation
