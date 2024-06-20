.. meta::
   :title: API Methods - CSV Upload
   :description: How to use the CSV Upload API Method

CSV Upload
==========

In some cases, you may already have a CSV file that you want to use. This can be raw sensor data with labels or 
features that you have cached. We separate this into DataFiles and Featurefiles which we explain below.

**DataFiles**

A DataFile allows you to upload sensor data into a pipeline for testing, rather than using Project Capture data. Files must
be in CSV format. Using datafile is convenient when:

   1. You have test data that you want to test against a model without adding the file to your Project Capture list.


Examples::

    client.list_datafiles()
    
    # if you want to upload directly from a csv file, force=True overwrites the file on the server if it exists.
    client.upload_data_file(name, path, force=True) 

    # if you already have a dataframe
    client.upload_dataframe(name, dataframe)


**FeatureFiles**

A featurefile can be used to directly load data into a pipeline, rather than querying Project Capture data. Files must
be in CSV format. Using featurefiles is convenient when:

   1. You want to cache features locally and then use those as input into the training algorithm so you can avoid running
      previous steps in the pipeline.


Examples::

    client.list_featurefiles()

    # if you want to upload directly from a csv file
    client.upload_feature_file(name, path) 

    # if you already have a dataframe
    client.upload_dataframe(name, dataframe)


.. automodule:: sensiml.datamanager.featurefiles
    :members: FeatureFiles

.. automodule:: sensiml.datamanager.featurefile
    :members: FeatureFile
