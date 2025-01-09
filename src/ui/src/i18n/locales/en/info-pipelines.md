
### Building a Model

The Model Building part of the Analytics Studio uses SensiML’s AutoML to build a model that gives you control of the features you want in your device. For example, if you build an algorithm that detects your events with 100% accuracy, the algorithm may use more resources. But by tweaking parameters in the AutoML settings you might find you can get an algorithm that uses half as many resources, while still getting 98% accuracy. You can configure SensiML’s AutoML process to maximize accuracy while fitting a within a desired memory constraint. This is a powerful concept that can save you a lot of time and money.

The model building process is represented as Pipelines. Each pipeline is a sequence of steps representing the process of data transformation during model building.

### Pipelines

A pipeline is a container for a series of data processing steps and contains the blueprint for how your model will be built. It contains the sensor data input parameters, transforms, feature generators, feature selectors, feature transforms and classifiers.

[See Documentation](https://sensiml.com/documentation/analytics-studio/building-a-model.html)
