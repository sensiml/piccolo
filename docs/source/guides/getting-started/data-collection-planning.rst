.. meta::
   :title: Data Collection Planning
   :description: Data collection planning with the SensiML Toolkit

Data Collection Planning
------------------------

Before you build an application, it is important to create a data collection plan. This involves determining what sort of **metadata** you are going to capture as well as what **type of events** you are detecting.

We recommend when starting a new application that you first collect a small amount of training data and validate your results in a proof of concept. Once you have validated your initial training set, collect a larger amount of data using what you've learned during the initial proof of concept.

.. figure:: /guides/getting-started/img/data-collection-planning.png
   :align: center


Determining your metadata
`````````````````````````

Metadata are custom properties that you can save to the files you capture that allow you to filter your sensor data based on characteristics of the files. Metadata properties are normally attributes about the subject or object you are recording.
This is a very important feature. Let's go over a couple examples of when this is useful:

1. If you are building a motor fault detection application, you can save the motor size of the motor you are recording. When you start to build a machine learning algorithm you might find out that you need two models to get accurate results: a small motor model and a large motor model. Since you saved the motor size as metadata you can easily split the models.

2. You could save the subject ID or motor ID as metadata. The subject ID would allow you to ignore certain subjects if you find that their data was not recorded correctly or maybe one subject/object is an extreme outlier from the rest of your data.

Determining events of interest
``````````````````````````````

Events of interest are ultimately the main goal of your application. These are the events you want your sensor 
application to be detecting.

Once you can determine your events of interest you can capture them and train a SensiML **Knowledge Pack** with
a machine learning algorithm for detecting those events.

Events tend to fall into one of two types:
**continuous** events or **discrete** events.

**Continuous "Status" Events**

* Continuous events are events that happen over longer, gradual intervals or periods of time. Think of them like you are looking for the current status of the device. An example of this includes a motor fault detection sensor. In this example the sensor will detect a continuous “Normal” status or in a continuous “Failure” status. In a fitness wearable you may be looking for the user’s activity status (Running, Walking, Resting).

**Discrete "Trigger" Events**

* Discrete events are events that have discrete trigger actions that the application needs to be trained for. An example of this includes a karate wearable sensor. In this example the sensor will detect the trigger events of “Karate Kick” or “Karate Chop”. Looking at the fitness wearable application, instead of the continuous status “is running” we may look at each footstep in the run as a trigger event.

**Why is this important?**

The type event you are trying to detect will change the way you want to train your raw sensor data in the SensiML toolkit. We will go into this concept in more detail in :doc:`labeling-your-data`

