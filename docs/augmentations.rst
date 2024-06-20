.. meta::
   :title: Machine Learning / Digital Signal Processing - Augmentation
   :description: How to use augmentation pipeline functions



Augmentation
````````````

Data augmentation benefits users by expanding the provided data for training a model. This helps to reduce over-fitting, which can occur when a model is trained on a limited amount of data. Data augmentation also helps to reduce bias in the training data by introducing additional variations of the same data. This helps to make the model more generalizable and better able to handle unseen data. Additionally, data augmentation can help to improve the accuracy of the model by introducing additional, more difficult data.

In many cases, users collect their data in a controlled conditions of a lab environment where data is clean and noise free. Most models that are built based on such data do not necessarily perform well in noisy conditions. One way to address the issue is to collect large datasets under various noisy conditions of a more realistic setup. Preparing realistic environments is not always easy and in most cases increases the costs of data collection.

Data augmentation is an alternative way to mitigate the issue by bringing synthetic data to the modeling process which consequently reduces the amount of data needed to train a model, and allows more efficient use of resources.

SensiML offers a set of augmentation methods for time series data. Each augmentation method is implemented as a member of an augmentation set. A function in the augmentation set uses segmented time series data individually. The subset will be created for each method individually and concatenated with the original data. Currently the supported augmentation methods are 

* **Add Noise:** Add random noise to time series. The added noise to each sample is independent and follows the distribution provided by the method parameter.

* **Scale Amplitude:** Scaling the target sensor values. All targeted sensors of the selected segment are scaled according to a scale factor randomly chosen from the provided scale range.

* **Time Shift:** Shifting segments along the time axis. The segment is padded with the signal average within the window of specified size.

* **Time Stretch:** Change the temporal resolution of time series. Time stretching/compression is often used to alter the tempo or speed of an audio signal without changing the pitch. The resized time series is obtained by linear interpolation of the original time series.

* **Pitch Shift:** Pitch shifting is used to change the pitch of an audio signal without changing its tempo or speed.

* **Random Crop:** Randomly cropping a set of long input segments. A set of output segments of the same size are generated. The starting point of each segment is drawn randomly. The odds of larger segments to contribute to the output set are proportional to their size.

* **Time Flip:**  Flipping the signal along the time axis. This augmentation is used to decrease the false positive rate by increasing the model sensitivity to feed-forward signals. The label of the flipped signal is different than the label of the original signal, usually "Unknown". 

Users are given the option to select a subset of the original data set by setting the following parameters:

- `target_labels`: A list of chosen labels. If not defined, the augmentation is applied on all labels.
- `filter`: A Dictionary to define the desired portion of the input data for augmentation. Dictionary keys are the names of metadata columns each referring to a selected list of metadata values.  
- `selected_segment_size_limit`: Range of the allowed segment lengths for augmentation.


Managing augmented data
```````````````````````

To avoid any overlaps between training and validation sets, we require that the augmented segments do *NOT* contribute to the validation set. As such, to partition the sample, all augmented segments are ignored prior to the splitting process. Then, all augmented segments are added to the training set except for those whose original counterparts are already in the validation set.   

In order to track the augmented segments, their UUID is designed to follow specific formats while preserving some parts of the original UUID. Here, the unaltered segments returned by the query are called original segments. The UUID of a cropped original segment has the semi-original UUID format. Cropping an augmented segment generate segments whose UUIDs follow the augmented UUID format. The UUID of a segments that goes through multiple rounds of augmentation transformations always follow the augmented format.

UUID formats are 

- **Original Segment:** `yyyyyyyy-yyyy-xxxx-xxxx-xxxxxxxxxxxx`             
- **Augmented Segments:** `yyyyyyyy-yyyy-fffc-xxxx-xxxxxxxnnf01`           
- **Semi-original Segments:** `yyyyyyyy-xxxx-eee4-xxxx-xxxxxxxxxxee`

where

`y` is the wildcard carried over from the original signal UUIDs. `f` and `e` are reserved codes for augmented or semi-original (cropped original) segments. `c` is the numeric code of the last augmentation transformation. For the augmented segments, `nn` is replaced with the checksum control digits derived from `yyyyyyyy-yyyy-fffc-xxxx-xxxxxxx`. `nn` is the two rightmost digits of the sum of all digits in hex format. The first 8 digits of UUIDs (`yyyyyyyy`) are used to find and match the segments of the same origin.

The usage of each augmentation method is fully documented below. Here is the input data set used for each of the examples

Original Data::

            accelx  accely  accelz     Class  Rep Subject                          segment_uuid  SegmentID
         0      377     569    4019  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
         1      357     594    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
         2      333     638    4049  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
         3      340     678    4053  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
         4      372     708    4051  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          0
         5      410     733    4028  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
         6      450     733    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
         7      492     696    3947  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
         8      518     677    3943  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
         9      528     695    3988  Crawling    1     s01  07baf4b8-21b9-4b98-8927-de1264bb2a92          1
         10     -44   -3971     843   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
         11     -47   -3982     836   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
         12     -43   -3973     832   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
         13     -40   -3973     834   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
         14     -48   -3978     844   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          0
         15     -52   -3993     842   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
         16     -64   -3984     821   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
         17     -64   -3966     813   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
         18     -66   -3971     826   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
         19     -62   -3988     827   Running    1     s01  e2a80997-346a-4327-8fa4-2de7de65ac99          1
           

Add Noise
^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: add_noise


Scale Amplitude
^^^^^^^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: scale_amplitude


Time Shift
^^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: time_shift


Time Stretch
^^^^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: time_stretch


Pitch Shift
^^^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: pitch_shift


Random Crop
^^^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: random_crop


Time Flip
^^^^^^^^^

.. automodule:: library.core_functions.augmentation
    :members: time_flip

