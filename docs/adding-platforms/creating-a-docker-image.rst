.. meta::
   :title: Third-Party Integration - Creating a Docker Image
   :description: How to create a docker image

=======================
Creating a Docker Image
=======================

The following guide defines how to create your own docker image if your hardware platform uses a compiler that is not in the list of :doc:`Supported Compilers <compiler>`.

SensiML Base Images
~~~~~~~~~~~~~~~~~~~

In order to create a docker image, we have provided a number of base images at `<https://hub.docker.com/u/sensiml>`__.

The source code for these base images resides at `<https://github.com/sensiml/docker-base-images>`__

.. _supported_compiler_sdk:

Creating a Custom SDK Image From Supported Compiler
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In order to use a create a custom SDK image, you must first use a base image from the list of SensiML supported compilers.

In this example, we will be using Arm GCC. The base images for SensiML using Arm GCC are here: `<https://hub.docker.com/r/sensiml/arm_gcc_none_eabi_base/tags>`__.

**Specify Base Version**

The code below will allow you to specify any of the tagged versions of our Arm GCC compiler images.

.. code:: docker

   ARG BASE_VERSION
   FROM sensiml/arm_gcc_none_eabi_base:${BASE_VERSION}

.. note::  Here, ``BASE_VERSION`` will be “9.3.1”, “10.2.1”, etc. to match the output version of ``arm-none-eabi-gcc --version`` downloads provided on the `Arm Developer site <https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm>`__

.. _sdk_code_dockerfile:

**Add SDK Code to the Dockerfile**

After pulling in the base image, your platform SDK can be added to the image. If no context is given, our build scripts assume that the SDK has been copied into ``build``. This can be done in a few ways. If your SDK resides in an open repository, you can clone it directly.

.. code:: docker

   RUN git clone --depth 1 --recursive https://repo_address.git /build

If you need to have an archive copied over, it is suggested to use a tar file

.. code:: docker

   ADD sdk_tar.tar /build

Here is an example of how the `Quicklogic qorc-sdk <https://github.com/QuickLogic-Corp/qorc-sdk>`__ is pulled into a Docker image via ``git clone``

.. code:: docker

   FROM sensiml/base_image:latest
   LABEL Author="Justin Moore <justin.moore@sensiml.com>"
   LABEL Description="Image for building library/applications for Qorc-SDK"

   RUN git clone --depth 1 --recursive https://github.com/QuickLogic-Corp/qorc-sdk.git /build

   WORKDIR /build
   RUN bash -c "source envsetup.sh"

   #Keep environment setup on re-entry.
   ENTRYPOINT ["source", "/build/envsetup.sh"]

.. _custom_compiler_image:

Creating a Custom Compiler Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating a custom compiler image, we'll need to start with the ``sensiml/sensiml_base`` image.

The base image will provide you with an image that has the latest tools required by SensiML to build and communicate with our services:

.. code:: docker

   FROM sensiml/base_image:latest

Now, add your compiler toolchain. In this example, we'll show how the Arm GCC toolchain is installed within the SensiML base images, as well as pathing information.

.. code:: docker

   FROM sensiml/base_image:latest
   LABEL Author="J Developer <j.dev@company.com>"

   ARG ARM_GCC_DOWNLOAD_LINK="https://developer.arm.com/-/media/Files/downloads/gnu-rm/10-2020q4/gcc-arm-none-eabi-10-2020-q4-major-x86_64-linux.tar.bz2"
   ARG ARM_GCC_FOLDER_NAME="gcc-arm-none-eabi-10-2020-q4-major"
   ARG ARM_GCC_VERSION="10.2.1"

   LABEL Description="Image for building arm-gcc project using Arm-gcc $ARM_GCC_VERSION"
   RUN cd /usr/local && wget -qO- $ARM_GCC_DOWNLOAD_LINK | tar -xj

   ENV PATH="/usr/local/$ARM_GCC_FOLDER_NAME/bin:${PATH}"

Here, Arm GNU Embedded tools are downloaded for version 10.2.1 (2020-q4-major), and put in ``/usr/local``. This information is then added to the ``PATH``.

.. _custom_platform_image:

Creating a Custom Compiler & SDK Image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When creating an image with a custom compiler and device SDK to build both library and binary Knowledge Pack downloads, first follow the steps to create a :ref:`Custom Compiler Image<custom_compiler_image>`.

You can then :ref:`add your SDK code<sdk_code_dockerfile>` to the image.

Testing a Docker Image
~~~~~~~~~~~~~~~~~~~~~~

If your SDK has a knowledgepack example, you can build the docker image:

.. code:: bash

   docker build . -t my_sdk_testing

And then run the image interactively to test:

.. code:: bash

   docker run -it my_sdk_testing

From here you will be in the Docker container. You can navigate to where your application is built and run the steps required to build.

Finalizing your Image
~~~~~~~~~~~~~~~~~~~~~

Now it’s time to delete the knowledgepack folder from the Docker image. This ensures that any model built using the Docker image will be using the generate model/source code from SensiML servers. In the example below, we assume all Knowledge Pack source/libraries are stored in a ``knowledgepack`` folder:

.. code:: docker

   RUN find /build -type d -name "knowledgepack" -print0 | xargs -0 rm -R
