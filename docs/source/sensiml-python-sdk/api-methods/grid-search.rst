.. meta::
   :title: SensiML Python SDK - Grid Search
   :description: How to use Grid Search in SensiML Python SDK

Grid Search
===========

Optimizing model performance often requires searching over a large parameter space. SensiML analytics engine also supports
grid search over pipeline parameters. After you have created a pipeline you can specify  which parameters to search over.
On the server side we take advantage of the pipelines ability to parallelize, as well as performing  optimizations for training
algorithms to speed up the computation. This makes it possible to search large parameter spaces quickly and efficiently.
After performing the grid search we rank each pipeline based on the f1 score, precision and sensitivity so that you can
choose the best performing combination to build a Knowledge Pack with.

Grid Search Syntax
------------------

After you have created a pipeline, you can call ``client.pipeline.grid_search()`` and pass in a list of grid_params to search over.

Grid params is a nested python dictionary object.

.. code-block:: python

    grid_params = {"Name Of Function":{"Name of Parameter":[ A, B, C]}}

``A, B, and C`` are the parameters to search over. Additionally, for each step you may want to search over more
than one of a functions configurable parameters. To do this simply add another element to the functions dictionary.

.. code-block:: python

    grid_params = {"Name Of Function":{"Name of Parameter 1":[ A, B, C],
                                          "Name of Parameter 2":[ D, E]}
                                      }

This will tell grid search to search over 6 different parameter spaces.

You can also specify more than one step to search over in grid params. This is done through simply
adding another element to the Function level of the grid_params dictionary.

.. code-block:: python

    grid_params = {"Name Of Function":{"Name of Parameter 1":[ A, B, C],
                                    "Name of Parameter 2":[ D, E]},
                   "Name of Function 2":{"Name of Parameter":[1, 2, 3, 4, 5, 6]}}

To access the grid parameter space, use the name of the training algorithm as shown in the example below to iterate over
the parameter space of the pipeline described in the Pipelines section of this documentation.

.. code-block:: python

    grid_params = {'Windowing': {"window_size": [25,50,75,100,125], 'delta':[100]},
                  'selector_set': {"Recursive Feature Elimination": {'number_of_features':[5,10,20]}},
                  'Hierarchical Clustering with Neuron Optimization': {'number_of_neurons':[5,10,]}
                }

    results, stats = client.pipeline.grid_search(grid_params)
