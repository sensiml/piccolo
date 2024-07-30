
## Adding Processor(s)

If a new platform has a processor that’s not yet supported, begin by adding it to the kbserver/library/fixtures/processors.yml file. This file contains information for processors only. Here is an example processor definition:

```yaml
- fields:
    uuid: cfea1e5c-0145-42f2-9ec4-f2cd48112e07
    architecture: 1
    display_name: "EFR32MG12 (Mighty Gecko)"
    manufacturer: "Silicon Labs"
    compiler_cpu_flag: "-mcpu=cortex-m4"
    clock_speed_mhz: 40
    float_options:
      {
        "None": "-mfloat-abi=soft",
        "Soft FP": "-mfloat-abi=softfp -mfpu=fpv4-sp-d16",
        "Hard FP": "-mfloat-abi=hard -mfpu=fpv4-sp-d16",
      }
    profiling_enabled: true
  model: library.ProcessorDescription
Field
```

Usage/Description

* **uuid**: Unique identifier for processor, to be used in platform definitions
* **architecture**: ID of the architecture, see below.
* **display_name**: MFG display name for processor
* **manufacturer**: maker of the processor
* **compiler_cpu_flag**: flags (if any) passed to the compiler to specify CPU. If none, leave as empty string (““)
* **float_options**: floating point options (if any) to pass to the compiler
* **clock_speed_mhz**: clock speed, in MHZ, used in profiling to estimate time in classification. 
* **profiling_enabled**: Whether or not we can generate code for profiling data.


## Adding Architectures

If the processor architecture is not in kbserver/library/fixtures/architectures.yml, it will need to be added. Currently added architectures are:

| Architecture | NameID |
| ------------ | ------ |
| ARM          | 1      |
| x86/64       | 2      |
| RISC-V       | 3      |
| Tensilica    | 4      |
| AVR          | 5      |
| RISC-V       | 6      |
| PIC24        | 7      |
| PIC16/18     | 8      |
| dsPIC33      | 9      |
 


## Adding Compiler(s)

Compiler definitions are found in kbserver/library/fixtures/compilers.yml. These are used to specify specific versions of a compiler to be used. 

```yaml
- fields:
    uuid: 7c98c2fa-a819-40a0-98f8-a60cc04130db
    name: GNU Arm Embedded (none-eabi)
    compiler_version: 8.2.1
    supported_arch: 1
    docker_image_base: "358252950181.dkr.ecr.us-west-2.amazonaws.com/sml_armgcc_generic"
  model: library.CompilerDescription
Field
```

Description

* **uuid**: Unique identifier for the compiler, to be used in platform definitions
* **name**: Name to display in analytics studio
* **compiler_version**: specific version of the compiler being used
* **supported_arch**: supported architecture of the compiler (note: 1 arch per compiler definition)
* **docker_image_base**: Docker image base name to use for compiling libraries and source only. This will combine with the compiler_version field to specify a docker image to build a knowledge pack library from. 


## Add Platform Definitions

Platform definitions cant be found in the kbserver/library/fixtures/platforms_v2.yml file. This file contains a lot of information about what a platform is capable of. Here’s an example of what it in a platform description:


```yaml
- fields:
    uuid: cd8adff3-627e-4f71-8a97-0be994f978b4
    name: Microchip SAMD21 ML Eval Kit
    description: Build libraries for Microchip SAMD21 development board/addons.
    docker_image: "358252950181.dkr.ecr.us-west-2.amazonaws.com/sml_microchip_samd21"
    platform_versions: ["1.1"]
    processors: [97aff1ea-ae7e-4a31-a4da-9333b2bb13de]
    can_build_binary: true
    codegen_file_location: ["microchip", "samd21"]
    permissions: { "developer": true, "enterprise": true, "starter": true }
    supported_source_drivers: {}
    applications:
      {
        "SensiML AI Simple Stream":
          {
            "description": "Provides an application binary (or example code) that implements SensiML Simple Streaming interface for reporting Knowledge Pack results",
            "supported_outputs": [["Serial"]],
            "codegen_app_name": "ml_eval_app",
          },
      }
    codegen_parameters:
      {
        "codegen_class": "ARMGCCGenericCodeGenerator",
        "uses_simple_streaming": True,
        "uses_sensiml_interface": False,
        "app_environment":
          {
            "EXTRA_LIBS_DIR": "/build",
            "SML_KP_DIR": "/build/libsensiml",
            "SML_KP_OUTPUT_DIR": "/build/libsensiml/_build",
            "SML_APP_BUILD_DIR": "/build/firmware/samd21-iot-sensiml-template.X",
            "SML_APP_DIR": "/build/firmware/",
            "SML_APP_CONFIG_GEN_DIR": "/build/firmware/knowledgepack/knowledgepack_project",
            "SML_APP_CONFIG_FILE": "/build/firmware/knowledgepack/knowledgepack_project/app_config.h",
            "SML_APP_LIB_DIR": "/build/firmware/knowledgepack/sensiml/lib",
            "SML_APP_LIB_INC_DIR": "/build/firmware/knowledgepack/sensiml/inc",
            "SML_APP_OUTPUT_BIN_DIR": "/build/firmware/samd21-iot-sensiml-template.X/dist/",
          },
      }
    supported_compilers: [24308768-a59d-468b-b65f-cde6071ae7b2]
    hardware_accelerators: { "hardware_neurons": false }
    default_selections:
      {
        "processor": "97aff1ea-ae7e-4a31-a4da-9333b2bb13de",
        "compiler": "24308768-a59d-468b-b65f-cde6071ae7b2",
        "float": "None",
      }
  model: library.PlatformDescriptionVersion2
```

* **uuid**: Unique identifier for the platform
* **name**: Name for display of the platform in Analytics Studio
* **description**: Description for tooltip in analytics studio
* **docker_image**: Docker image to be used in binary creation, as well as library/source. This will override anything specified in the compiler! This is combined with any specified versions in platform_versions to build various releases of the same platform SDK.
* **platform_versions**: List of supported versions. REQUIRED if specifying docker_image above. 
* **processors**: List of supported processors
* **supported_compilers**: List of supported compilers/versions
* **codegen_file_location**: Relative location for any application/make files, etc. on the server. Relative to kbserver/codegen/templates/platforms
* **applications**: specifies application support for builds. Typically, this will just be the SensiML AI Simple Stream application. More description below
* **codegen_parameters**: Specific parameters for code generation and docker container environment variable overrides. More description below
* **hardware_accelerators**:specifies if this platform has any hardware accelerators. most platforms don’t. 
* **default_selections**: Specifies defaults to use for compiler, processor, and float options in the analytics studio ui

## Add Applications

Applications are a dictionary in the fixture, with keys being application name, and value being further parameters:

* **description**: Snippet describing what the application does
* **supported_outputs**: List of lists with various combinations of outputs. For example: [[“Serial”],[“BLE”][“Serial”,”BLE”]] will output Serial, BLE, or BOTH, respectively.
* **codegen_app_name**: Name of the application folder residing on the server.

 

## Codegen Parameters

Codegen parameters layout the name of the class to use in the server, as well as what an app_environment would look like for a docker container. As some docker containers built for multiple platforms, the environment variables will specify the actual files/paths to use in building a Knowledge Pack.

* **codegen_class**: Class name of the code generator on the server. Specific classes will contain generation specific to a particular platform, in most cases
* **uses_simple_streaming**: Indicates that the platform uses SensiML simple streaming interface. This should be true for new platforms going forward
* **app_environment**: specifies environment variables used by build scripts in docker containers

 

## Creating Docker Images

Most docker images are based off a version of ARM-gcc, etc. For platforms like AVR/PIC, they’re based off MicroChip’s XC8/16/32 compilers, and are a little more involved. The files for Docker image creation are all in  this repository: sensimldevteam/docker_files 

In the root folder, there’s a basic requirements.txt and a python script. This will require Python 3.6 or higher to use. This build script will build everything in a sub-directory.

Every sub-directory will have an arguments.json file. This is used to specify versions of compiler, download links, github projects, repository name, tag to use, etc. 

 

## C Code Location

C code is kept in a given platform folder located in kbserver/codegen/templates/platforms. Typically these are added by manufacturer/product line. There will be a libsensiml folder and an applications folder. There can also be some bash script files for configuring sensors.

Platform Specific codegen files
Applications
For all builds, we have an “application” folder with an application name. 

This will consist of a couple of files, namely the sml_recognition_run.c/cpp file that will contain the recognition run functions that a platform will call to pass data to a knowledge pack, and the header file that is used in the SML_APP_CONFIG_FILE environment configuration for a docker image. These files contain tags that allow for template filling done by the server. A README is provided for integration instructions in most platforms. 

Configuration and build scripts
config_sensor_files.sh is a script that is used to configure data in the SML_APP_CONFIG_FILE header file. This can set sample rate, enable/disable sensors, etc. This is platform specific and not able to be very generic. 

build_binary.sh is a script for binary-supported platforms that will copy files to their proper directories, and build a binary file of the example application to be returned to a user. 

Libsensiml directory
The libsensiml directory will contain 2-3 files:

Makefile - a mostly generic file that will contain the build for a library. platform specific items include the compiler (xc32-gcc vs arm-none-eabi-gcc, etc.), and paths to any vendor provided libraries/CMSIS, etc.

sml_profile_utils.h - file that contains register or timer usage definitions to get on-device profiling for knowledge packs. Mostly only supported on Cortex-M4 or other ARM that supports DWTCTRL registers. Optional, or can leave empty.

testdata.h - file with a template for filling in test data to run known labeled data on a device rather than use sensor data. 
