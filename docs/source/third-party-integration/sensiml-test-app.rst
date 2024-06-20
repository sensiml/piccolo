.. meta::
    :title: Third-Party Integration - SensiML TestApp
    :description: How to interface with the SensiML TestApp

====================================
Interfacing with the SensiML TestApp
====================================

The SensiML TestApp is an application that shows real-time event classifications from the SensiML Knowledge Pack (recognition firmware) running on your edge device over Bluetooth-LE.

SensiML TestApp
---------------

Instructions for implementing BLE GATT characteristics readable by the SensiML TestApp is in the :doc:`Reading SensiML BLE Characteristics Documentation<../../knowledge-packs/sensiml-ble-characteristics>`.

SensiML OpenApp Project
-----------------------

We also provide source code for an Android application called the SensiML OpenApp Project. The SensiML OpenApp Project reads SensiML BLE GATT characteristics similar to the SensiML TestApp, but by providing the source code you can customize the application to meet your business needs. Download the source code at `<https://bitbucket.org/sensimldevteam/sensiml_android_open_project/>`_