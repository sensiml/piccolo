.. meta::
   :title: Data Studio - Import External Sensor Data
   :description: How to import external sensor data in the Data Studio

Importing External Sensor Data
------------------------------

The Data Studio can import sensor data from any external source if it is in a CSV, WAV, or QLSM format.

DAI Format and Pre-Labeled Data
```````````````````````````````

If you labeled your data through an external source you can import your labels via the DAI format. Find out how to use the .dai format in the :doc:`Importing Pre-Labeled Data<dai-import-format>` tutorial

.. note:: If you want to import your sensor data without labels you can skip the Pre-Labeled Data tutorial.

CSV Format
``````````

If you are importing CSV files then your data should have a header row

.. figure:: /data-studio/img/csv-format.png
   :align: center


How to Import Sensor Data
`````````````````````````

1. Create a new project in the Data Studio

2. Click File → Import Files and select the files you wish to import

.. image:: /guides/getting-started/img/dcl-menu-import-files-2.png
   :align: center

3. Select the columns you wish to import (CSV only)

.. figure:: /data-studio/img/select-columns.png
   :align: center

.. note:: You should only import your sensor data columns into the file. If you have labels you wish to import, you can create a .dai file to import these labels. See more about this feature in the :doc:`Importing Pre-Labeled Data<dai-import-format>` tutorial

4. (Optional) Rename columns (CSV Only)

.. figure:: /data-studio/img/rename-columns.png
   :align: center

5. Click **Next**

.. figure:: /data-studio/img/dcl-import-settings.png
   :align: center

6. Select a sensor configuration to associate with your files and click **Next**

.. figure:: /data-studio/img/dcl-device-plugin-select-import.png
   :align: center

.. note:: If you did not use one of the built-in device plugins you can click **Skip** to setup a custom sensor configuration profile

7. Enter a name for your sensor configuration profile and click **Save**

.. figure:: /data-studio/img/dcl-import-save-sensor-configuration.png
   :align: center
