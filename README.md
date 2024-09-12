![Piccolo AI Banner Image](https://sensiml.org/wp-content/uploads/2024/07/piccolo_github_banner.png)
## About Piccolo AI<sup>™</sup>

Piccolo AI is the open-source version of [SensiML Analytics Studio](https://sensiml.com/services/toolkit/analytics-studio/), a software development toolkit for constructing sensor-based AI inference models optimzed to run on low-power microcontrollers and IoT edge platforms (ex. x86 embedded PCs, RPi, arm Cortex-A mobile processors).  Piccolo AI is intended for individual developers, researchers, and AI enthusiasts and made available under the AGPLv3 license.

The Piccolo AI project includes:

* **SensiML's ML Engine**: The engine behind SensiML’s AutoML model building, sensor data management, model tracking, and embedded firmware generation 
* **Embedded ML SDK**: SensiML's Inferencing and DSP SDK designed for building and running DSP & ML pipelines on edge devices
* **Analytic Studio UI**: An Intuitive web interface for working with the SensiML ML Engine to build TinyML applications
* **SensiML Python Client**: Allows programmatic access to the REST API services through Jupyter Notebooks

### Use Cases and Application Examples
Piccolo AI is currently optimized for the classification of **time-series** sensor data. Common use cases enabled by Piccolo AI include:

| Application | | Example Use Cases | Piccolo AI Reference Application(s) |
| ----------- | --- | ----------------- | ------------------------------ |
| **Acoustic<br>Event Detection** | ![Window Breakage Event](/assets/images/acoustic-event-detection.png) | Intrusion Detection<br>Machinery / Appliance Monitoring<br>Public Safety (ex. gunshot recogition)<br>Vehicle Diagnostics<br>Livestock Monitoring<br>Worker Safety (ex. leak detection) | [Pump State Recognition Demo](https://forum.sensiml.org/t/microphone-based-state-and-fault-detection-for-fluid-pumps/258/1)<br>[Smart Lock Demo](https://forum.sensiml.org/t/building-a-smart-lock-application-using-an-audio-sensor/50/1) |
| **Activity<br>Recognition** | ![Gait Analysis](/assets/images/activity-recognition.png) | Human Gait Analysis<br>Ergonomic Assessment<br>Sport/Fitness Tracking<br>Elder Care Monitoring | [Boxing Punch Classification Demo](https://forum.sensiml.org/t/boxing-punch-activity-recognition/260) |
| **Gesture<br>Detection** | ![Gesture Recognition](/assets/images/gesture-recognition.png)| Touchless Machine Interfaces<br>Smarthome Control<br>Gaming Interfaces<br>Driver Monitoring<br>Interactive Retail Displays | [Wizard Wand Demo](https://forum.sensiml.org/t/wizard-magic-wand-gesture-game/76/1) |
| **Anomaly<br>Detection** | ![Anomaly Detection](/assets/images/anomaly-detection.png) | Factory/Plant Process Control<br>Predictive Maintenance<br>Robotics<br>Remote Monitoring | [Robotic Arm Anomaly Detection](https://forum.sensiml.org/t/robot-arm-motion-recognition-and-anomaly-detection/256/1) |
| **Keyword<br>Spotting** | ![Voice Recognition](/assets/images/voice-recognition.png) | Consumer Electronics UI<br>Security (ex. Voice Authentication)<br>HMI Command/Control | Keyword Spotting Demo<br>([Part 1](https://forum.sensiml.org/t/keyword-spotting-part-i-data-collection-and-data-annotation/86/1),[Part 2](https://forum.sensiml.org/t/keyword-spotting-part-ii-building-a-keyword-spotting-model/87/1)) |
| **Vibration<br>Classification** | ![Machine State Detection](/assets/images/vibration-monitoring.png) | Predictive Maintenance<br>Vehicle Monitoring<br>Supply Chain Monitoring<br>Machine State Detection | [Smart Drill Demo](https://forum.sensiml.org/t/smart-cordless-power-drill-detecting-fastener-driving-states/72/1)<br>[Fan State Demo](https://forum.sensiml.org/t/imu-based-predictive-maintenance-fans-motors/254) |

Piccolo AI is not limited to only the applications listed above.  Virtually any time-series sensor input(s) can be used to classify application-specific events of interest.  Piccolo AI also provides support for regression models as well as basic feature transform outputs without classification. To learn more about Piccolo AI features and capabilities, see the
[product page](https://sensiml.com/services/toolkit/analytics-studio/).

## Get Started

The simplest way to get started learning and using the features in Piccolo AI is to sign up for an account on SensiML's managed SaaS service at [SensiML Free Trial](https://sensiml.com/plans/trial/).

If you prefer to install and manage Piccolo AI yourself, you can get the latest version on [GitHub](https://github.com/sensiml/piccolo).

## Run Piccolo AI Locally

To try out Piccolo AI on your machine, we recommend using Docker.

### Prerequisites 

1. Install and start docker and docker-compose - https://docs.docker.com/engine/

   * *Note: Windows users will need to use the wsl2 backend. Follow the instructions [here](https://learn.microsoft.com/en-us/windows/wsl/install)*
   * *Note: If using Docker Desktop go to **Preferences > Resources > Advanced** and set Memory to at least 12GB.*

2. Follow the [post-installation instructions](https://docker-docs.uclv.cu/engine/install/linux-postinstall/) as well to avoid having to run docker commands as sudo user 

3. Some functionality requires calling docker from within docker. To enable this, you will need to make the docker socket accessible to docker containers

   ```
   sudo chmod 666 /var/run/docker.sock
   ```

5. By default the repository does not include docker images to generate model/compiler code for devices. You'll need to pull docker images for the compilers you want to use. See docker images:
  
   ```
   docker pull sensiml/sml_x86_generic:9.3.0-v1.0
   docker pull sensiml/sml_armgcc_generic:10.3.1-v1.0
   docker pull sensiml/sml_x86mingw_generic:9.3-v1.0
   docker pull sensiml/sensiml_tensorflow:0a4bec2a-v4.0
   ```
   
6. Make sure you have the latest sensiml base docker image version. If not, you can do a docker pull

   ```
   docker pull sensiml/base
   ```

### Start Piccolo AI

1. Make sure docker is running by checking your system tray icons. If it is not running then open Docker Desktop application in Windows to start the docker background service.

2. Open a Ubuntu terminal through Windows Subsystem for Linux

   ```
   git clone https://github.com/sensiml/piccolo
   cd piccolo
   ```

3. Use [docker compose](https://docs.docker.com/compose/) to start the services

   ```
   docker compose up
   ```

**Login via the Web UI Interface**

Go to your browser at `http://localhost:8000` to log in to the UI. See the [Getting Started Guide](https://sensiml.com/documentation/guides/getting-started/overview.html) to get started. 

The default username and password is stored in the `src/server/datamanager/fixtures/default.yaml` file

   ```
   username: piccolo@sensiml.com
   password: TinyML4Life
   ```

### Step-by-Step Install Video

To help you get up and running quickly, you may also find our video installation guide useful.  Click on the video below for a complete walkthrough for getting Piccolo AI installed on a Windows 10 / 11 PC:


<a href="https://sensiml.wistia.com/medias/lzyxvqlr9k?wvideo=lzyxvqlr9k"><img src="https://embed-ssl.wistia.com/deliveries/37d2cc5387147b921cb1c4b444244f53.jpg?image_crop_resized=900x506&image_play_button=true&image_play_button_size=2x&image_play_button_color=2949E5e0" alt="Piccolo AI Installation Video" width="450" height="253" /></a>

## Data Studio

The Data Studio is SensiML's standalone Data Capture, Labeling, and Machine Learning Model testing application. It is a companion application to Piccolo AI, but it requires a [subscription](https://sensiml.com/plans/data-studio-edition/) to use with your local Piccolo AI. 


## Upgrades
Upgrades will need to check out the latest code and run database.intialize container script which will perform any migrations. You may also need to pull the newest sensiml/base docker image in some cases when the underlying packages have been changed.


## Documentation

Piccolo AI is the open-source version of SensiML ML Engine. As such, it's features and capabilities align with the majority of those found in SensiML's ML Engine for which documentation can be found
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

## Last but Not Least, a Special Thank You to Our Supporters!
[![Stargazers repo roster for @sensiml/piccolo](https://reporoster.com/stars/sensiml/piccolo)](https://github.com/sensiml/piccolo/stargazers)
