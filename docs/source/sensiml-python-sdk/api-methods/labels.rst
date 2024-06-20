.. meta::
   :title: API Methods - Labels
   :description: How to use the Label API Method

Labels
======

    Labels are used to describe the events your application will be detecting. Each label will have a subset of label values that can be assigned to any segment of data that you are annotating. For example, you might create a label called "Activity" which has multiple Label Values such as Walking, Running, Sitting, Standing, etc. Projects can have multiple labels each having their own set of label values

Examples::

    from sensiml.datamanager.label import LabelSet
    from sensiml.datamanager.labelvalue import LabelValueSet

    # gets the set of labels associated with this project
    label_set = LabelSet(client._connection, client._project)


    # get the first label object
    label = label_set.labels[0]
    label.name

    # gets the set of label values associated with the label
    label_values_set = LabelValueSet(client._connection, client._project, label)

    print(label_values_set)


.. automodule:: sensiml.datamanager.label
    :members: Label, LabelSet

.. automodule:: sensiml.datamanager.labelvalue
    :members: LabelValue, LabelValueSet

