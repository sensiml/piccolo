# Creating a new Classifier

Adding a new classifier can be broken down into three parts.

1. Adding python version of the classifier that reads a trained model and inferences using the c code

2. Creating optimized c code that can perform classifications on embedded devices and a compact model format that can be stored in SRAM

3. Update codgen to find the classifier and generate the parameters for it from the JSON Serialized  model parameters

## Adding a Python Classifier

* New classification algorithms should be added to the folder library.classifier
* New classifiers should subclass the Classifier class in library.classifier.classifier
* The classifier needs to store its model parameters in a JSON serializable format
* The classifier needs to be able to load the JSON serialized model parameters and run the model inference  by loading the compiled c library of the classifier. This happens inside the recognize_vectors function
* Add the classifier to the Classifiers class in  library.classifier.classifiers so it can be retrieved 
* Add the classifier to mg_contracts with a description (this will be shown on the client)
* Add the classifier in to functions_to_load.csv so it is loaded to the database
* RecognitionEngine class in engine.recognition_engine needs to initialize the classifier in its initalize_classifier function

 

## Creating the C code for inference

* The c implementation should be split into two parts the classifier that runs a model and the stored model parameters
* Create a <classifier_name>.c and <classifier_name>.h file in the codgen.templates.classifiers.<classifier_name> folder
* Create a Makefile in the codegen.templates.classifiers.<classifier_name> that generates a linkable .so version of the classifier
* Create the c and h files for the trained model template codegen.templates.trained_models.<classifier_name>

 

## Model Code Generation

* Add codegen/model_gen/<classifier_name>.py, use code_gen/model_gen/.py decision_tree_ensemble.py as a template
* Update codegen/model_gen/model_gen.py to include the new classifier helper functions
* Update the codegen/knowledgepack_codegen_mixin.py file to include the calls to the classifier. See examples for the other classifiers for which functions to update (ie get_classifier_type_map)
