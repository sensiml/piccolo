.. meta::
   :title: Quick Start Project
   :description: How to use the quick start project in the SensiML Toolkit

Quick Start Project
-------------------

In this guide we are going to walk through a *Hello World* example project which we refer to as the **Slide Demo**. The goal of this demo is to familiarize you with the SensiML Toolkit workflow.

**Optional: Download Dataset**

We provide a full dataset for this tutorial that you can use to follow along.

  * :download:`Example Dataset </guides/getting-started/file/slide-demo.zip>`

Events
``````

The **Slide Demo** has three continuous states. This demo is used to simulate a motor motion. To make this demo more accessible we make these motions with our hand, but in the real world you would attach your sensor to a motor.

  Events of interest:

  • **Stationary** - Board is resting on a desk surface
  • **Horizontal** - Board is slid back and forth (**left to right** or **forward to back**) on a flat surface in a repetitive rhythmic motion to simulate a part moving back and forth

  .. figure:: /guides/getting-started/img/sensor-tile-horizontal.png
     :align: center

     *Horizontal orientation*

  • **Vertical** - Board is lifted in an **up and down** motion in the air in repetitive rhythmic motion to simulate a part being lifted up and down

  .. figure:: /guides/getting-started/img/sensor-tile-vertical.png
     :align: center

     *Vertical orientation*
