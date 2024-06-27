## Piccolo AI™

Piccolo AI is the open-source version of [SensiML Analytics Studio](https://sensiml.com/services/toolkit/analytics-studio/) intended for individual developers, researchers, and AI enthusiasts. For enterprise teams contact SensiML for a licensed enterprise version of the software.

The Piccolo AI project includes

* SensiML's ML Engine: The engine behind SensiML’s AutoML model building, sensor data management, model tracking, and embedded firmware generation 
* Embedded ML SDK: SensiML's Inferencing and DSP SDK designed for building and running DSP & ML pipelines on edge devices
* Analytic Studio UI: An Intuitive web interface for working with the SensiML ML Engine to build TinyML applications
* SensiML Python Client: Allows programmatic access to the REST API services through Jupyter Notebooks

Piccolo AI is currently optimized for the classification of time-series sensor data. Common use cases enabled by Piccolo AI include:

* Acoustic Event Detection
* Activity Recognition
* Gesture Detection
* Anomaly Detection
* Keyword Spotting
* Vibration Classification

To learn more about Piccolo AI features and capabilities, see the
[product page](https://sensiml.com/services/toolkit/analytics-studio/).

## Get Started

The simplest way to get started learning and using the features in Piccolo AI is to sign up for an account on SensiML's managed SaaS service at
[SensiML Free Trial](https://sensiml.com/plans/trial/).

If you prefer to install and manage Piccolo AI yourself, you can get
the latest version on [github](https://github.com/sensiml/piccolo).

## Run Piccolo AI Locally

To try out Piccolo AI on your machine, we recommend using Docker.

### Prerequisites 

1. Install and start docker and docker-compose - https://docs.docker.com/engine/

   * *Note: Windows users will need to use the wsl2 backend. Follow the instructions [here](https://docs.docker.com/desktop/wsl/)*
   * *Note: If using Docker Desktop go to **Preferences > Resources > Advanced** and set Memory to at least 12GB.*

2. Follow the [post-installation instructions](https://docker-docs.uclv.cu/engine/install/linux-postinstall/) as well to avoid having to run docker commands as sudo user 

3. Some functionality requires calling docker from within docker. To enable this, you will need to make the docker socket accessible to docker containers

   ```
   sudo chmod 666 /var/run/docker.sock
   ```

5. By default the repository does not include docker images to generate model/compiler code for devices. You must pull docker images for the compilers you want to use. See docker images:
  
   ```
   docker pull sensiml/sml_x86_generic:9.3.0-v1.0
   docker pull sensiml/sml_armgcc_generic:10.3.1-v1.0
   docker pull sensiml/sml_x86mingw_generic:9.3-v1.0
   docker pull sensiml/sensiml_tensorflow:0a4bec2a-v4.0
   ```

### Start Piccolo AI

1. Make sure docker is running by checking your system tray icons. If it is not running then open Docker Desktop application in Windows to start the docker background service.

2. Open a Ubuntu terminal through Windows Subsystem for Linux

3. Navigate to your piccolo directory

   ```
   cd /mnt/c/Users/my_user/Documents/Repos/piccolo
   ```

4. Run docker compose

   ```
   docker-compose up
   ```

   Note: You should have the latest version of the sensiml base docker image. If not, you can do a docker pull

   ```
   docker pull sensiml/base
   ```

**Login via the Piccolo UI**

Go to your browser at `http://localhost:8000` to log in to the UI. See the [Getting Started Guide](https://sensiml.com/documentation/guides/getting-started/overview.html) to get started. 

The default username and password is stored in the `src/server/datamanager/fixtures/default.yaml` file

   ```
   username: piccolo@sensiml.com
   password: TinyML4Life
   ```

## Data Studio

The Data Studio is SensiML's standalone Data Capture, Labeling, and Machine Learning Model testing application. It is a companion application to Piccolo AI, but it requires a [subscription](https://sensiml.com/plans/data-studio-edition/) to use with your local Piccolo AI. 


## Upgrades
Upgrades will need to check out the latest code and run database.intialize container script which will perform any migrations. You may also need to pull the newest sensiml/base docker image in some cases when the underlying packages have been changed.


## Documentation

Piccolo AI is the open-source version of SensiML Analytics Studio. As such, it's features and capabilities align with the majority of those found in SensiML's Analytics Studio for which documentation can be found
[here](https://sensiml.com/documentation/analytics-studio/index.html).

For more information about our documentation processes or to build them yourself, see the
[docs README](https://github.com/sensiml/piccolo/blob/main/docs/README.md).

## Contribute

We welcome contributions from the community. See our contribution guidelines, see [CONTRIBUTING.md](https://github.com/sensiml/piccolo/blob/main/CONTRIBUTING.md). 

## Developer Guides

Documentation for developers coming soon!

## Support 

* To report a bug or request a feature, create a
[GitHub Issue](https://github.com/sensiml/piccolo/issues/new/choose). Please
ensure someone else hasn't created an issue for the same topic.

* Need help using Piccolo AI? Reach out on the [forum](https://forum.sensiml.org/),
fellow community member or SensiML engineer will be happy to help you out.

