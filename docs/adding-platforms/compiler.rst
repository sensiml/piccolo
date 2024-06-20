.. meta::
  :title: Third-Party Integration - Compiler
  :description: How to define a compiler

========
Compiler
========

A compiler defines the toolchain your hardware platform will use. SensiML uses `Docker <https://www.docker.com/>`__ to run a build environment for your hardware platform. You can have multiple compilers for a single hardware platform.

Supported Compilers
```````````````````

+---------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Arm GCC                         | https://hub.docker.com/r/sensiml/arm_gcc_none_eabi_base/tags                                                                                                                                                        |
+---------------------------------+---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Supported compilers can be used to build the **library** version of a Knowledge Pack. See how to define a supported compiler below:

.. code:: yaml

  - fields:
      uuid: 00000000-0000-0000-0000-000000000000
      supported_compiler: "sensiml/arm_gcc_none_eabi_base"
      supported_compiler_version: 9.3.1

+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **uuid**                        | uuid4  | Unique UUID for your compiler. This will be referenced in the :doc:`Hardware Platform <hardware-platform>` YAML ``supported_compilers`` property                                                           |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_compiler**          | string | Repository path for SensiML docker image                                                                                                                                                                   |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_compiler_version**  | string | Version of SensiML docker image compiler                                                                                                                                                                   |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

Custom SDK with Supported Compiler
``````````````````````````````````

If your hardware platform has a custom SDK that uses a supported compiler to also build a **binary** version of a Knowledge Pack then you can provide the SDK repository path and version. See the :ref:`Creating a Custom SDK Image From Supported Compiler<supported_compiler_sdk>` documentation for how to create your own SDK


See how to define a custom SDK with a supported compiler below:


.. code:: yaml

  - fields:
      uuid: 00000000-0000-0000-0000-000000000000
      supported_compiler: "sensiml/arm_gcc_none_eabi_base"
      supported_compiler_version: 9.3.1
      custom_sdk_image: "sdk_repo/custom_image"
      custom_sdk_image_version: 1.0

+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **uuid**                        | uuid4  | Unique UUID for your compiler. This will be referenced in the :doc:`Hardware Platform <hardware-platform>` YAML ``supported_compilers`` property                                                           |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_compiler**          | string | Repository path for SensiML docker image                                                                                                                                                                   |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_compiler_version**  | string | Version of SensiML docker image compiler                                                                                                                                                                   |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **custom_sdk_image**            | string | Repository path for custom SDK image                                                                                                                                                                       |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **custom_sdk_image_version**    | string | Version of custom SDK image                                                                                                                                                                                |
+---------------------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+


Custom Compiler
```````````````

If your hardware platform uses a custom compiler to build a **library**, see the :ref:`Creating a Custom Compiler Image<custom_compiler_image>` documentation for how to create your own docker image. See how to define a custom compiler below:

.. code:: yaml

   - fields:
       uuid: 00000000-0000-0000-0000-000000000000
       name: Your Compiler Name
       compiler_version: 1.0
       supported_arch: 1
       docker_image_base: "repo/image_base"
     model: compiler


+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **uuid**              | uuid4  | Unique UUID for your compiler. This will be referenced in the :doc:`Hardware Platform <hardware-platform>` YAML ``supported_compilers`` property                                                           |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **name**              | string | Name for your compiler to be displayed in Analytics Studio                                                                                                                                                 |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **compiler_version**  | string | Version of your compiler                                                                                                                                                                                   |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_arch**    | int    | Architecture number supported by the compiler. For multiple architectures, add 1 compiler entry per architecture.                                                                                          |
|                       |        | See the :doc:`Architecture Documentation<architecture>` for a list of supported architectures                                                                                                              |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **docker_image_base** | string | Repository path for base docker image                                                                                                                                                                      |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. note:: If your ``docker_image_base`` does not have a public path you can send a Dockerfile for us to recreate the image


Custom Compiler with SDK
````````````````````````

If your hardware platform uses a custom compiler and SDK to build **binary** images, see the :ref:`Creating a Custom Comiler & SDK Image<custom_platform_image>` documentation for how to create your own docker image. See how to define a custom compiler below:

.. code:: yaml

   - fields:
       uuid: 00000000-0000-0000-0000-000000000000
       name: Your Compiler Name
       compiler_version: 1.0
       supported_arch: 1
     model: compiler


+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **uuid**              | uuid4  | Unique UUID for your compiler. This will be referenced in the :doc:`Hardware Platform <hardware-platform>` YAML ``supported_compilers`` property                                                           |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **name**              | string | Name for your compiler to be displayed in Analytics Studio                                                                                                                                                 |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **compiler_version**  | string | Version of your compiler                                                                                                                                                                                   |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| **supported_arch**    | int    | Architecture number supported by the compiler. For multiple architectures, add 1 compiler entry per architecture.                                                                                          |
|                       |        | See the :doc:`Architecture Documentation<architecture>` for a list of supported architectures                                                                                                              |
+-----------------------+--------+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

.. note:: If your ``docker_image_base`` does not have a public path you can send a Dockerfile for us to recreate the image

In addition to the compiler definition, we will need the ``custom_sdk_image`` and ``custom_sdk_image_version``:

.. code:: yaml

  - fields:
      custom_sdk_image: "sdk_repo/custom_image"
      custom_sdk_image_version: 1.0

+---------------------------------+--------+---------------------------------------------+
| **custom_sdk_image**            | string | Repository path for custom SDK image        |
+---------------------------------+--------+---------------------------------------------+
| **custom_sdk_image_version**    | string | Version of custom SDK image                 |
+---------------------------------+--------+---------------------------------------------+


