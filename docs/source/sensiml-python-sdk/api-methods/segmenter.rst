.. meta::
   :title: API Methods - Sessions
   :description: How to use the Session API Method

Sessions (Segmenters)
=====================

    A session separates your :doc:`segments` into a group. The session allows you to work on multiple branches of the same data set. In the server APIs the related session method is called **segmenter**. There are two types of sessions:
    
    1. Manual: Create segments by manually setting the start and end locations for each event
    2. Auto: Use a segmentation algorithm to automatically detect the start and end locations for each event

Examples::

    # gets the set of labels associated with this project
    client.project.list_segmenters()

.. automodule:: sensiml.datamanager.segmenter
    :members: Segmenter, SegmenterSet


