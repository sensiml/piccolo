==================
SensiML Python SDK
==================

The SensiML Python SDK provides a programmatic interface to SensiML REST API's for
building machine learning pipelines including data processing, feature
generation and classification for developing smart sensor algorithms optimized
to run on embedded devices.

Installation/Setup Instructions
===============================

1. The SensiML Python SDK requires **python version 3.7 or greater** to be installed on your computer.

2. We recommend running the SensiML Python SDK using Jupyter Notebook. Install Jupyter Notebook by opening a command prompt window on your computer and run the following command

    pip install jupyter

3. Next, to install the SensiML Python SDK open a command prompt window on your computer and run the following command

      pip install SensiML

This command will install the SensiML Python SDK and all of the required dependencies to your computer. 

Connect to SensiML Cloud
-------------------------

Once you have installed the software, you can connect to the server by running the following

    from sensiml import *

    client = SensiML()

Connecting to SensiML servers requires and account, you can register at https://sensiml.com

Documentation can be found here https://sensiml.com/documentation/

