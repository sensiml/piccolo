.. meta::
   :title: API Methods - DataSegments
   :description: How to use the DataSegments API

DataSegments
============

A DataSegments object is a collection of DataSegment objects. Each DataSegment object encapsulates its raw sensor data along with metadata. The DataSegments API supports plotting, manipulating, and importing/exporting to a variety of formats including DataFrames, Audacity Labels or DCLI. 


Getting Segments from DCLProject
--------------------------------

You can get all the segments from captures in any DCLProject along with the sensor data (as long as the senor data has been downloaded) using the get_capture_segments API.

.. code-block:: python

    from sensiml.dclproj import DCLProject

    # Put the path to dclproj file for the project you would like to connect to
    dclproj_path = r'<path-to.dclproj>'

    dcl = DCLProject(path=dclproj_path)

    capture= "<capture-name>"
    gt_session = "<ground-truth-session-name>"

    gt_segs = dcl.get_capture_segments([capture], sessions=[gt_session])


Manipulating Segments
---------------------

There are a number of built in filters that you can use to clean up the results. You may need to build your own to post-process the dataset before computing the confusion matrix

* join_segments: Join neighboring segments  who are within a delta distance of each other
* filter_segments: Remove segments whose length is smaller than a min width
* merge_segments: Merge overlapping or near segments with the same label
* remove_overlap: Remove the overlap between two segments by shrinking the overlapping segments so they are neighboring segments

.. code-block:: python

    from sensiml.dclproj.visualizations import plot_segment_labels

    # merge overlapping segments and then filter them so only segments
    # that are greater than 4000 will be kept. Results are returned as DataFrame
    merged_filtered_segments = gt_segs.merge_segments().filter_segments(min_length=4000)

    data = dcl.get_capture(capture)

    # plot the resulting segments against the capture file
    plot_segments_labels(
        merged_filtered_segments,
        data=data,
        labels=gt_segs.label_values,
        title="Merged then filtered Segments",
    )

Computing Confusion Matrix
---------------------------

You can compute the confusion matrix between DataSegments from two sessions across the same capture using the confusion_matrix API


.. code-block:: python

    gt_segs = dcl.get_capture_segments([capture], sessions=[gt_session])
    pred_segs = dcl.get_capture_segments([capture], sessions=[pred_session])

    pred_segs.confusion_matrix(gt_segs)

Uploading Segments
------------------

You can also upload the segments in a DataSegments object using the upload API. We often use this in cases where want to modify segment label_values. In this example, we modify the predicted segments by updating the labels with the nearest overlapping label from the ground truth. Then we upload the updated label values.

.. code-block:: python

    gt_segs = dcl.get_capture_segments([capture], sessions=[gt_session])
    pred_segs = dcl.get_capture_segments([capture], sessions=[pred_session])

    pred_segs.nearest_label(gt_segs)

    pred_segs.upload(client, default='Unknown')

Exporting to DataFrame
``````````````````````

You can convert any DataSegments object into a DataFrame object using the to_dataframe API.

.. code-block:: python

    final_segs_df = merged_filtered_segments.to_dataframe()


Importing from DataFrame 
````````````````````````

In the previous section, we ended up with a DataFrame of segments, it is straight forward to convert that back into a DataSegments object.

.. code-block:: python

    from sensiml.dclproj import segment_list_to_datasegments

    final_segs = segment_list_to_datasegments(final_segs_df, dcl=dcl)


Exporting to DCLI Format
````````````````````````

You can convert any DataSegments object into a DCLI file so they can be imported into the Data Studio.

.. code-block:: python

    final_segs.to_dcli('final_segs.dcli')


Working with Audacity
---------------------


Another tool that is often used when working audio data is Audacity. We provide APIs to make it easy to import/export Audacity labels into DataSegment objects.

Exporting to Audacity
`````````````````````

You can export a DataSegments to Audacity labels using the to_audacity API. The to_audacity API creates multiple files with the naming convention file_{capture_name}_session_{session_name}.txt. These can be imported into Audacity directly going to File->Import->Labels in Audacity

.. code-block:: python

    gt_segs.to_audacity()


Importing Audacity labels
`````````````````````````

Audacity labels can also be loaded as DataSegment objects. The following example reloads the Audacity labels we just created. 

.. code-block:: python
    
    audacity_segs = audacity_to_datasegments(
        dcl,
        capture_name=capture,
        file_path="file_{capture_name}_session_{session_name}.txt".format(
            capture_name=capture, session_name=session
        ),
    )


Visualize Audacity labels
`````````````````````````

After loading the DataSegments object, you can continue to use them as if they were native dcl segments.


.. code-block:: python

    data = dcl.get_capture(capture)
    plot_segments_labels(audacity_segs, data=data,  title='Audacity labels')


.. image:: /sensiml-python-sdk/api-methods/img/audacity_labels.png
    :align: center



DataSegment API
---------------

.. automodule:: sensiml.dclproj.datasegments.DataSegment


DataSegments API
----------------

.. automodule:: sensiml.dclproj.datasegments.DataSegments
    :members: confusion_matrix, apply, upload, nearest_labels, filter_by_metadata, merge_label_values, merge_segments, filter_segments, remove_overlap, join_segments, to_dataframe, to_dcli, to_audacity, to_timeseries, label_values


DataSegments Loader API
-----------------------

.. automodule:: sensiml.dclproj.loaders
    :members: import_model_results, import_segment_list, import_audacity, import_timeseries

DataSegments Segmenter API
---------------------------

.. automodule:: sensiml.dclproj.segmentation
    :members: sliding_window  