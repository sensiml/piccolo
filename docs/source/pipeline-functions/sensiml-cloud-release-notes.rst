.. meta::
   :title: SensiML Cloud - Release Notes
   :description: Release notes history for SensiML Cloud

.. raw:: html

    <style> .blue {color:#2F5496; font-weight:bold; font-size:16px} </style>

.. role:: blue

===========================
SensiML Cloud Release Notes
===========================

Current Release
---------------

.. _sensiml-cloud-release-2024-1-2:

2024.1.2 (04/01/2024)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for SensiML Data Studio

:blue:`Bug Fixes`

* Fixes issue where sml_output.c file was not included with QuickFeather application


Past Releases
-------------

.. _sensiml-cloud-release-2024-1-1:

2024.1.1 (03/14/2024)
`````````````````````

:blue:`What's New`

Major Features

* Adds support to directly use labeled values in a pipeline without a segmentation algorithm. (Use Labels Segmenter)

Minor Features

* Adds support for SensiML Data Studio Client application

:blue:`Bug Fixes`

* Removes selected genetic algorithm steps if they are not included in the pipeline instead of raising an exception
* Stability improvements to the pipeline execution engine and autoscaling 


.. _sensiml-cloud-release-2024-1-0:

2024.1.0 (02/15/2024)
`````````````````````

:blue:`What's New`

Major Features

* Added quantization aware training (QAT) step for TensorFlow models
* Embedded SDK improved the generation of statistical metrics
* Added support for video synchronization
* Improved pipeline validation

Minor Features

* Added distribution of segments, samples, and feature vectors to pipeline step cache

:blue:`Bug Fixes`

* Fixed XC16/8 header file function
* Fixed bug where Classifier latency not showing up in the Model Download Screen


.. _sensiml-cloud-release-2023-3-0:

2023.3.0 (11/06/2023)
`````````````````````

:blue:`What's New`

Major Features Features

* Adds support for Linear Regression with OLS, Lasso, and Ridge training algorithms.
* Updates to use the SensiML Embedded SDK version 1.5. 
   * Removes support for deprecated functions
   * Adds support for multiple feature vector type inputs (float, int8, int16, uint8, uint16)
   * Adds support for returning results as a model_results object that contains the result and class probabilities
   * Adds additional APIs for getting model outputs for the feature vector, feature bank, segment buffers
   * Simplifies the overall kb_model_t struct
* Improves API for sandbox status results
* All trained models are retained until specifically deleted


:blue:`Bug Fixes`

* Fixes issues with xc32, xc16 compiler for some target processors

.. _sensiml-cloud-release-2023-2-2:

2023.2.2 (8/27/2023)
````````````````````

:blue:`What's New`

Minor Features

* Optimized performance for create/update/delete metadata and label capture relationships
* Deleting a pipeline no longer deletes associated Knowledge Packs
* Pipeline /data API now accepts query params to select the cached data

:blue:`Bug Fixes`

* Fixes issue with quantization calculation for inference in TensorFlow models
* Fixes issue where using an API key would incorrectly return a 403 error on some endpoints


.. _sensiml-cloud-release-2023-2-1:

2023.2.1 (8/21/2023)
````````````````````

:blue:`What's New`

Major Features

* Adds Temporal Convolution Neural Network Training Algorithm

Minor Features

* Adds support for downloading pipelines as .ipynb and .py files utilizing the Python SDK
* Updated the status for pipeline time to the format h:m:s
* Improve performance for compiling TensorFlow code
* Improved logging

:blue:`Bug Fixes`

* Fixed issue where unused magnitude transform could cause a divide by zero error when no columns were passed in
* Fixed issue where sometimes pipelines would not terminate correctly when killed by the user
* Fixed issue where DataSegments could be created that were empty due to packet loss in data collection
* Renamed peak to peak segmenter variable from boolean to bool which caused some issues on some compilers
* Updated the calculation of the quantization factor for TensorFlow models


.. _sensiml-cloud-release-2023-2-0:

2023.2.0 (8/21/2023)
````````````````````

:blue:`What's New`

Major Features

* Update TensorFlow Lite for Microcontrollers inference engine to latest version. 
* Adds voice activity detection algorithms (VAD) SILK and WebRTC algorithms
* Adds KWS template based on ds-cnn architecture with 16 filters in convolution blocks and trimmed feature vector of shape 49x16

Minor Features

* Adds dynamic query options to the Knowledge Pack REST API endpoint
* Knowledge Pack firmware downloads now have a consistent folder structure across platforms
* The model.tflite file is now returned as part of the Knowledge Pack firmware download for models with TensorFlow classifiers
* Server performance optimizations

:blue:`Bug Fixes`

* Capture Metadata Values are now set to only capture, label being unique
* Improve validation for feature file analysis endpoint


.. _sensiml-cloud-release-2023-1-5:

2023.1.5 (7/06/2023)
````````````````````

:blue:`What's New`

Minor Features

* Allow downloading and uploading TensorFlow Lite flatbuffer to Knowledge Pack API

:blue:`Bug Fixes`

* Fixed regression in the feature generator Cross Column Peak to Peak Difference
* Fixed issue with XC32 compiler for TensorFlow Lite models

.. _sensiml-cloud-release-2023-1-4:

2023.1.4 (4/20/2023)
````````````````````

:blue:`What's New`

Major Features

* Enhanced audio augmentation features.
* The Recognize Signal API now returns the output tensor/probabilities for each classification.

Minor Features

* Improved documentation for the machine learning pipeline function.
* Performance and scaling enhancements.

:blue:`Bug Fixes`

* Fixed an issue where running anomaly detection in the AutoML would sometimes result in a "not part of parameter inventory" error.



.. _sensiml-cloud-release-2023-1-3:

2023.1.3 (3/08/2023)
````````````````````

:blue:`What's New`

Major Features

* Adds Espressif ESP-IDF ESP32 compiler
* Adds support for M5Stack M5StickC PLUS ESP32-PICO Mini IoT Dev Kit

:blue:`Bug Fixes`

* Downloading a Knowledge Pack source that fails to build a library file will still return source code for most platforms. Previously, it would report an error that the library failed to compile.


.. _sensiml-cloud-release-2023-1-2:

2023.1.2 (2/28/2023)
````````````````````

:blue:`What's New`

Minor Features

* Improved API for downloading capture files
* Adds an additional keyword spotting model for 8000 sample (.5 second) keywords

:blue:`Bug Fixes`

* Add better error handling for when segments are filtered prior to Feature Generation


.. _sensiml-cloud-release-2023-1-1:

2023.1.1 (2/14/2023)
````````````````````

:blue:`What's New`

Major Features

* Adds API to the SensiML Embedded SDK for returning the output tensor probabilities from decision tree ensemble and neural network models

Minor Features

* Adds teammember_uuid to /user-info/ and /team-subscription/ API responses

:blue:`Bug Fixes`

* Fix issue where the password reset URL was getting set to http instead of https
* Fix issue with the sandbox out of resources error message referenced 1000 hours instead of 1000 credits


.. _sensiml-cloud-release-2023-1-0:

2023.1.0 (2/02/2023)
````````````````````

:blue:`What's New`

Major Features

* Optimized SensiML Embedded SDK improving latency of many feature generators by 25%
* Adds support for API key authentication
* Adds support for TensorFlow Lite for Microcontrollers for Microchip XC32
* Adds support to compile libraries for all Microchip device families (XC8, XC16, XC32)

Minor Features

* Adds asynchronous project delete endpoint
* Adds -fPIC to x86 compiled libtensorflow-microlite library to support creating .so
* Adds support for more balanced training epochs for Transfer Learning
* Adds UMAP, TSNE, and PCA, APIs to aid feature visualization

:blue:`Bug Fixes`

* Server stability improvements for uploading files
* Fix issue where Knowledge Packs would fail to compile if no resources were available, now waits instead
* Fix Knowledge Pack binary generation issue for QuickLogic QuickFeather and SparkFun QuickLogic Thing Plus - EOS S3

.. _sensiml-cloud-release-2022-4-0:

2022.4.0 (12/01/2022)
`````````````````````

:blue:`What's New`

Major Features

* Adds transfer learning training algorithm for foundation models
* Adds foundation models tailored toward keyword spotting
* Adds support for Microchip XC8, XC16 and XC32 Compilers

Minor Features

* Improved performance feature store and model store APIs
* Improved model profiling information for TensorFlow Lite models
* Improved pipeline logging

:blue:`Bug Fixes`

* Fixed firmware segment length calculation for models with sliding windows across multiple cascades
* Fixed firmware bug in run_model_feature_cascade_reset which was not advancing correctly when using a threshold filter in the pipeline
* Fixed bug with test model from pipelines that have a windowing segmenter with window size 1




.. _sensiml-cloud-release-2022-3-2:

2022.3.2 (10/03/2022)
`````````````````````

:blue:`What's New`

Minor Features

* Improved performance of firmware generation when downloading a Knowledge Pack
* Improved logging for running pipelines and Knowledge Pack generation

:blue:`Bug Fixes`

* Set min value of k-fold to 2 for all validation algorithms


.. _sensiml-cloud-release-2022-3-1:

2022.3.1 (9/07/2022)
````````````````````

:blue:`What's New`

Major Features

* Adds Knowledge Pack import/export API endpoints for importing and exporting custom Knowledge Packs

Minor Features

* Adds a family feature selector to allow feature selection by family groups (ie. all features from an MFCC feature generator would be used vs selecting individual bins)

:blue:`Bug Fixes`

* Fix issue where capture configurations without columns were causing models to fail code generation

.. _sensiml-cloud-release-2022-3-0:

2022.3.0 (8/04/2022)
````````````````````

:blue:`What's New`

Major Features

* Optimized pipeline caching performance
* Optimized query caching performance
* Optimized Windowing, Feature Cascade, and Min Max Scale performance
* Adds MFE Feature Extractor
* Adds Fully Connected NN to AutoML Search


Minor Features

* Optimized project-summary API endpoint
* Adds a delay parameter to the segment filter energy threshold
* Improved detailed logging messages
* Add explicit DataFile step to the pipeline
* Knowledge Pack models now generate features prior to filtering by default when cascade is enabled
* Improved overall functional and unit tests coverage

:blue:`Bug Fixes`

* Fix issue where capture_configuration was not always used during model download
* Fixed issue where segmenter parameters that were Bool values could be generated as "True" instead of "true"
* Adds last modified to project
* TensorFlowLite for Microcontrollers is now compiled with -FPIC for x86 GCC Generic to allow for shared library creation
* Adds validation to project names to avoid creating names that will not work on Windows
* Fixes issue where binary classification for TensorFlow models would return 127

.. _sensiml-cloud-release-2022-2-2:

2022.2.2 (5/18/2022)
````````````````````

:blue:`What's New`

Major Features

* Optimizations for capture file uploads
* Adds API documentation https://sensiml.cloud/api

Minor Features

* Improved descriptions of supported platforms

.. _sensiml-cloud-release-2022-2-1:

2022.2.1 (4/26/2022)
````````````````````

:blue:`What's New`

Major Features

* Adds support for the :doc:`/firmware/silicon-labs-xg24/silicon-labs-xg24`
* Adds support for accelerating NN ops using the Matrix Vector Processor on the :doc:`/firmware/silicon-labs-xg24/silicon-labs-xg24`
* Adds support for specifying int8/uint8 inputs to TensorFlow models (moving forward we will prioritize int8 support as most accelerators do not support uint8 inputs)

Minor Features

* The confusion matrix and accuracy in the Test Model tab of the Analytics Studio are now only compared against labeled ground truth data. Previously, unlabeled regions would be considered as the Unknown label.
* Adds a **backoff** parameter to the Segment Filter Energy threshold allow for **N** segments to pass after the threshold is triggered
* Adds support for storing a **color** value in against labels
* Improved error messages responses

:blue:`Bug Fixes`

* Fixes an issue where pipelines with downsampling filters report the wrong segment length
* The Feature Cascade feature transform now correctly drops segments with noncontiguous sections

.. _sensiml-cloud-release-2022-2-0:

2022.2.0 (3/23/2022)
````````````````````

:blue:`What's New`

Major Features

* Adds power spectrum feature generator
* Performance and stability improvements
* Support for Arduino Nicla Sense ME Platform

Minor Features

* Adds support for on device model profiling for Silicon Labs Thunderboard Sense 2
* Improved performance of Knowledge Pack firmware generation
* Improved support for tracking TensorFlow training
* Incorrect requests for capture files now returns the name of the file that does not exist instead of only raising a does not exist exception

Removed Features

* Removed support for the ``auto`` execution_type parameter from the pipeline API (/project/<uuid>/pipeline/<uuid>/)
* Deprecated version 1 of the Generate Knowledge Pack API

   * /project/<uuid>/knowledge-pack/<uuid>/generate_lib/
   * /project/<uuid>/knowledge-pack/<uuid>/generate_source/
   * /project/<uuid>/knowledge-pack/<uuid>/generate_binary/

:blue:`Bug Fixes`

* Fixes an issue with code generation for device profiling on some platforms

.. _sensiml-cloud-release-2022-1-1:

2022.1.1 (2/15/2022)
````````````````````

:blue:`What's New`

Minor Features

* Adds support for storing pipeline hyper_params to the SandBox API
* Performance and scalability improvements

.. _sensiml-cloud-release-2022-1-0:

2022.1.0 (2/2/2022)
```````````````````

:blue:`What's New`

Major Features

* Adds support for the :doc:`/firmware/infineon-psoc6/infineon-psoc6-cy8ckit-062s2-43012`

Minor Features

* Improved documentation for supported DSP and ML library functions
* Improved model registry support for TensorFlow models
* Improved AutoML training metrics results
* Adds support for removing unknown patterns from the PME after training
* Adds a new segment filter **Segment Energy Threshold Filter**
* Updated the **Adaptive Windowing Segmenter** algorithm to allow taking the absolute value of the signal
* Improved support for TensorFlow Lite files generated from the most recent versions of TensorFlow

:blue:`Bug Fixes`

* Fixes an issue with the logs for custom transforms
* Fixes an issue with the MAX_VECTOR_SIZE not being generated for some projects

2021.2.9 (12/27/2021)
`````````````````````

:blue:`What's New`

Minor Features

* Improved support for tracking pipeline CPU usage and runtime
* Additional query optimization improvements
* Improvements to query error messages on failure



2021.2.8 (11/12/2021)
````````````````````````

:blue:`What's New`

Minor Features

* Adds API to check if the query cache is in sync with the projects training data
* Adds support for the latest firmware for Microchip Technology SAMD21 ML Eval Kit (SAM-IoT WG)

:blue:`Bug Fixes`

* Fixes an issue with a missing header file in the Nordic Thingy binary download


2021.2.7 (11/04/2021)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for automatic onsemi sensor configuration file generation :doc:`onsemi RSL10<../firmware/onsemi-rsl10-sense/onsemi-rsl10-sense>`.
* Adds support for including the scratch buffers with custom feature generators, see :doc:`documentation<../knowledge-packs/adding-custom-functions-to-the-sensiml-toolkit>`.
* Adds support for custom feature generators that produce more than one feature, see :doc:`documentation<../knowledge-packs/adding-custom-functions-to-the-sensiml-toolkit>`.

Minor Features

* Adds better error handling and logging for custom feature generator upload
* Adds better logging for bonsai decision trees

2021.2.6 (10/29/2021)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for training fully connected neural network
* Adds anomaly detection for AutoML optimizations

Minor Features

* Adds streaming decimation filter
* Adds peak frequency feature generator

:blue:`Bug Fixes`

* Fixes codegen issue for multiple sensor filters
* Fixes query caching issue with overwriting cache


2021.2.5 (10/06/2021)
`````````````````````

:blue:`What's New`

Major Features

* Queries are now cached when executed by a pipeline or by calling the cache query API. By caching the query, your dataset is versioned to the time the query is created. This will speed up model execution time and allow you to continue to update your dataset, yet still build models/test models against older versions of the dataset. Query caches can be updated by calling the cache query API.
* Adds support for TensorFlow Lite for Microcontrollers inference on Raspberry Pi 3/4

2021.2.4 (9/22/2021)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for onsemi RSL10 Sense

Minor Features

* Adds the ability to return partial segments for general threshold segmenter if the capture file ends before segmentation finishes

:blue:`Bug Fixes`

* Fixes codegen issue for segment transforms which had magnitude transforms sensors
* Fixes codegen for correlation cross column feature generator
* Fixes sensor configuration for Microchip Knowledge Packs
* Always include testdata.h with Arm GCC Knowledge Packs
* Improved server stability


2021.2.3 (9/07/2021)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for Windows x86 Knowledge Pack libraries

:blue:`Bug Fixes`

* Fixes issue with Thunderboard Sense 2 Knowledge Pack binary sensor configuration
* Improved support for 8/16 bit microcontroller architectures


2021.2.2 (8/24/2021)
`````````````````````

:blue:`What's New`

Major Features

* Add support for M0/3/M0+ in processors for Knowledge Pack library downloads
* Adds support for latest tflite-micro inference engine https://github.com/tensorflow/tflite-micro

Minor Features

* Adds additional information to model.json in the Knowledge Pack download including Knowledge Pack summary and the expected input sensors

Beta Feature

* Add ability to add custom functions as part of the your DSP/ML pipelines, see documentation :doc:`(here)<../knowledge-packs/adding-custom-functions-to-the-sensiml-toolkit>`

:blue:`Bug Fixes`

* Fixes issue with password reset
* Fixes a bug where capture configurations created for MQTT/SN would incorrectly configure sensors for Knolwedge Pack SensiML AI applications

2021.2.1 (7/29/2021)
`````````````````````

:blue:`What's New`

Minor Features

* Adds ranges to all transform fields for better validation
* Improved Knowledge Pack profiling information

Feature Preview

* Add ability to add custom functions as part of the your DSP/ML pipelines (contact us for access)

:blue:`Bug Fixes`

* Fixes an issue where team admin could not delete some of their users
* Fixes some code generation issues for the MCHP and Android NDK builds
* Recognition now return an empty list instead of raising an exception when no segments are found
* Improved load balancing and server stability

2021.2.0 (6/30/2021)
`````````````````````

:blue:`What's New`

Major Features

 * Adds Knowledge Pack support for Microchip Technology SAMD21 ML Eval Kit (SAM-IoT WG)
 * Adds Knowledge Pack profiling option for cycle measurements of feature generators and classifier inference on platforms that support the DWT_CYCCNT register
 * Adds Knowledge Pack support for Android NDK
 * Adds support for custom pipelines as part of AutoML search
 * Adds support for using feature cascade as part of hierarchical model creation

:blue:`Bug Fixes`

 * Minor bug fixes and performance improvements

2021.1.2 (5/17/2021)
`````````````````````

:blue:`Bug Fixes`

 * Fixes source code download file extension to be .zip instead of tar.bz2
 * Removes deprecated kb_print_model_result from sml_recognition_run.c
 * Fixes issue with using custom feature generators with hierarchical models
 * Fixes recognition mode failing for Bonsai decision tree models


2021.1.1 (4/19/2021)
`````````````````````

:blue:`What's New`

Major Features

 * Adds additional Knowledge Pack APIs which enable finer control of pipeline step execution
 * Improved tuning of the TensorFlow memory usage to reduce the overall memory footprint of TF Lite models
 * Adds a model_json.h file to the library download which contains information about the Knowledge Pack pipeline

:blue:`Bug Fixes`

 * Fixes a bug in input contracts that affected some sample feature generators
 * Fixes a compile issue for QuickAI Knowledge Packs


2021.1.0 (3/04/2021)
`````````````````````

:blue:`What's New`


Major Features

 * Adds Support for SparkFun Thing Plus - QuckLogic EOS S3

:blue:`Bug Fixes`

 * Fix Audio Recognition for QuickFeather Binary where the audio Flag was not being set correctly

2020.3.1 (12/04/2020)
`````````````````````

:blue:`What's New`


Major Features

 * Adds community edition subscription tier https://sensiml.com/plans/community-edition/



2020.3.0 (11/10/2020)
`````````````````````

:blue:`What's New`


Major Features

 * Adds additional segment transforms to normalize segments
 * Allow source code download for enterprise and standard customers
 * Adds Cortex M7, Nano 33 library build option
 * Adds augmentation libraries for segment data
 * Adds ability to specify classifiers and training algorithms for AutoML search
 * Improved logging for AutoML pipelines
 * AutoML now returns the fitness score for all pipelines searched across

:blue:`Bug Fixes`

 * Fixes issue where scaling was not performed to the full width before MFCC feature extraction



2020.2.2 (09/08/2020)
`````````````````````


:blue:`What's New`

Minor Features

 * Adds additional Feature Extractors (linear regression stats, zero crossings, positive zero crossings, negative zero crossings, shape median difference, shape absolute median difference)


:blue:`Bug Fixes`

 * Performance improvements and minor bug fixes


2020.2.1 (08/19/2020)
`````````````````````


:blue:`What's New`

Major features

 * Adds support for `Quickfeather HDK <https://www.quicklogic.com/products/eos-s3/quickfeather-development-kit/>`_

Minor Features

 * Adds support for multi-channel DTW
 * Adds additional feature generators
 * Performance improvements


:blue:`Bug Fixes`

 * Improved validation for custom sensors


2020.2.0 (07/17/2020)
`````````````````````

:blue:`What's New`

Major features

 * Adds ability to test multiple captures in a single calls.
 * Adds ability to generate confusion matrix for a target label when running test data.
 * Adds ability to download source file for enterprise level accounts.
 * Allow user to specify which classifier algorithms will be used as part of AutoML optimization.

Minor Features

 * Increased the number of decision trees available in random forest and boosted tree ensembles during inference.


:blue:`Bug Fixes`

 * Fixes issue where sensor columns could be generated in different order than sensor configuration specified




2020.2.0 (07/17/2020)
`````````````````````

:blue:`What's New`

Major features

 * Adds ability to test multiple captures in a single calls.
 * Adds ability to generate confusion matrix for a target label when running test data.
 * Adds ability to download source file for enterprise level accounts.
 * Allow user to specify which classifier algorithms will be used as part of AutoML optimization.

Minor Features

 * Increased the number of decision trees available in random forest and boosted tree ensembles during inference.


:blue:`Bug Fixes`

 * Fixes issue where sensor columns could be generated in different order than sensor configuration specified



2020.1.6 (05/04/2020)
`````````````````````

:blue:`What's New`

Major features

 * Adds ability to specify decision tree of strong classifiers to optimize against

Minor Features

 * Adds Interleave feature generator for combining sensors channels
 * Performance improvements and bug fixes



2020.1.5 (04/14/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Adds a threshold setting to tflite post processing to return unknown below threshold value
 * Improvements to database query performance
 * caching optimizations for increased performance


2020.1.4 (04/02/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Improvements to tensorflow-lite micro support
 * Improvements to database query performance
 * Adds API's to Knowledge Pack for setting feature vector directly as well as recognizing feature vector

2020.1.3 (03/23/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Improvements to tensorflow-lite micro support
 * Additional Bulk API's for faster egress
 * Minor bug fixes

2020.1.2 (03/03/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Adds new bulk API's to improve performance of uploading/deleting/updating multiple segments at the same time
 * Improved performance for a number of feature transforms and extractors
 * adds beta support for tensorflow lite micro
 * Adds a more detailed query statistics endpoint for richer information
 * Adds ability to include the segment_uuid in the query

2020.1.1 (02/04/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Adds new segment filter threshold algorithm

2020.1.0 (01/20/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Adds Profiling and better debug logs to Knowledge Packs
 * Increased Max Feature vector size to 2048

Minor Features

 * Adds option to use less than comparison as part of the windowing threshold algorithm
 * Adds DTW to Hierarchical Clustering Training Algorithm

:blue:`Bug Fixes`

 * Fixes issue where auto segmentation heuristics would generate invalid parameter settings
 * Fixes issue where DTW distances larger than uint16 were not being truncated
 * Fixes issue where Mayhew board could be configured incorrectly when generating a Knowledge Pack
 * Minor bug fixes and performance improvements

2019.3.6 (11/05/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Support for sqlite optimized Data Studio

Minor Features

 * Computed distances for PME are stored as part of the knowledge pack
 * Model Size is stored as part of the Knowledge Pack

2019.3.5 (10/21/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Support for  AD7476 Sensor at up to 1Mhz

Minor Features

 * Additional API for flushing model ring buffer to clean state
 * Stability Improvements

2019.3.4 (10/08/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Boosted tree classifiers now part of autosense optimization routine

:blue:`Bug Fixes`

 * Stability improvements to pipeline performance scheduling

2019.3.3 (09/23/2020)
`````````````````````

:blue:`Bug Fixes`

 * Fixed issue where feature validation was to strict for some validation methods
 * Improved error message reporting for Knowledge Pack downloads

2019.3.2 (09/19/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Implementation of bonsai decision tree classifier which combines dimensionality reduction with an efficient tree classifier structure
 * Store full results from train, validation and test in the Knowledge Pack
 * Performance and stability improvements

:blue:`Bug Fixes`

 * Fixed issue where some column name characters weren't being correctly sanitized during firmware generation

2019.3.1 (08/22/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Addition of Dynamic Time Warping as a distance metric for the PME classifier
 * Added two new model selection methods (metadata k-fold, and stratified metadata-kfold)

2019.3.0 (07/30/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Support for SensorTile 1.0 Knowledge Pack Binary and Library Builds

2019.2.0 (06/27/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Adding for under sampling the majority class in order to balance a data set
 * Adding support as part of auto sense pipeline for balancing data sets
 * Adding support for supplying a user specified validation method to the auto sense pipeline
 * Adding support for specifying capture uuid as part of the metadata in a query

:blue:`Bug Fixes`

 * Fixes issue with some queries failing due to the names of the metadata

2019.1.4 (06/11/2020)
`````````````````````

:blue:`What's New`

Major Features

 * Adding support for Chilkat Hardware Knowledge Pack creation

Minor Features

 * Improvements to accuracy calculations of AutoSense pipeline

2019.1.3 (06/04/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Speed optimizations for recognize signal
 * Project statistics now returns information about all captures and segments

:blue:`Bug Fixes`

 * Fixed issue where having a decision tree ensemble and gradient boost classifier in the same model would fail to compile
 * Fixed issue where terminating a pipeline wasn't always removing it from the active pipeline queue

2019.1.2 (05/22/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Speed improvements to AutoSense pipeline and underlying training algorithms
 * QuickAI SDK 1.2.1 release.

:blue:`Bug Fixes`

 * Fixed issue in QuickAI 1.2 SDK when recording using ADC with 3 channels

2019.1.1 (05/14/2020)
`````````````````````

:blue:`What's New`

Minor Features

 * Improved server performance to increase number of batch jobs executed in parallel during pipeline execution

:blue:`Bug Fixes`

 * Fixed issue where uploading a large feature vector file could being split up before being sent to the TVO or selector set steps

2019.1.0 (05/05/2020)
`````````````````````

:blue:`What's New`

QuickLogic S3 AI Recognition updates

 * Support for recognition from 1-4 Channel ADC Mayhew at 16khz
 * Support for recognition for 1 Channel ADC Mayhew at 100khz
 * Support for recognition of Audio at 16khz
 * Support for IMU recognition from 25-1600Hz

AutoSense Pipeline

 * Includes random forest algorithm as part of the search over the classifier space
 * Now allows users to select whether or not to use a classifier that will return unknown when it is unsure of the result
 * Allows users to build a submodel using autogrouping of classes

Other Major Features

 * Added a boosted tree ensemble classifier that performs binary classification
 * Captures can now be associated with the capture configuration that created them
 * Improvements to upload speed of metadata labels
 * Status messages now return more information about running pipelines

Notes: The minimum SensiML client version is 2019.1.0

:blue:`Bug Fixes`

 * Fixed issue where pipeline would appear to be in the queue but actually be running

2.5.1 (02/28/2020)
``````````````````

:blue:`What's New`

 * General performance improvements
 * General Security improvements

Notes: The minimum SensiML client version is 2.5.3

2.5.0 (01/15/2020)
``````````````````

:blue:`What's New`

 * Additional Board Support for ChilKat platform
 * Feature generators automatically iterate through input columns and specify their correct input
 * Major Server Stability Improvements for handling larger data sizes
 * AutoGenerated Knowledge Packs now support knowledge rehydration, previously only pipeline rehydration was supported
 * New segmentation, feature generation and sampling algorithms added
 * Any segmenter can be used as input to cascade feature
 * Ability to specify multiple datafiles as input to a pipeline
 * Better error messages returned for many endpoints
 * Naming convention for classifier "PVP" has been deprecated,  all pipelines are required to use the name "PME" for this classifier

Notes: The minimum SensiML client version is 2.5

:blue:`Bug Fixes`

 * Knowledge Pack rehydration now accounts for feature family generators

2.4.0 (11/09/2018)
``````````````````

:blue:`What's New`

 * Additional Feature generator

    - Convolution Max


 * Additional Streaming Filter

    - Downsample
    - High Pass

 * High Frequency Data Collection using the Quick AI Module
 * HW acceleration support for QuickAI Hard Neurons
 * DSP optimizations for Knowledge Packs built targeting arm m3/m4 processors

2.3.3 (10/31/2018)
``````````````````

:blue:`Bug Fixes`

 * Support for segments up to length 8192
 * Server Stability Improvements
 * Improvements to error messages
 * Improvements to QuickAI FFE data capture

2.3.2 (10/24/2018)
``````````````````

:blue:`What's New`

 * Adding Support for QuickAI low power ffe for pre-processing sensor data
 * Increase number of classes supported by PME reinforcement learning
 * Adding model.json to Knowledge Pack download that has information about the contained model
 * Stability and speed improvements to Auto Sense pipelines

:blue:`Bug Fixes`

 * Fix Hierarchical Clustering bug where Nan was being returned and causing a crash

2.3.1
`````

:blue:`What's New`

 * Custom validation method can be used by the automation engine
 * Additional API’s for Knowledge Pack to enable loading/saving models to/from flash

    - flush_model
    - get_model_header
    - get_model_pattern

 * Additional API’s for Knowledge Pack to support cascade windowing with reset

2.3.0
`````

:blue:`What's New`

Major Features

 * QuickAI board now supports capture and SensiML recognition without re-flashing
 * Adding support for reinforcement learning to PME algorithm on the device
 * Adding API’s to the c Knowledge Pack to retrieve information about the model such as the class map, model patterns, model map etc. (see kb.h for full list of API’s)

Minor Features

 * Pipeline status is returned during pipeline execution
 * General stability improvements and bug fixes
 * Return a model.json file with all Knowledge Packs that describes the model
 * Bug Fix where terminating a pipeline didn’t terminate correctly all the time

2.2.2
`````

:blue:`What's New`

Major Features

 * Adding software support for QuickAI board (hardware accelerated classification and FPGA feature generation acceleration support will be added in future releases)
 * Adding ability to use the emulator for hierarchical models via recognize_signal
 * Added Knowledge Pack support for decision tree ensemble trained via random forest training algorithm
 * Adding new class of feature generators (cross column) for use in comparing features across sensor columns

Minor Features

 * Hierarchical models now generate their calls to arbitrary depth
 * Added two tail t-test based feature selector
 * Min max scale now accepts partial parameters and will scale the rest
 * General stability improvements and bug fixes

2.2.1
`````

:blue:`What's New`

Major Features

 * Library Code generation for RPI, Arm and Ubuntu with gcc version 7.2
 * Support for constructing a feature vector from multiple sliding windows

Minor Features

 * Added Moving Average Sensor Transform
 * SensiML Labs (Experimental Features)
 * Random Forest Classifier (Important: This feature is in an early concept stage, it cannot be used on a device)
 * Adding an API to add new patterns to the device while it is running

:blue:`Bug Fixes`

 * Schema error on upload now returns message for which fields are incorrect
 * Minor bug fixes and stability improvements

2.2.0
`````

:blue:`What's New`

New Platforms

 * FreeRTOS

Major Features

 * Automation now has a cross validation option to prevent under/overfitting
 * Adding double peak segmentation algorithm (a key based segmentation algorithm)

Minor Features

 * KP download now includes option to explicitly define source (Audio, Motion, Custom)
 * Combine labels allows renaming labels and creating new groups
 * Auto Combine label, automatically splits many events into two groups

SensiML Labs (Experimental Features)

 * Adding Cascade Windowing Segmenter (Important: This feature is in an early concept stage, it cannot be used on a device)
 * Adding Bonsai Decision Tree Classifier (Important: This feature is in an early concept stage, it cannot be used on a device)

:blue:`Bug Fixes`

 * Fixes to pipeline seeds for automation
 * Fix overflow bug for raw data

2.1.3
`````

:blue:`What's New`

Major Features

 * Metadata Separator for choosing the best class split in Hierarchical models

2.1.2
`````

:blue:`What's New`

Major Features

 * Adds outlier removal samplers for improving model accuracy

:blue:`Bug Fixes`

 * Fixes bug with Hierarchical Models not returning correct results

2.1.1
`````

:blue:`What's New`

Major Features

 * Support for building Knowledge Packs using audio data for Nordic Thingy

Minor Features

 * Added ability to specify a capture file as the test data in recognize signal
 * Add new transform for grouping labels into subgroups. See Combine Labels in docs
 * Added ability to use entire segment from parent model for submodels
 * Adds a padding option to min max scale which can improve classification accuracy in some cases

:blue:`Bug Fixes`

 * Fixed issues with some feature generators (conv avg, min percentile, sum)
 * Fix some issues with correlation feature selectors

2.1.0
`````

:blue:`What's New`

Major Features

 * Knowledge Pack compatibility with Nordic Thingy

Minor Features

 * Server side optimizations for faster query performance

:blue:`Bug Fixes`

 * Queries not correctly selecting segments when labels have been created by more than one autosegmenter
 * Fix integer overflow in magnitude sensor transform when more than 2 axis are used

2.0.0
`````

:blue:`What's New`

Major Features

 * **Pipeline Automation** - Automated pipelines reduce the amount of code you have to write to find good features and pipeline parameters. Use pre-defined Pipeline Seeds ("Basic Features", "Advanced Features", "Downsample Features", "Histogram Features") - or define your own pipeline and let the automation API fine-tune the parameters with its genetic algorithm.\
 * **Convolution/Submodels** - A segment captured and classified by one model, can be fed and used by other models which can use the entire segment or perform their own segmentation
 * **Segmenter Discovery/Optimization** - Given a labeled data set, the server will optimize the parameters for detecting those segments from the signal

Minor Features

 * Optimization for core function for latency and memory usage
 * SensiML Python SDK list functionality - for most types of objects on the server is now supported. client.list_* to allow easy information discovery
 * Knowledge Packs can now be saved and retrieved by name. models from multiple pipelines/projects can now be combined into a single binary file
 * Grid Search can now be performed over the validation, classifier and training algorithm of the tvo step. The option to replace Hierarchical Clustering with Neuron Optimization in the grid search has been removed. To use Neuron Optimization, use it in the pipeline tvo step like all other training algorithms
 * Addition of new feature generators and transforms

    - Transform: Pre-emphasis Filter
    - Feature Generator: MFCC
    - Feature Generator: FFT
    - Feature Selector: Custom Feature Selection
    - Validation Method: Set Sample Validation
