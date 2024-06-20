.. meta::
   :title: API Methods - Queries
   :description: How to use the Query API Method

Queries
=======

In most cases, the first step to building an experiment or sandbox pipeline is to design a query. The query API is a powerful tool that selects the data you want to use to train your model. See the tutorial in :doc:`../getting-started-with-the-sensiml-python-sdk` for a practical introduction to queries.


Queries can be created in the Analytics Studio UI and also programmatically using the create query API.

Examples::

    client.create_query('my_query', columns = ['AccelX', 'AccelY', 'AccelZ'],
                                 metadata_columns = ['Subject'],
                                 label_columns=['Label']
                                 metadata_filter = '[Subject] IN [User001, User002]',
                                 force = True)

    client.pipeline.set_input_query('my_query')


Managing the query cache

.. code-block:: python

   # list the queries in the current project
   client.list_queries()

   # get a query that you have already created
   q = client.get_query("<query-name>")

   # check if there is a cache and how many partitions there are
   print(q.cache)

   # update the cache for the query from the latest information in the project    
   q.cache_query()

   # check the status of the query 
   q.cache_query_status()

   # stop the current query cache operation
   q.cache_query_stop()


.. automodule:: sensiml.datamanager.queries
    :members: Queries

.. automodule:: sensiml.datamanager.query
    :members: Query

