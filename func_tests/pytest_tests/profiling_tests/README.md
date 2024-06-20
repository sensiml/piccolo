# Running profiling

## Setup

Currently, the only device supported is the Nano33 BLE Sense. More platforms/cpus will come.

Clone the [Nano33 Knowledge Pack repo](https://github.com/sensiml/nano33_knowledge_pack).

Ensure you have platformIO cli installed:

`pip install platformio`

Plug the Nano33 in to your computer, and get the com port. Default on Linux is `/dev/ttyACM0`, but always good to check if there are multiple things plugged in.

## Running

Run the profiling test like any other pytest test. You will need to pass in the location you cloned the Nano33 repository to (`--sdk_dir`), as well as the port and baud rate for uploading firmware/reading results.

``` bash
cd func_tests/pytest_tests
py.test profiling_tests/test_profiling_on_device.py --rlocal=True --server=localhost2 --device_port=/dev/ttyACM0 --device_baud=115200 --sdk_dir=Nano33_repo_dir
```

# Do no run this with threads.
