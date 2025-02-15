The Analytics Studio has several useful tools for testing how your model will perform before flashing it to a device. By using the Analytics Studio you can run a model against on any files you have added to your project.
1. Select a model in the **Test Model** page
  
2. Select one or more of the capture files. Click the **Compute Accuracy** button to validate it against the test data. To generate the model results, the SensiML Cloud emulates the firmware model classifications on the selected sensor data. This provides a bit accurate view of the performance you will expect when deploying your model to an edge device.

3. Once the results are finished you can click the **Compute Summary** button to see how the confusion matrix performs across all files you just tested against. The ground truth for the confusion matrix is generated based on the labels that are created in the Data Studio. You can switch which **session** is used to compute the ground truth as well.

4. Click on the **Results icon** for one of your capture files. The results are summarized as actual prediction vs ground truth labels. In the **Classification Chart** (top) the Y-axis tells us the classification name and the X-axis tells us the sample number or time. Classifications are generated by the model at the interval you selected for windowing segmentation. Locations where the ground truth and classification do not match are marked by a red **X**. The **Feature Vector Heat Map** (bottom) visualizes the features that are generated by each segment prior to being fed into the classifier as a heat map. The values for features are always scaled to a single byte prior to classification.

[See Documentation](https://sensiml.com/documentation/analytics-studio/testing-a-model-using-the-analytics-studio.html)
