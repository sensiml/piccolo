.. meta::
   :title: SensiML Python SDK - Pipelines
   :description: How to use Pipelines in the SensiML Python SDK

Pipelines
=========

A pipeline is a container for a series of data processing steps. The pipeline object allows you to
get an existing pipeline or create a new one with a given name. With this object, you can set input data sources, add
transforms, feature generators, feature selectors, feature transforms and classifiers. An example pipeline is shown below.

Examples::

    client.pipeline = 'my_pipeline'

    client.pipeline.set_input_query('ExampleQuery')

    client.pipeline.add_transform('Windowing')

    # Feature Generation
    client.pipeline.add_feature_generator(
        [
            {'subtype_call':'Time', 'params':{'sample_rate':100}},
            {'subtype_call':'Rate of Change'},
            {'subtype_call':'Statistical'},
            {'subtype_call':'Energy'},
            {'subtype_call':'Amplitude', 'params':{'smoothing_factor':9}}
        ],
            function_defaults={'columns':sensor_columns},
        )

    # Scale to 8 bit representation for classification
    client.pipeline.add_transform('Min Max Scale')

    # Perform Feature Selection to remove highly correlated features, features
     with high variance and finally recursive feature eliminate.
    # (Note: Recursive feature elimination can be very slow for large data sets and large number of parameters,
    #        it is recommended to use other feature selection algorithms to first reduce the number of features)

    client.pipeline.add_feature_selector(
        [
            {"name": "Correlation Threshold","params":{'threshold':0.85}},
            {"name": "Variance Threshold",
                                "params":{
                                    'threshold':0.05
                                        }
            },
            {"name":"Recursive Feature Elimination",
                                "params":{
                                        "method":"Log R",
                                        "number_of_features":20
                                        }
            },
        ],
            params = {"number_of_features":20}
        )

    client.pipeline.set_validation_method('Stratified K-Fold Cross-Validation',
                                            params={'number_of_folds':3})

    client.pipeline.set_classifier('PME',
                params={'classification_mode':'RBF',
                        'distance_mode':'L1'
                        })

    client.pipeline.set_training_algorithm('Hierarchical Clustering with Neuron Optimization',
                        params = {'number_of_neurons':10})

    client.pipeline.set_tvo({'validation_seed':0})

    results, stats = client.pipeline.execute()

The final step is where the pipeline is sent to the SensiML Cloud Engine for execution, once the job is completed the results will be returned
to you as a model object if classification has occurred, or a DataFrame if you are at an intermediary step.

    client.pipeline.execute()

.. automodule:: sensiml.pipeline
    :members: Pipeline



