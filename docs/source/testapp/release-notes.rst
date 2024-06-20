.. meta::
   :title: SensiML TestApp - Release Notes
   :description: Release notes history for the SensiML TestApp

.. raw:: html

    <style> .blue {color:#2F5496; font-weight:bold; font-size:16px} </style>

.. role:: blue

=============
Release Notes
=============

Current Release
---------------

.. _testapp-release-2023-1-0:

2023.1.0 (10/04/2023)
`````````````````````

:blue:`What's New`

 * Updated the target Android SDK to the latest version *(Android 13 - v33)*
 * Increased the minimum Android version from *(Android 4.4 - v19)* to *(Android 5 - v21)*
 * Updated SaaS License Agreement to the latest version (v063021)
 * Removed deprecated permissions for loading photos on device storage

Past Releases
-------------

2019.2.0 (12/11/2019)
`````````````````````

:blue:`What's New`

 * Added the ability to show pictures for events

.. figure:: /testapp/img/testapp-classifications-with-images.png
   :align: center
..

 * Added Event Summary panel which shows the total classifications for a given event
 * Added the ability to set classification names manually without a model.json file

2019.1.0 (06/04/2019)
`````````````````````

:blue:`What's New`

 * Added a majority vote algorithm setting for determining classifications

2.3.1 (02/26/2019)
``````````````````

:blue:`What's New`

 * Added support for upcoming server release

2.3.0 (11/13/2018)
``````````````````

:blue:`What's New`

Major Features

 * Added the ability to save a model json string on the configuration screen. This allows for classification names and model names to be displayed in the TestApp
 * Added various new display settings to the configuration screen

2.2.0 (08/30/2018)
``````````````````

:blue:`What's New`

Major Features

 * Added new supported device - QuickAI

2.1.5
`````

:blue:`What's New`

Major Features

 * Added SensiML TestApp to the Google Play store

2.1.4
`````

:blue:`What's New`

Minor Features

 * Added ability to see model classifications. To show the model, enable ‘Show model names’ in the configuration screen

:blue:`Bug Fixes`

 * Class IDs now show as the correct reverse int values (100 now will show as 1)

2.1.3
`````

:blue:`What's New`

Minor Features

 * Made optimizations to BLE event listener

2.1.2
`````

:blue:`What's New`

Major Features

 * Sensi has been renamed to SensiML TestApp

Minor Features

 * Made optimizations to event detection history control

2.1.1
`````

:blue:`What's New`

Minor Features

 * Optimized BLE device scan

2.1.0
`````

:blue:`What's New`

Major Features

 * Created a new Android application that can connect to a Nordic Thingy and show live classification results from a knowledge pack