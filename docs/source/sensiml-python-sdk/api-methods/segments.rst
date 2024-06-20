.. meta::
   :title: API Methods - Segments
   :description: How to use the Segment API Method

Segments
========

Segments are how we define an event location in the SensiML Toolkit. They contain the start and end location of the event and the :doc:`Label <labels>` for the event


Examples::

    from sensiml.datamanager.label_relationship import Segment, SegmentSet

    # to see a list of segments associated with a capture
    segment_set = SegmentSet(client._connection, client._project, capture)
    print(segment_set.segments)

    # To create a new segment
    segment = Segment(client._connection, project, capture, segmenter, label, label_value)
    segment.sample_start = 100
    segment.sample_end = 1000
    segment.insert()

.. automodule:: sensiml.datamanager.label_relationship
    :members: Segment, SegmentSet