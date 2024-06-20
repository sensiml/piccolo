.. meta::
   :title: Data Studio - Import Pre-Labeled Data
   :description: How to import pre-labeled data in the Data Studio

.. |br| raw:: html

   <br />

Importing Pre-Labeled Data with the DAI Format
----------------------------------------------

You can import pre-labeled sensor data from outside sources into the SensiML Toolkit. It is a very useful tool if you have created your own protocols/applications for collecting/labeling sensor data and wish to integrate your labeled data into the SensiML Toolkit.

.. note:: This tutorial will be showing how to define your labels. To find out more about the raw sensor data files that SensiML supports see the in the :doc:`importing-external-sensor-data` tutorial

You can write a script or application to convert your data into this format. This allows you to continue using your previous methods for collecting/labeling data while getting the benefits that the SensiML Toolkit provides.

.. note:: This guide assumes you are familiar with a few key terms from the :doc:`Getting Started Guide<../guides/getting-started/quick-start-project>`. We will be referring to Metadata, Sessions, and Segments from this guide. If you are not familiar with these terms, please read the guide above before getting started.


How to Import Metadata/Segments
```````````````````````````````

The Data Studio allows you to import metadata and segments via .DAI files (Data Annotation Interface files). We will define the DAI file format in the next section. For now, just note that in order to import your metadata and segments you can find the import feature inside the menu item File → Import from DAI…

.. image:: /data-studio/img/ds-import-from-dai.png
   :align: center
   :scale: 75%


DAI File Format
```````````````

The Data Studio allows you to import metadata and segments via .DAI files (Data Annotation Interface files).

1. Download a full working example here: :download:`Import Example <file/import-format.zip>`. We suggest you download and try this example out before building your own .dai files.

The DAI format is a JSON based format with JSON properties that the Data Studio will look for when importing your metadata/segments. Let’s take a look at a snippet taken from the example code:

.. code-block:: json

  [
      {
          "file_name": "Example_01.csv",
          "metadata": [
              {
                  "name": "Subject",
                  "value": "User001"
              },
              {
                  "name": "Size",
                  "value": "Medium"
              }
          ],
          "sessions": [
              {
                  "session_name": "Session 1",
                  "segments": [
                      {
                          "name": "Label",
                          "value": "Kick",
                          "start": 188,
                          "end": 1500
                      },
                      {
                          "name": "Label",
                          "value": "Pass",
                          "start": 2500,
                          "end": 3000
                      }
                  ]
              },
              {
                  "session_name": "Session 2",
                  "segments": [
                      {
                          "name": "Label",
                          "value": "Dribble",
                          "start": 101,
                          "end": 200
                      },
                      {
                          "name": "Label",
                          "value": "Kick",
                          "start": 400,
                          "end": 600
                      }
                  ]
              }
          ],
          "videos": [
              {
                  "video_path": "C:\\Users\\User\\Videos\\VideoFile.mp4"
              }
          ]
      }
  ]


JSON Object Definitions
```````````````````````

The DAI file is a list of file objects with various properties for importing metadata/segments. Listed below is a description of each property and how to use it. It is helpful to download the full example above to see how these definitions relate to a real example.


**File**

.. csv-table::
   :widths: 5,20

   file_name, (String) Name of the file to import. The Data Studio will look for the file in the same directory of the DAI file. If your project already has a file with the same name then the Data Studio will update the segments/metadata/videos of the existing file
   metadata, (List<Object>) Defined below
   sessions, (List<Object>) Defined below
   videos, (List<Object>) Defined below

**Metadata**

Metadata defines attributes about the file (Example: Subject, Size, etc)

.. csv-table::
   :widths: 5,20

   name, (String) Group name for your metadata |br| |br| Example: Subject | Size
   value, (String) Value associated with the file metadata |br| |br| Example: John | Small

**Sessions**

Sessions are used to group your segments together

.. csv-table::
   :widths: 5,20

   session_name, (String) Name of the session you want to associate with your segments
   segments, (List<Object>) Defined below

**Segments**

.. csv-table::
   :widths: 5,20

   name, (String) Group name for your segment labels |br| |br| Example: Label
   value, (String) Name of the event in the segment |br| |br| Example: Dribble | Kick | Pass
   start, (Integer) Start index location of where your segment is located within the file
   end, (Integer) End index location of where your segment is located within the file

**Videos**

.. csv-table::
   :widths: 5,20

   video_path, (String) The path to your video file. |br| |br| Video path can be defined as any of the following formats: Absolute | Relative path to the DAI file | Relative path to the current project. |br| |br| Example: C:\\\\\\\\Users\\\\\\\\User\\\\\\\\Videos\\\\\\\\VideoFile.mp4 |br| |br| The Data Studio will prompt you to select a format when you import your file.