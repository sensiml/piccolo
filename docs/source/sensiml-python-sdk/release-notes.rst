.. meta::
   :title: SensiML Python SDK - Release Notes
   :description: Release notes history for the SensiML Python SDK

.. raw:: html

    <style> .blue {color:#2F5496; font-weight:bold; font-size:16px} </style>

.. role:: blue

=============
Release Notes
=============

Current Release
---------------

.. _sensiml-python-sdk-release-2023-3-0:

2023.3.0 (11/06/2023)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for models built using the SensiML Embedded SDK v1.5


Past Releases
-------------


.. _sensiml-python-sdk-release-2023-2-1:

2023.2.1 (9/13/2023)
`````````````````````

:blue:`What's New`

Minor Features

* Adds support for downloading pipelines as .ipynb and .py files



.. _sensiml-python-sdk-release-2023-2-0:

2023.2.0 (8/21/2023)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for downloading and uploading projects

Minor Features

* Update SMLRunner to support latest KnowledgePack firmware folder structure



.. _sensiml-python-sdk-release-2023-1-3:

2023.1.3 (4/20/2023)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for audio augmentation in the training pipeline.


:blue:`Bug Fixes`

* Fixes the dclproj upload to ignore labels with local status "To Be Deleted".


.. _sensiml-python-sdk-release-2023-1-2:

2023.1.2 (2/23/2023)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for computing the confusion matrix between two DataSegments objects (ie. model predictions vs ground truth)
* Adds support for applying the nearest label_value from one DataSegments object to the DataSegments in another DataSegments obj
* Adds support for uploading labels directly from a DataSegments object
* Adds the client download_capture API for downloading a single capture files data from a project
* Adds the client download_captures API, which is an optimized API for downloading multiple capture files from a project
* Removes deprecated DataSegmentsV1 API

.. _sensiml-python-sdk-release-2023-1-1:

2023.1.1 (2/14/2023)
`````````````````````

:blue:`What's New`

Major Features

* Adds support to SMLRunner for showing the output tensor probabilities from decision tree ensemble and neural network models

Minor Features

* Improved error handling for client connection

.. _sensiml-python-sdk-release-2023-1-0:

2023.1.0 (2/02/2023)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for API key authentication
* Adds support for uploading projects exported from the SensiML Data Studio in the .dcli format

Minor Features

* Adds logging from submitting a sandbox that includes remaining cpu credits and task_id


:blue:`Bug Fixes`

* Adds trailing \ to version checking API

.. _sensiml-python-sdk-release-2022-3-2:

2022.3.2 (12/01/2022)
`````````````````````

:blue:`What's New`

Minor Features

* Adds API to get team account resource usage information client.account_info()


.. _sensiml-python-sdk-release-2022-3-1:

2022.3.1 (10/03/2022)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for uploading a project from a .dclproj file

   .. code-block:: python

      client.upload_project("PROJECT_NAME", proj_path)


:blue:`Bug Fixes`

* Fix issue where validating the SDK could fail if connected to a server that doesn't return a server version


.. _sensiml-python-sdk-release-2022-3-0:

2022.3.0 (9/06/2022)
````````````````````

:blue:`What's New`

Major Features

* Adds a DataSegmentsV2 API which improves and simplifies over the DataSegments API (DCLProj now uses DataSegmentsV2)
* Adds an Export KnowledgePack API which allow users to export Knowledge Packs to share or modify with other users and projects.
* Adds a create KnowledgePack API that allows users to upload custom knowledge packs which can be compiled using code generation.

Minor Features

* Adds support for a version check which warns users if their version of the Python SDK is compatible with the current server version

.. _sensiml-python-sdk-release-2022-2-4:

2022.2.4 (8/04/2022)
````````````````````

:blue:`What's New`

Minor Features

* Improved function docstrings
* Adds client.capture_configurations() API for getting capture configurations objects
* Adds client.get_pipelines() API for getting pipelines objects
* Adds client.get_queries() API for getting query objects
* Adds client.pipeline.to_list() API for converting the current pipeline to JSON format
* Adds client.upload_sensor_dataframe() and client.upload_feature_dataframe() APIs to upload either DataFiles or FeatureFiles
* client.pipeline.set_input_data() now takes an optional group_columns argument
* Adds DataFileCall API

.. _sensiml-python-sdk-release-2022-2-3:

2022.2.3 (5/18/2022)
````````````````````

:blue:`What's New`

Minor Features

* Improved documentation
* Removed deprecated pipeline seeds API
* Renamed the main class in client.py from **SensiML** to **Client** (SensiML import still works, but is deprecated)

.. _sensiml-python-sdk-release-2022-2-2:

2022.2.2 (4/27/2022)
````````````````````

:blue:`What's New`

Minor Features

* Adds support setting the **color** property of a label value
* Adds support in the pipeline feature_to_tensor method for converting features to int8 and specifying their shape

.. _sensiml-python-sdk-release-2022-2-1:

2022.2.1 (3/2/2022)
```````````````````

:blue:`What's New`

Major Features

* Adds support for importing/exporting DataSegments into Audacity labels
* Adds support for running Knowledge Packs on Windows using the Python SDK

.. _sensiml-python-sdk-release-2022-2-0:

2022.2.0 (2/15/2022)
````````````````````

:blue:`What's New`

Major Features

* Adds support for converting a DataSegments object into a .dcli file
* Adds support for merging, filtering, and joining the segments of a DataSegments object
* Adds support for computing the confusion matrix between two DataSegments objects
* Adds support for importing classification results exported from the Data Studio into a DataSegments object
* Adds some additional plotting to the DCLProject API for visualizing frequency data along with labels

.. figure:: /sensiml-python-sdk/img/release-notes/plot_frequency.png
   :align: center

:blue:`Bug Fixes`

 * Fixes a bug with the create_query API where session strings would raise an exception

.. _sensiml-python-sdk-release-2022-1-0:

2022.1.0 (2/2/2022)
```````````````````

:blue:`What's New`

Major Features

* Adds support for converting a .CSV file into a .DCLI file

Minor Features

* Remove a number of installation dependencies
* Removes deprecated python widgets


2021.11.12 (11/12/2021)
```````````````````````

:blue:`What's New`

Major Features

* Adds support for reading .wav files in DCLProject API
* Adds support for checking if the query cache is up to date with the training data
* Adds support for uploading custom features that return more than one feature
* Adds support for uploading custom features that use a scratch buffer

Minor Features

* Improvements to the sandbox response API to return more information

2021.2.1 (10/04/2021)
`````````````````````

:blue:`What's New`

Major Features

* Improved support for DCLProject API, see documentation :doc:`here <../sensiml-python-sdk/api-methods/dcl-project>`
* Adds support for the cache query API, see documentation :doc:`here <../sensiml-python-sdk/api-methods/queries>`


2021.2.0 (8/24/2021)
`````````````````````

:blue:`What's New`

Major Features

* Adds support for including custom functions as part of the sensiml pipeline, see documentation :doc:`here <../knowledge-packs/adding-custom-functions-to-the-sensiml-toolkit>`


2021.1.0 (3/17/2021)
`````````````````````

:blue:`What's New`

* Update client.create_query to include the option for passing in the Name of the segmenter instead of the id.

:blue:`Bug Fixes`

 * Fixes issue where refresh token is not reset correctly on failed login.


2020.3.0 (11/10/2020)
`````````````````````

:blue:`What's New`

 * Adds API for data augmentation pipeline step
 * Improves snippets functionality for building pipelines

:blue:`Bug Fixes`

 * Fix issue where data columns were being sorted prior to building pipeline step

2020.2.1 (07/07/2020)
`````````````````````

:blue:`What's New`

 * Adds API to delete Knowledge Packs

      client.delete_knowledgepack(uuid)
      kp = client.get_knowledgepack(uuid)
      kp.delete()

 * Adds API to view featurefiles stored on the server

      client.list_featurefiles()
      client.get_featurefile(uuid)

 * Adds API to view datafiles stored on the server

      client.list_datafiles()
      client.get_datafiles(uuid)


2020.2.0 (07/07/2020)
`````````````````````

:blue:`What's New`

 * Adds tensorflow helper functions
 * Adds support for local queries against Data Studio Project
 * Adds support for bulk updates/creates for Labels, Label_Values, Capture Label and Metadata Relationships


2020.1.2 (03/03/2020)
`````````````````````

:blue:`What's New`

 * Ability to query by segment_uuid
 * Adds more detailed statistics for queries

2020.1.1 (02/12/2020)
`````````````````````

:blue:`Bug Fixes`

 * Fixed bugs with installer

2020.1.0 (01/20/2020)
`````````````````````

:blue:`What's New`

 * Adds the ability to visually plot features in the model explore widget

.. figure:: /sensiml-python-sdk/img/release-notes/explore-models-plot-features.png
   :align: center
..

 * Improvements to debug log outputs and addition of profiling option

.. figure:: /sensiml-python-sdk/img/release-notes/debug-log-output.png
   :align: center
..

 * Adds option for automating the creation of a hierarchical model which can provide increased accuracy but may increase the size of the model

.. figure:: /sensiml-python-sdk/img/release-notes/model-building-hierarchical-optimization.png
   :align: center
..


2019.3.6 (11/13/2019)
`````````````````````

:blue:`Bug Fixes`

 * Specifies a version for pywin32 as the latest version is breaking installs

2019.3.5 (10/21/2019)
`````````````````````

:blue:`What's New`

Minor Features

 * Better rendering of error messages in the Dashboard
 * Dashboard now resizes the notebook width on refresh
 * API updates

2019.3.4 (09/19/2019)
`````````````````````

:blue:`What's New`

Major Features

 * Autosense pipeline now runs asynchronously and has a terminate button
 * Project and Pipeline are now locked while autosense is running

2019.3.3 (09/19/2019)
`````````````````````

:blue:`What's New`

Major Features

 * Additional Pipeline settings

.. figure:: /sensiml-python-sdk/img/release-notes/model-building-additional-pipeline-settings.png
   :align: center
..

 * Ability to specify custom features for the feature family in the model building step

.. figure:: /sensiml-python-sdk/img/release-notes/model-building-custom-features.png
   :align: center
..

 * Added ability to use data files in the model explore widget

.. figure:: /sensiml-python-sdk/img/release-notes/explore-models-data-files.png
   :align: center
..


2019.3.2 (09/09/2019)
`````````````````````

:blue:`Bug Fixes`

 * Fixes issue with SML_Runner missing function

2019.3.1 (08/22/2019)
`````````````````````

:blue:`What's New`

Major Features

 * Additional plotting that shows the number of samples for each capture events along with the number of segments

.. figure:: /sensiml-python-sdk/img/release-notes/query-number-of-segments.png
   :align: center
..

 * Improvements to the Model Explore widget to allow selecting multiple capture files for model evaluation

.. figure:: /sensiml-python-sdk/img/release-notes/explore-models-multiple-captures.png
   :align: center
..

 * Addition of new model selection algorithms Metadata K-fold and Stratified Metadata K-fold to Model Creation Widget

.. figure:: /sensiml-python-sdk/img/release-notes/model-building-new-validation-algorithms.png
   :align: center
..

 * Minor visual improvements

2019.3.0 (07/30/2019)
`````````````````````

:blue:`What's New`

Major Features

 * Adds support for SensorTile 1.0 Knowledge Pack creation
 * Adds support for SensorTile Firmware 1.0 flashing
 * Overhaul of the Model Creation Widget, which now supports selecting an optimizing for a specific metric along with the Classifier Size in bytes

.. figure:: /sensiml-python-sdk/img/release-notes/model-building-widget.png
   :align: center
..

 * Addition of the Project Explorer to the Data Exploration Widget

.. figure:: /sensiml-python-sdk/img/release-notes/query-project-explorer.png
   :align: center
..


2019.2.0 (06/11/2019)
`````````````````````

:blue:`What's New`

Major Features

 * Adds support for choosing the validation method used in the auto sense pipeline
 * Adds support for balancing data as part of the AutoSense pipeline
 * Adds support for query by capture_uuid
 * Adds post processing to model explore widget for test data that uses a majority voting algorithm over the last N examples

Minor Features

 * Adds support for displaying the created date to projects, pipelines, Knowledge Packs and captures

:blue:`Bug Fixes`

 * Fixes issue where downloading a Knowledge Pack after running the autosense pipeline was resetting the settings

2019.1.4 (06/11/2019)
`````````````````````

:blue:`Bug Fixes`

 * Fixes issue with Analytics Studio version number display

2019.1.3 (06/04/2019)
`````````````````````

:blue:`What's New`

Minor Features

 * Adds status messages information to widget output as well as log output
 * Previous results for Auto Sense pipeline will now be displayed when logging into the dashboard if available
 * Sets the width of jupyter notebooks to 95% when import sensiml dashboard
 * Switch from project level to pipeline level for displaying Knowledge Packs in explore models and create knowledgepack tabs
 * All list functions now also display the uuid of the object (ie: list_captures, list_capture_configurations...)
 * Adds a model summary view to the model exploration tab

.. figure:: /sensiml-python-sdk/img/release-notes/explore-models-model-summary.png
   :align: center
..

2019.1.2 (05/16/2019)
`````````````````````

:blue:`What's New`

Model Exploration Widget

 * Enables viewing confusion matrix in UI
 * Enables viewing feature summary in UI
 * Enables testing a model with Test Data captured through the Data Studio

.. figure:: /sensiml-python-sdk/img/release-notes/explore-models-widget.png
   :align: center
..


2019.1.0 (05/05/2019)
`````````````````````

:blue:`What's New`

Minor Features

 * UI improvements to DashBoard widget
 * Additional documentation
 * Capture Configuration is selectable in the download widget

:blue:`Bug Fixes`

 * Removes Metadata from the query widget label field

2.5.6 (03/18/2019)
``````````````````

:blue:`Bug Fixes`

 * Locking down jupyter notebook to 5.7.5 until his issue is resolved with 5.7.6 https://github.com/jupyter/notebook/issues/4467

2.5.5 (03/14/2019)
``````````````````

:blue:`What's New`

Minor Features

 * UI improvements to DashBoard widget
 * Adds additional documentation

:blue:`Bug Fixes`

 * Disable jedi autocomplete in ipython as it is causing errors with autocompletion

2.5.4 (03/06/2019)
``````````````````

:blue:`Bug Fixes`

 * Latest version of nrfutil is causing install failure

2.5.3 (02/28/2019)
``````````````````

:blue:`What's New`

 * Compatibility with server release 2.5.1

2.5.2 (02/04/2019)
``````````````````

:blue:`Bug Fixes`

 * Improvements to DashBoard widget stability
 * SMLRunner bug fix for get_model
 * Fixed issue in DashBoard widget where user could accidentally queue multiple pipelines by clicking 'Optimize Knowledge Pack' multiple times

2.5.1 (01/15/2019)
``````````````````

:blue:`What's New`

 * Updates to Dashboard widget layout
 * SMLRunner improved state checking
 * Provides version compatibility checking against the SensiML Cloud server
 * Generating a Knowledge Pack now displays the local directory path

2.4.1 (10/31/2018)
``````````````````

:blue:`What's New`

 * Improvements to pipeline state tracking
 * Minor documentation updates

2.4.0 (10/24/2018)
``````````````````

:blue:`What's New`

 * Improvements to Download Widget

:blue:`Bug Fixes`

 * Adding some sanity checks to SMLRunner that prevent getting Knowledge Pack in a bad state

2.3.16 (10/17/2018)
```````````````````

:blue:`Bug Fixes`

 * Stability improvements to sml_runner

2.3.15 (10/09/2018)
```````````````````

:blue:`Bug Fixes`

 * Fixes bug where sml_runner would enter debug mode
 * Flash widget now finds zip files from downloads and unzips for Nordic thingy
 * Improved error reporting from server
 * Minor stability improvements
 * Fixes some python 2/3 compatibility issues

2.3.13 (09/10/2018)
```````````````````

:blue:`Bug Fixes`

 * Fixed bug in feature visualization that was causing incorrect number of plots to show in Python 3
 * Added DashBoard to top level sensiml import

2.3.0
`````

:blue:`What's New`

Major Features

 * SensiML Python SDK now supports python 3.4+ (pip install sensiml)
 * Adding SMLRunner for calling a Knowledge Pack c library

Minor Features

 * Pipeline status is returned during pipeline execution

Deprecation Warning

 * pipeline.set_input_data no longer allows passing of a dataframe, use this practice instead:

    .. code-block:: python

        client.upload_dataframe('file_name', df)
        client.set_input_data('file_name', data_columns=...)
    ..

    *NOTE: There are minor differences in syntax between python 2 and 3. The most obvious being print statements now require parentheses.  ie print(“message”) instead of print “message” cheat sheet for 2-3:* http://python-future.org/compatible_idioms.html


2.2.2
`````

:blue:`What's New`

Major Features

 * Adding ability to use the emulator for hierarchical models via recognize_signal
 * SensiML Python SDK can now be installed/updated through pip (pip install sensiml)

Minor Features

 * Adding ability to rehydrate a Knowledge Pack summary (this is only the part of the Knowledge Pack that is put on the device)
 * General stability improvements and bug fixes

2.2.1
`````

:blue:`What's New`

Minor Features

 * ModelVisualizationWidget improvements with support for Windows Test App and Feature Vectors DataFrame

2.2.0
`````

:blue:`What's New`

Major Features

 * SensiML Dashboard Widget

Minor Features

 * Visual improvements/bug fixes to all widgets
 * KP download now includes option to explicitly define source (Audio, Motion, Custom)

SensiML Labs (Experimental Features)

 * Model Visualization Widget for viewing feature values in real time (early concept)

:blue:`Bug Fixes`

 * Generating OTA file from Flash widget works without installing nRFgo Studio

2.1.3
`````

:blue:`What's New`

Major Features

 * Improvements to all widgets (Query, Download, Flash, AutoSense)
 * Creation of Dashboard widget

:blue:`Bug Fixes`

 * Flash widget now working on windows

2.1.2
`````

:blue:`What's New`

Major Features

 * Adds support for hierarchical models in Download Widget
 * Adds ability to upload project data from Data Studio Project

2.1.1
`````

:blue:`What's New`

Major Features

 * Added visualizations for comparing features as well as neuron/feature placement

Minor Features

 * Added ability to specify a capture file as the test data in recognize signal
 * Added ability to upload a dcl project from the client
 * Widget optimizations

2.1.0
`````

:blue:`What's New`

Major Features

 * Kbclient has been replaced by SensiML as the client for connecting to SensiML's Rest APIs

Minor Features

 * Label column is now part of the query
 * Widget improvements
 * Query statistics are now displayed when adding a query through the widget
 * statistics_segments() now detailed information for all segment in that query
 * statistics() now returns summary information for query

2.0.0
`````

:blue:`What's New`

Major Features

 * Widgets - KB Client now has some built in widgets for bring a GUI to some basic functions. Widgets have been created for Querying, Pipeline Automation, and Knowledge Pack Generation
