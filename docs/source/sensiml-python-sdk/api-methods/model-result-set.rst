.. meta::
   :title: SensiML Python SDK - ModelResultSet
   :description: How to use ModelResultSet in the SensiML Python SDK

ModelResultSet
==============

Model objects from a pipeline come back from the server organized into ModelResultSets and Configurations. A
ModelResultSet represents everything returned by the pipeline and a Configuration is a subset pertaining to a single
train-validate-optimize (TVO) configuration or combination. It is very common for a ModelResultSet to have a
configuration containing many models. See the tutorials for more information about models, their metrics, and
recognition capabilities.

.. automodule:: sensiml.datamanager.modelresults
    :members: ModelResultSet, Configuration, ModelMetrics
    :noindex: knowledpack

.. automodule:: sensiml.datamanager.confusion_matrix
    :members: ConfusionMatrix


