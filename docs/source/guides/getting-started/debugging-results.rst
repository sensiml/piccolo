.. meta::
   :title: Debugging Bad Results
   :description: How to debug bad results using the SensiML Toolkit


Debugging Bad Results
---------------------

The process of building a good model may involve some iterations of trial and error. If you are not getting good results in a model it's good to check the following things to improve your results.

* **Collect more data** - If you are working with a small dataset, it's likely you do not have enough data to find a good match. The Data Studio makes it easy to quickly iterate and improve your model by using Knowledge Pack results to re-train your dataset with new labels. See more about this feature in the :doc:`Data Studio Documentation <../../data-studio/testing-a-model-using-the-data-studio>`

* **Check your sensor placement** - Is your sensor oriented consistently throughout your training data? A bad sensor placement can cause very unpredictable results

* **Evaluate your labels are consistent and accurate** - Are your labels consistent throughout your project? Check spacing and start/end placement to verify you are labeling your events in a consistent way

* **Evaluate different algorithms, seeds, segmenters** - You may need to try out different parameters in the model building step above or move to the :doc:`SensiML Python SDK <../../../sensiml-python-sdk/overview>` to get better results if your events are more complex