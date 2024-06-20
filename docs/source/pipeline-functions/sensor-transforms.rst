.. meta::
   :title: Machine Learning / Digital Signal Processing - Sensor Transforms
   :description: How to use sensor transforms pipeline functions

Sensor Transforms
-----------------

Act on a single sample of sensor data directly as a pre-processing step. Can create a new source that
is fed as input to the next step in the pipeline. ie Ax,Ay,Az can become MagnitudeAxAyAz.

.. automodule:: library.core_functions.sensor_transforms
    :members: tr_magnitude, tr_average, tr_absolute_average

