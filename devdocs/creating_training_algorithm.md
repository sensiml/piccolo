# Creating a New Training Algorithm

Training algorithms are implemented as a subclass of the ModelGenerator class. A model generator takes a dataset, classifier object,  validation object, along with parameters as inputs then trains a model and stores a model to thee database along with some performance metrics. New training algorithms should be added to library.model_generators

To add a new training algorithm

1. Add thetraining algorithm as a class to the file library.model_generators.<training-algorithm-name>.py which subclasses the ModelGenerator object

2. The training algorithm needs to be added to the model_generators.py as an available class

3. Add the training algorithm input contract and documentation to mg_contracts with a description that will be shown on the client

4. Add the training algorithm to functions_to_load.csv database so that it is loaded to the database
