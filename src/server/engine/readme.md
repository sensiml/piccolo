Adding Classifier/Training Algorithm to SML Server


Adding a new classifier can be broken down into three parts.

Adding a model generator which uses a specific training algorithm (python or c)
Adding a classifier which reads a trained model and can recognize a vector (python or c)
creating optimized c code that can perform classifications on embedded devices and a compact model format that can be stored in SRAM


*** Model Generator ***

A model generator uses a classifier opject to train and store a model to the server. New training algorithms should be added to
engine.model_generators

* the training algorithm should subclass ModelGenerator object
* the training algorithm needs to be added to the model_generators.py as an available class
* the training algorithm needs to be added to mg_contracts with a description this will be shown on the client
* the training algorithm needs to also be added to functions_to_load.csv database so that it is loaded to the database
*

*** Classifier ***

Server

New classification algorithms should be added to the folder engine.classifier
engine.classifier.

* classifiers should subclass of the Classifier object
* the classifier needs to store its model in some internal format that can be stored as a json
* the classifier needs to be able to load and execute a recognize_vector using its internal stored representation
* the classifier must be added to the classifiers class so it can be retrieved
* the classifier needs to be added to mg_contracts with a description this will be shown on the client
* the classifier needs to also be added to functions_to_load.csv database so that it is loaded to the database
* the classifier needs to have a fucntion to compute its costs
* Recognition Engine needs to initialize the classifier in its initalize_classifier function


Codegen

* the c implementation should be split into two parts the classifier that runs a model and the stored model parameters
* the c implementation of the classifier should be stored in codgen.templates.classifiers
* the c implementatino of the trained model should be stored in codegen.templates.trained_models
* codegen will have to be updated to recognize the classifier and add it (this should be abstracted to a higher level probably)
* If you are using arm_dsp libraries from CMSIS include the files that are actually used in an arm_dsp folder within the classifier 
    (these will be used to compile for x86 as well as to help keep track of what is used)

ModelExploreWidget

 * add method for parsing the model summary for the new classifier





