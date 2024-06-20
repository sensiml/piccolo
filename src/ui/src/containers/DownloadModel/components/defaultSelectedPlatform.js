/*
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
*/

/* eslint-disable max-len */
export default {
  uuid: "e9f53dfa-f434-4f24-9577-839c190f74da",
  name: "ARM GCC Generic",
  hardware_accelerators: {
    cmsis_nn: {
      kernel: "cmsis_nn",
      description: "Use the ARM CMSIS library intrinsic functions to accelerate ops",
      display_name: "CMSIS",
    },
  },
  can_build_binary: false,
  supported_source_drivers: {},
  platform_versions: [],
  processors: [
    {
      architecture: "ARM",
      float_options: {
        None: "-mfloat-abi=soft",
        "Hard FP": "-mfloat-abi=hard -mfpu=fpv4-sp-d16",
        "Soft FP": "-mfloat-abi=softfp -mfpu=fpv4-sp-d16",
      },
      manufacturer: "ARM",
      display_name: "Cortex M4",
      profiling_enabled: true,
      uuid: "241a03d2-3e13-4087-9d7b-07a3f96e6dff",
    },
    {
      architecture: "ARM",
      float_options: {
        None: "-mfloat-abi=soft",
        "Hard FP": "-mfloat-abi=hard -mfpu=fpv5-sp-d16",
        "Soft FP": "-mfloat-abi=softfp -mfpu=fpv5-sp-d16",
      },
      manufacturer: "ARM",
      display_name: "Cortex M7",
      profiling_enabled: false,
      uuid: "530e1a45-22d3-429b-ae03-90b28040c54d",
    },
    {
      architecture: "ARM",
      float_options: {
        "Hard FP": "-mfloat-abi=hard -mfpu=crypto-neon-fp-armv8",
        "Soft FP": "-mfloat-abi=softfp -mfpu=crypto-neon-fp-armv8",
      },
      manufacturer: "ARM",
      display_name: "Cortex A53",
      profiling_enabled: false,
      uuid: "de848043-c284-4647-8364-7cc1a8582e68",
    },
    {
      architecture: "ARM",
      float_options: {
        None: "-mfloat-abi=soft",
      },
      manufacturer: "ARM",
      display_name: "Cortex M0+",
      profiling_enabled: false,
      uuid: "b003c819-90cc-4ec0-9c67-1986a74e90da",
    },
    {
      architecture: "ARM",
      float_options: {
        None: "-mfloat-abi=soft",
        "Hard FP": "-mfloat-abi=hard -mfpu=fpv5-sp-d16",
        "Soft FP": "-mfloat-abi=softfp -mfpu=fpv5-sp-d16",
      },
      manufacturer: "ARM",
      display_name: "Cortex M33",
      profiling_enabled: false,
      uuid: "a7aa7320-c6a3-4f00-a429-b300ff38613e",
    },
    {
      architecture: "ARM",
      float_options: {
        None: "-mfloat-abi=soft",
      },
      manufacturer: "ARM",
      display_name: "Cortex M0",
      profiling_enabled: false,
      uuid: "5192eb71-8831-474e-97b3-5f0a825303cb",
    },
    {
      architecture: "ARM",
      float_options: {
        None: "-mfloat-abi=soft",
      },
      manufacturer: "ARM",
      display_name: "Cortex M3",
      profiling_enabled: false,
      uuid: "3cc7739d-b218-4946-9366-3ab2293d42d6",
    },
  ],
  applications: {
    "AI Model Runner": {
      description: "An application that feeds sensor data into a SensiML Knowledge Pack model",
      codegen_app_name: "testdata_runner",
      supported_outputs: [["Serial"]],
    },
    "Arduino Model Runner": {
      description: "A SensiML model library that can be imported into an Arduino project",
      codegen_app_name: "arduino",
      supported_outputs: [["Serial"]],
    },
  },
  supported_compilers: [
    {
      name: "GNU Arm Embedded (none-eabi)",
      uuid: "2e8bdcf0-557a-41bd-a41d-64e443ec97a9",
      compiler_version: "10.3.1",
    },
  ],
  default_selections: {
    float: "Hard FP",
    compiler: "2e8bdcf0-557a-41bd-a41d-64e443ec97a9",
    processor: "241a03d2-3e13-4087-9d7b-07a3f96e6dff",
    hardware_accelerator: "cmsis_nn",
  },
  url: "http://dev.sensiml.cloud/platforms/v2/e9f53dfa-f434-4f24-9577-839c190f74da/",
  description: "Use the ARM-GCC compiler to build libraries for ARM Cortex-M/A devices.",
  documentation:
    "https://sensiml.com/documentation/firmware/arm-cortex-generic/cortex-arm-generic-platforms.html",
  platform_type: "compiler",
  manufacturer: "ARM",
};
