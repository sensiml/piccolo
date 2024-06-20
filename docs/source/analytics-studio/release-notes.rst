.. meta::
   :title: Analytics Studio - Release Notes
   :description: Release notes history for the Analytics Studio

.. raw:: html

    <style> .blue {color:#2F5496; font-weight:bold; font-size:16px} </style>

.. role:: blue

=============
Release Notes
=============

Current Release
---------------

.. _analytics-studio-release-2024-1-0:

2024.1.0 (02/15/2024)
`````````````````````

:blue:`What's New`

Minor Features

 * Added graph with distribution of step segments, samples, and feature vectors to the Pipeline Builder

   .. figure:: /analytics-studio/img/release-notes/v2024.1.0-cache.png
      :align: center

 * Updated the Model Summary graph to show Quantization Aware Training metrics

   .. figure:: /analytics-studio/img/release-notes/v2024.1.0-model-explorer.png
      :align: center

:blue:`Bug Fixes`

 * Fixed issue where the Pipeline Builder showed the Edit button for classifier and training algorithm steps when AutoML was enabled
 * Fixed issue where the Confusion Matrix was sometimes not rounding all numbers to two digits
 * Fixed issue where the Classifier latency did not load in the Download Model screen for custom models

Past Releases
-------------

.. _analytics-studio-release-2023-8-0:

2023.8.0 (12/19/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Added account settings page that allows managing account information, subscriptions, and API keys

   .. figure:: /analytics-studio/img/release-notes/v2023.8.0-account-page.png
      :align: center

 * Added functionality to download pipeline cache from the Pipeline Builder

   .. figure:: /analytics-studio/img/release-notes/v2023.8.0-pipeline-cahce-download.png
      :align: center

:blue:`Bug Fixes`

 * Fixed "Select All" checkbox in the Test Model screen

.. _analytics-studio-release-2023-7-0:

2023.7.0 (11/06/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Added audio player to the Data Manager screen

   .. figure:: /analytics-studio/img/release-notes/v2023.7.0-audio-player.png
      :align: center

 * Added buttons to download pipelines in JSON, Python, and Python notebook format

   .. figure:: /analytics-studio/img/release-notes/v2023.7.0-export-menu.png
      :align: center

 * Organized pipeline builder steps according to data processing task
 * Added building and cache statuses to the Pipeline Builder screen

 .. figure:: /analytics-studio/img/release-notes/v2023.7.0-pipeline-builder.png
      :align: center

Minor Features

 * Added autoscrolling to the result on the Test Model screen
 * Made Processor field searchable at the Download Model screen

:blue:`Bug Fixes`

 * Fixed incorrect default compiler
 * Fixed issue where Magnitude transform used incorrect sensor columns
 * Fixed incorrect label colors on the Prepare Data charts

.. _analytics-studio-release-2023-6-0:

2023.6.0 (09/21/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Added a Feature Embedding tab in the Model Explore page that enables data visualization for UMAP, PCA, and TSNE embedding methods

    .. figure:: /analytics-studio/img/release-notes/v2023.6.0-feature-embedding.png
      :align: center
 
 * Updated Feature Vector to provide segments and feature insights chart

   .. figure:: /analytics-studio/img/release-notes/v2023.6.0-feature-visualization-1.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2023.6.0-feature-visualization-2.png
      :align: center

 * Improved the pipeline builder to make it easier to use

   .. figure:: /analytics-studio/img/release-notes/v2023.6.0-pipeline-builder.png
      :align: center

 * Improved performance for Explore Model tab
 * Improved responsiveness for small-screen form factor

Minor Features

 * Improved Keyword Spotting template
 * Synced query filter with changing metadata field in query form
 * Improved validation warning for AutoML pipelines

:blue:`Bug Fixes`

 * Fixed bug where the "Created" date was wrong in the query table
 * Fixed bug where model information was not loading correctly after a pipeline was built
 * Fixed bug where invalid metadata could prevent editing of imported capture files

.. _analytics-studio-release-2023-5-1:

2023.5.1 (06/29/2023)
`````````````````````

:blue:`What's New`

Minor Features

 * Added item selection functionality to *Pipelines*, *Queries*, and *Models* tables

   .. figure:: /analytics-studio/img/release-notes/v2023.5.1-table-multiselect.png
      :align: center

:blue:`Bug Fixes`

 * Fixed bug where the capture table did not update after uploading files
 * Fixed bug with item selection in the Test Model screen table
 * Fixed bug where the projects table search bar did not work properly with paginated pages
 * Fixed bug where direct URL links did not work after logging in


.. _analytics-studio-release-2023-5-0:

2023.5.0 (06/14/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Updated Pipeline Settings in Pipeline Builder

   .. figure:: /analytics-studio/img/release-notes/v2023.5.0-pipeline-setting.png
      :align: center

 * Added new Training Summary with all AutoML models generated during the training process

   .. figure:: /analytics-studio/img/release-notes/v2023.5.0-pipeline-training-summary.png
      :align: center

 * Improved performance of loading the Data Manager *Capture Files* table

Minor Features

 * Added a session filter to Data Manager *Capture Files* table

   .. figure:: /analytics-studio/img/release-notes/v2023.5.0-session-filter.png
      :align: center

 * Added Pipeline actions buttons to the top panel

   .. figure:: /analytics-studio/img/release-notes/v2023.5.0-pipeline-btns.png
      :align: center

 * Improved Confusion Matrix

   .. figure:: /analytics-studio/img/release-notes/v2023.5.0-confusion-matrix.png
      :align: center

 * Improved workflow of changing projects

 * Removed *Hierarchical Model* option from AutoML settings

:blue:`Bug Fixes`

 * Fixed bug that caused Feature Visualization to not load properly after changing the active model
 * Fixed bug where min_max_scale was getting overwritten in the JSON tab
 * Fixed bug that could break the Data Manager chart width while rendering
 * Fixed bug with query screen label colors

.. _analytics-studio-release-2023-4-0:

2023.4.0 (05/08/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Upgraded UI and restyled various components

   .. figure:: /analytics-studio/img/release-notes/v2023.4.0-ui-updates.png
      :align: center

 * Added a new form for importing capture files with the ability to upload multiple files

   .. figure:: /analytics-studio/img/release-notes/v2023.4.0-multi-import.png
      :align: center

 * Improved Feature Generator form for better usability

   .. figure:: /analytics-studio/img/release-notes/v2023.4.0-fg.png
      :align: center

Minor Features

 * Improved Keyword Spotting template
 * Test Model's action buttons moved to the top

   .. figure:: /analytics-studio/img/release-notes/v2023.4.0-test-btn.png
      :align: center

 * Updated Confusion Matrix charts

   .. figure:: /analytics-studio/img/release-notes/v2023.4.0-confuasion-matrix.png
      :align: center

:blue:`Bug Fixes`

 * Fixed bugs where routers changing not loading at the top of the page

.. _analytics-studio-release-2023-3-0:

2023.3.0 (03/22/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Added Data Explorer screen and Queries table with features to create, edit,  delete, and build caches for queries

   .. figure:: /analytics-studio/img/release-notes/v2023.3.0-data-explorer.png
      :align: center

Minor Features

 * Updated Query Screen charts 

   .. figure:: /analytics-studio/img/release-notes/v2023.3.0-query-chart.png
      :align: center
   
 * Updated Select Target screen in the Download Model tab

   .. figure:: /analytics-studio/img/release-notes/v2023.3.0-download-platforms.png
      :align: center

 * Added a Change Platform button to the control panel in the Download Model tab

   .. figure:: /analytics-studio/img/release-notes/v2023.3.0-download-change-platform-btn.png
      :align: center

:blue:`Bug Fixes`

 * Fixed issue where the Confusion Matrix is not loading properly
 * Fixed issue in Pipeline Templates where sensor fields are not being set correctly

.. _analytics-studio-release-2023-2-0:

2023.2.0 (03/07/2023)
`````````````````````

:blue:`What's New`

Major Features

 * Added new tab called the Data Manager with features to upload, delete, download files, and manage file metadata

   .. figure:: /analytics-studio/img/release-notes/v2023.2.0-captures-explorer.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2023.2.0-captures-explorer-import.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2023.2.0-captures-explorer-metadata.png
      :align: center
      :scale: 50%

 * Added feature to open capture files in the Data Manager with options to add, update, and delete segments in the files

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-datamanager-chart.png
         :align: center

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-datamanager-table.png
         :align: center

 * Added Labels screen to the Project Settings with options to create, edit, and delete labels in a project

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-labels-screen.png
         :align: center

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-labels-screen-create.png
         :align: center
         :scale: 80%

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-labels-screen-edit.png
         :align: center
         :scale: 80%

 * Added Metadata screen to the Project Settings with options to create, edit, and delete metadata in a project

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-metadata-screen.png
         :align: center

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-metadata-screen-create.png
         :align: center

      .. figure:: /analytics-studio/img/release-notes/v2023.2.0-metadata-screen-edit.png
         :align: center

 * Added Vibration Classification, Activity Recognition, and Gesture Recognition templates to the Pipeline Builder

Minor Features

 * Added option to create a new Project
 * Improved performance of Model Explorer screen

:blue:`Bug Fixes`

 * Fixed a bug with rendering parameters correctly in the pipeline builder
 * Fixed a bug with showing server error messages

.. _analytics-studio-release-2023-1-0:

2023.1.0 (02/02/2023)
`````````````````````

Major Features

:blue:`What's New`

 * Added Keyword Spotting template to the Pipeline Builder

   .. figure:: /analytics-studio/img/release-notes/v2023.1.0-kw-template.png
      :align: center
      :scale: 50%

.. _analytics-studio-release-2022-4-2:

2022.4.2 (12/01/2022)
`````````````````````

Minor Features

:blue:`What's New`

 * Added a window about the usage of Account Credits

   .. figure:: /analytics-studio/img/release-notes/v2022.4.2-account-credits-header-menu.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2022.4.2-account-credits-window.png
      :align: center

 * Improved Explore Model view
 * Improved query caching


.. _analytics-studio-release-2022-4-1:

2022.4.1 (08/11/2022)
`````````````````````

Minor Features

:blue:`What's New`

 * Added better support for low resolution monitors
 * Updated the alert about unsaved pipeline changes

:blue:`Bug Fixes`

 * Fixed a bug with updating values for the input slider in the pipeline builder forms

.. _analytics-studio-release-2022-4-0:

2022.4.0 (07/26/2022)
`````````````````````

:blue:`What's New`

Major Features

 * Added JSON editor to the pipeline builder

    .. figure:: /analytics-studio/img/release-notes/v2022.4.0-pipeline-step-editor.png
      :align: center

Minor Features

 * Added a restart button to the result table in the pipeline builder screen

   .. figure:: /analytics-studio/img/release-notes/v2022.4.0-piprline-builder-optimize-btn.png
      :align: center

 * Added Feature Generator and Validation steps to AutoML pipeline and Classifier
 * Added Training Algorithm steps to the custom training pipeline in the pipeline builder

 *AutoML pipeline*

   .. figure:: /analytics-studio/img/release-notes/v2022.4.0-piprline-regular-view.png
      :align: center

 *Custom training pipeline*

   .. figure:: /analytics-studio/img/release-notes/v2022.4.0-piprline-regular-view-custom-pipeline.png
      :align: center

:blue:`Bug Fixes`

 * Fixed a bug with saving data at the array from field
 * Fixed classifier selection for creating a custom training pipeline
 * Fixed formatting pipeline data for pipeline builder screen

.. _analytics-studio-release-2022-3-1:

2022.3.1 (05/26/2022)
`````````````````````

:blue:`What's New`

Minor Features

 * Improved validation in the pipeline builder

.. _analytics-studio-release-2022-3-0:

2022.3.0 (05/19/2022)
`````````````````````

:blue:`What's New`

Major Features

 * Added audio classification pipeline template to the pipeline builder

    .. figure:: /analytics-studio/img/release-notes/v2022.3.0-pipeline-templates.png
      :align: center

 * Added new selection for compilers and development platforms in the download model screen

   .. figure:: /analytics-studio/img/release-notes/v2022.3.0-download-screen-selected.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2022.3.0-download-screen-information.png
      :align: center

Minor Features

 * Improved Profile Information loading in the download model screen
 * Improved logic for handling trying to open, delete, rename deleted models
 * Improved logic for loading model data

:blue:`Bug Fixes`

 * Fixed showing unnecessary warning alert in the pipeline builder screen
 * Fixed bugs where filtering labels were not matching with a query in the pipeline builder screen
 * Fixed classification chart bug with scaling in the explore model screen
 * Added sanitizing model names before sending to download
 * Fixed bug with parsing use_session_preprocessor param during import pipelines and pipeline templates

.. _analytics-studio-release-2022-2-0:

2022.2.0 (04/26/2022)
`````````````````````

:blue:`What's New`

Major Features

 * Added importing pipeline to the pipeline builder

    .. figure:: /analytics-studio/img/release-notes/v2022.2.0-import-btn.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2022.2.0-import-modal-first-page.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2022.2.0-import-modal-second-page.png
      :align: center

 * Added exporting pipeline to the pipeline builder

   .. figure:: /analytics-studio/img/release-notes/v2022.2.0-pipeline-export.png
      :align: center
   
   .. figure:: /analytics-studio/img/release-notes/v2022.2.0-pipeline-export-table.png
      :align: center

 * Added query selection to form for creating a new pipeline

   .. figure:: /analytics-studio/img/release-notes/v2022.2.0-create-modal-first-page.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2022.2.0-create-modal-second-page.png
      :align: center


Minor Features

 * Added HW Accelerator option to the download screen

     .. figure:: /analytics-studio/img/release-notes/v2022.2.0-download-pipeline-accelerator.png
      :align: center

 *	Added option to delete Knowledge Packs

     .. figure:: /analytics-studio/img/release-notes/v2022.2.0-model-table-delete.png
      :align: center
 
 *	Added an information alert to the pipeline builder

     .. figure:: /analytics-studio/img/release-notes/v2022.2.0-builder-warning-alert.png
      :align: center

 *	Added Loader with logs for creating and loading pipeline

 *	Added reload button to the captures table

:blue:`Bug Fixes`

 * Fixed filters at the captures table
 * Fixed incorrect sequence for loading pipelines

.. _analytics-studio-release-2022-1-1:

2022.1.1 (02/15/2022)
`````````````````````

:blue:`What's New`

Minor Features

 * Added reload button to Knowledge Pack table

     .. figure:: /analytics-studio/img/release-notes/v2022.2.0-reload-models.png
      :align: center

 * Added saving AutoML pipeline parameters

:blue:`Bug Fixes`

 * Fixed saving parameters at Feature Selector step
 * Fixed saving “Use Session Preprocessor” parameter at Input Query step

.. _analytics-studio-release-2022-1-0:

2022.1.0 (01/30/2022)
`````````````````````

:blue:`What's New`

Major Features

 * Added dictionary fields to the pipeline builder that covered parameters with dictionary types

    .. figure:: /analytics-studio/img/release-notes/v2022.1.0-feature-grouping.png
      :align: center

 * Added editable array field to the pipeline builder that allows adding custom values to parameters

    .. figure:: /analytics-studio/img/release-notes/v2022.1.0-custom-array-field.png
      :align: center

 * Added additional information to the model summary for PME and TensorFlow Lite for Microcontrollers classifiers 

    .. figure:: /analytics-studio/img/release-notes/v2022.1.0-model-summary-tf.png
      :align: center

    .. figure:: /analytics-studio/img/release-notes/v2022.1.0-model-summary.png
      :align: center

 * Added confusion matrix charts

    .. figure:: /analytics-studio/img/release-notes/v2022.1.0-confusion-matrix.png
      :align: center

Minor Features

 * Added information about CPU time usage to pipeline table

     .. figure:: /analytics-studio/img/release-notes/v2022.1.0-cpu-limit.png
      :align: center

 * Added status of running to pipeline table

     .. figure:: /analytics-studio/img/release-notes/v2022.1.0-running-status.png
      :align: center
 
 * Added default TVO steps to pipelines that don't have them

:blue:`Bug Fixes`

 * Fixed bug when changing classifier resets training algorithm step
 * Fixed order of feature selectors
 * Fixed indexing bug for adding and deleting pipeline steps
 * Fixed bug with editing feature generators with the same name

2021.5.0 (12/29/2021)
`````````````````````

:blue:`What's New`

Major Features

 * Added alerts about relevance and status of a query cache to the pipeline builder and query screen

    .. figure:: /analytics-studio/img/release-notes/v2021.5.0-out-of-cache-query-screen.png
      :align: center

    .. figure:: /analytics-studio/img/release-notes/v2021.5.0-not-built-query-pipeline-builder-screen.png
      :align: center

Minor Features

 * Added auto-updating status while building a new cache at the queries table

     .. figure:: /analytics-studio/img/release-notes/v2021.5.0-query-auto-uipdate-query-table.png
      :align: center

 * Added status of query cache to Input Query step at the pipeline builder screen

     .. figure:: /analytics-studio/img/release-notes/v2021.5.0-query-status-pipeline-builder-screen.png
      :align: center

 * Improved the code quality coverage

:blue:`Bug Fixes`

 * Fixed default Training Algorithm selection for TensorFlow Micro Classifier at the pipeline builder

2021.4.1 (12/08/2021)
```````````````````````

:blue:`What's New`

Minor Features

 * Optimized logic for the pipeline builder query step updating

:blue:`Bug Fixes`

 * Fixed issue in the pipeline builder where default pipeline has incorrect passthrough_columns

2021.4.0 (12/02/2021)
```````````````````````

:blue:`What's New`

Major Features

 * Added a project navigation panel and button to switch an active project

    .. figure:: /analytics-studio/img/release-notes/v2021.11.16-project-changing.png
      :align: center

 * Added a new pipeline selection screen and pipeline navigation panel

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-pipeline-selection.png
      :align: center

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-pipeline-changing.png
      :align: center
 
 * Added a new pipeline creation form with options to select machine learning algorithms

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-pipeline-form.png
      :align: center

 * Added Custom Training mode to Pipeline Builder 

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-custom-training.png
      :align: center

 * Added a new model selection screen and model navigation panel

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-model-selection.png
      :align: center
   
   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-model-changing.png
      :align: center

 * Added handlers for updating columns according Feature Transform and Sensor Transforms at Pipeline Builder
 * Added Device Profile Information to Download Model screen

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-device-profile-info.png
      :align: center

Minor Features

 * Improved the code quality coverage
 * Updated status of cache at Query Summary table

   .. figure:: /analytics-studio/img/release-notes/v2021.11.16-query-table.png
      :align: center

 * Updated table styles
 * Optimized performance for Pipeline Builder screen

:blue:`Bug Fixes`

 * Fixed initial loading pipeline data after login
 * Fixed loading data after change user account

2021.3.11 (10/07/2021)
``````````````````````

:blue:`What's New`
 
Minor Features

 * Adds support for rebulding the query cache in the Query Summary table
 * Adds additional column information such as Created Date and UUID to the Query, Pipeline and Knowledge Pack summary tables

2021.3.10 (10/05/2021)
``````````````````````

:blue:`What's New`
 
:blue:`Bug Fixes`

 * Fixed issue in the AutoML builder view where default parameters didn't contain SegmentID
 * Fixed login issue with redirecting to a source router  if user use direct router link and have to login first

2021.3.7 (09/27/2021)
`````````````````````

:blue:`What's New`

Minor Features

 * Optimized project summary screen
 * Performance and styles improvments
 * Show a warning message for incomplete pipelines in the AutoML builder

   .. figure:: /analytics-studio/img/release-notes/unsaved-modal-v2021.3.7.png
      :align: center

 * Added a warning message about unsaved data to AutoML builder

   .. figure:: /analytics-studio/img/release-notes/advanced-mode-v2021.3.7.png
     :align: center


:blue:`Bug Fixes`

* Fixed a bug in the Test Model screen where it could crash if some data was not yet loaded
* Fixed a bug where logging into multiple accounts simultaneously was not loading loading project information correctly

2021.3.1 (09/14/2021)
`````````````````````

:blue:`What's New`

Major Features

 * Adds a pipeline builder to construct DSP pipelines for AutoML model building

   .. figure:: /analytics-studio/img/release-notes/analytics-studio-model-building-v2021.3.1.png
     :align: center
     
   - **[1]** Pipelines can be created with different combinations of steps and parameters 
   - **[2]** The active pipeline can be changed on the selection list 

 * Advanced Pipleine Options

  - **[3]** Enables an advanced mode that allows adding more steps and parameters
  - **[5]** Each step may be editable (exclude Input Data and steps that have been extracted from a session) 
  - In addition to the default steps, additional steps can be added.
  - **[6]** Configure the AutoML hyperparameters for specific training algorithms, features, and classifier size limits.

Minor Features

* Added a button to load logs for Knowledge Pack files failed generation

   .. figure:: /analytics-studio/img/release-notes/analytics-studio-download-logs-v2021.3.1.png
     :align: center
 
:blue:`Bug Fixes`

 * Fixed logout bug at model building page
 * Fixed broken demo account flow
 * Fixed some performance and styles issues

2021.2.1 (08/19/2021)
`````````````````````

:blue:`What's New`

* Implemented application routers
* Updated styles for all pages
* Optimized logic for loading data

:blue:`Bug Fixes`

* Bug fixes at the store and api calls

2021.1.1 (08/05/2021)
`````````````````````

:blue:`What's New`

* Optimized loading data after a user has logged in
* Optimized refreshing for authorization auth token

:blue:`Bug Fixes`

* Minor bug fixes at the store
* Fixed some eslint errors

2021.1.0 (04/07/2021)
`````````````````````

:blue:`What's New`

* New Download Model screen with supporting new version of platforms and Knowledge Pack information

      .. figure:: /analytics-studio/img/release-notes/download-model-screen-v2.png
         :align: center

* New Project screen styles with last opened project

      .. figure:: /analytics-studio/img/release-notes/project-table-with-last-opened-project.png
         :align: center

* Added support for localization


:blue:`Bug Fixes`

* Minor bug fixes and security improvements
* Fixed the issue with changing Pipelines and Model when the project is changing
* Fixed behavior for expired auth token

2020.2.3 (01/11/2021)
`````````````````````
:blue:`What's New`

 * Adds a project description tab which includes project summary information as well as editable markdown field to describe your project.

      .. figure:: /analytics-studio/img/release-notes/analytics-studio-project-summary.png
         :align: center

 * Adds a number of Demos that can be accessed in read-only mode.

2020.2.2 (10/28/2020)
`````````````````````
:blue:`What's New`

 * The Advanced Settings tab has been moved to the bottom of the action buttons.

      .. figure:: /analytics-studio/img/release-notes/advanced-settings-moved-to-the-bottom-v2020.2.2.png
         :align: center

 * Enhanced Model Building Status Check to retry when a network issue occurs instead of returning a failure message.

:blue:`Bug Fixes`

 * Fixed an issue with the Query Filter in the Prepare Data view. If one of the metadata values is 0, the value was being removed from the query filter.
 * Fixed the Default Query Selection in the Build Model view for projects with a non-custom segmenter.
 * Fixed an issue where the magnitude column was duplicated when using Query Segments and Custom Feature Generator set.
 * Feature Threshold selection was not being persisted on the pipeline. This issue has been fixed.
 * The rename feature in the Knowledge Pack tab in the Project Summary view, renames the selected model’s name. In the case of a hierarchical model, all child model names needed to be prefixed with the parent model name. This issue has been fixed.
 * Fixed an issue with the Feature Vector Distribution Graph in the Explore Model View. The chart was not changing to the child model’s data when users switched to the child model tabs.
 * For hierarchical models, the parent model KP description details were not being posted back to the server with the Test Model run request. This issue has been fixed.



2020.2.1 (10/07/2020)
`````````````````````

:blue:`What's New`

 * Enhancements to the Model Explorer view

   * Added Pipeline Summary to the Explore Model Screen, showing the pipeline flow and step details.

      .. figure:: /analytics-studio/img/release-notes/pipeline-summary-v2020.2.1.png
         :align: center

   * Added Knowledge Pack Summary to the Explore Model Screen, showing the steps and step details used to generate the Knowledge Pack.

      .. figure:: /analytics-studio/img/release-notes/knowledgepack-summary-v2020.2.1.png
         :align: center

 * Added variance and correlation based feature thresholds to the advanced settings in the Model Building view.

      .. figure:: /analytics-studio/img/release-notes/feature-threshold-variance-correlation-v2020.2.1.png
         :align: center

 * Enhanced the Projects table by adding a segment count column. Starter Licenses are limited to 2500 segments per project. For Starter Licenses, the segments column will show a usage indicator of the number of segments used for the project.

      .. figure:: /analytics-studio/img/release-notes/starter-edition-segments-column-v2020.2.1.png
         :align: center

2020.2.0 (09/16/2020)
`````````````````````

:blue:`What's New`

 * Enhancements to the Project Summary view

   * Moved all summary tables into a single tab view and defaulted to displaying 10 rows per table.

   * Create and Modified Date columns are added to the Queries and Pipelines Summary tables.

   * Added a Knowledge Pack counts column to the Pipeline Summary table showing the number of Knowledge Packs for the pipeline.

   * Knowledge Pack summary table is enhanced to show Accuracy, Classifier, Model Size and Feature Counts.

   * Moved the "Refresh Summary" button to the bottom of the tab view.

   * Changed default sorting on the Query and Pipeline Summary tables to sort by the latest last modified date column and the Knowledge Pack summary table by the created date column.

   .. figure:: /analytics-studio/img/release-notes/project-summary-changes-v2020.2.0.png
      :align: center

 * Enhanced the Captures Files Table to show metadata data marked for lookup as drop-down filters.

   .. figure:: /analytics-studio/img/release-notes/capture_files_metadata_filters_v2020.2.0.png
      :align: center

 * Applied color gradient based on the ratio of value to support in the Confusion Matrix.

   .. figure:: /analytics-studio/img/release-notes/confusion-matrix-color-gradient-v2020.2.0.png
      :align: center

 * Title shows the Project Name on all screens except for the Home Screen.

:blue:`Bug Fixes`

 * Fixed issue in the Download Model view where the default Target OS selection for Cortex M4 was not correct.

2020.1.5 (08/19/2020)
`````````````````````

:blue:`What's New`

 * Enhanced Project and Capture Statistics tables with advanced filtering capabilities and type aware filter options (Date, Text, and Numeric Filters).

   .. figure:: /analytics-studio/img/release-notes/project_and_capture_statistics_table_filtering_enhancements.png
      :align: center

 * Added Feature Cascade, Strip Mean, and Magnitude Transforms to the Model Building View.

   .. figure:: /analytics-studio/img/release-notes/feature_cascade_strip_mean_and_magnitude_transforms.png
      :align: center

 * Added ability to select a Knowledge Pack Architecture in the Model Building View. You can select between a Single or Hierarchical Multi-Model or both.

   .. figure:: /analytics-studio/img/release-notes/single_and_hierarchical_multi_model_knoweldge_pack_architecture.png
      :align: center

 * Added an enhanced experience for Model Testing.

   * Test Model menu displays a new section for model testing.

   * You can now sort and filter, capture files on all capture attributes and metadata fields.

   * Multiple capture files can be selected to simultaneously run signal recognition.

   * Added a menu for selecting/unselecting all capture files.

   .. figure:: /analytics-studio/img/release-notes/select_all_and_unselect_all_capture_files.PNG
      :align: center

   * Enabled selection of any session and model on the project to run the capture files to run signal recognition and compute the accuracy.

   * Accuracy is displayed in the table after signal recognition.

   * Capture row is color highlighted to show if accuracy is above 80% (green) or below 80% (red) or grey (when no ground truth data is provided).

   * Added ability to compute a summary confusion report of selected capture files run's.

   .. figure:: /analytics-studio/img/release-notes/test_model_table_multi_select_and_accuracy_results.png
      :align: center

* Enhanced Model Test Results.

   * Classification Results are displayed when the results button is clicked.

   .. figure:: /analytics-studio/img/release-notes/enhanced_test_results_results_button.PNG
      :align: center

   * The results section consists of a confusion matrix, a classification chart showing the ground truth and predictions for the segments, and a feature vector heat map showing the feature values for a given feature and segment.

   * Enabled synchronous hover on the classification chart and feature vector heatmap, when hovered over the heat map the predicted event for the segment is displayed in the classification chart.

   .. figure:: /analytics-studio/img/release-notes/test_model_enhanced_reporting_of_results.png
      :align: center

* Enhanced Confusion Matrix.

   * Diagonal cells in the Matrix with data are highlight green and non-diagonal data cells are highlighted red.
   * UNC column has been removed from the table and Sense Perc will only be displayed when Support is greater than 0.
   * Accuracy will only be displayed when there is ground truth data.
   * All decimal values in the matrix are rounded to 2 decimals.


2020.1.4 (06/22/2020)
`````````````````````

:blue:`What's New`

 * Added visualizations to the Model Explore Screen.

   *Feature Vector Plots* added under the Feature Visualization Tab.

   .. figure:: /analytics-studio/img/release-notes/explore-feature-vector-charts.png
      :align: center

   *Feature Vector Distribution Plots* added under the Feature Summary Tab.

   .. figure:: /analytics-studio/img/release-notes/explore-feature-vector-distribution-charts.png
      :align: center

 * Added a button to the project list view to allow users to refresh the project list

   .. figure:: /analytics-studio/img/release-notes/projects-refresh-button.png
      :align: center

 * Enhanced the Confusion Matrix labels to highlight diagonal cells and total row/columns.

   .. figure:: /analytics-studio/img/release-notes/confusion-matrix-highlight-diagonals-totals.PNG
      :align: center

 * Enhanced the query creation flow to select all the sources by default when a new query is created.

 * Metadata selection list is now sorted alphabetically in the Data Exploration view.

2020.1.3 (05/20/2020)
`````````````````````

:blue:`What's New`

 * Added a 'Get Started' link to provide an overview of the tool to new users
 * Enhanced the Confusion Matrix to show row labels in as-is casing instead of all caps
 * Classification Chart now have all the labels for the query
 * Added a button to stop a classification run

2020.1.2 (05/04/2020)
`````````````````````

:blue:`What's New`

 * Added a 'delete' column to project list view with action buttons for project deletion
 * Breakup of the Status log error message by line breaks in the Model Building page
 * Enhancements to the Model Building view to enable persistence of the Build/Optimization settings for the pipeline

:blue:`Bug Fixes`

 * Fixed Issue with project statistics table, where it was not resizing when the Nav bar is collapsed
 * Fixed issue with Explore Model -Test Model - Charting and optimized server calls to eliminate extraneous sever requests across the application
