# Arduino Knowledge Pack Example for Nano33 BLE Sense
Example application code for running a [SensiML Knowledge Pack](https://github.com/sensiml/nano33_knowledge_pack/) on Arduino boards, for the Nano33 BLE Sense

## Choosing the correct SensiML hardware platform

In order to run a Knowledge Pack, you must first have a model generated via [SensiML Analytics Studio](https://sensiml.com/products/analytics-studio/).

When downloading a model, you will need to select `Arduino Cortex M4 ARM GCC 8.2.1` from the target device.

This will give you the option to build a library configured properly for a Cortex-M4 based Arduino device.

## Running your downloaded model

Unzip the download to a location of your choosing. In the folder, you will find the following directories:

* knowledgepack/
  * application/
  * libsensiml/

Copy the files from `libsensiml` to lib/sensiml. It is **ok to overwrite these, but do not commit them in a pull request**. The files provided in this repository are for examples only.

Copy the files from `application` to src/
This should be `sml_recognition_run.cpp`, which will contain the necessary model running code to enable recognition on the device. 

Build/upload the firmware.

### Adjusting IMU Frequency

If you wish to run the IMU at a different frequency (default for data capture and this example is 119 Hz), modify the `ACCEL_GYRO_DEFAULT_ODR` in `include/sensor_config.h`
As the [Data Capture Lab](https://sensiml.com/products/data-capture-lab/) of the SensiML Toolkit does not actively configure the device, a capture configuration isn't generated when creating the model code.

## Viewing Model Output

For Serial output, simply connect to your Nano33 via any serial monitoring application. You should see an output similar to this:

``` json
{"ModelNumber":0,"Classification":2,"FeatureLength":33,"FeatureVector":["2","0","253","252","93","217","0","0","0","0","0","0","205","221","255","183","0","0","0","1","1","0","0","1","0","1","0","0","2","0","4","145","19"]}
```

## Using TensorFlow Lite for Microcontrollers in a Knowledge Pack
When running a model built using [TensorFlow Lite](https://www.tensorflow.org/lite) in a [SensiML Knowledge Pack](https://sensiml.com/tensorflow-lite/), another environment is provided in the code base.
The environment `env:nano33ble_with_tensorflow` will automatically link TensorFlow from a model download into the application
