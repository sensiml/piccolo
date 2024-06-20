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

/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include <stdint.h>

#ifndef TENSORFLOW_LITE_MICRO_EXAMPLES_MODEL_RUNNER_MICRO_API_H_
#define TENSORFLOW_LITE_MICRO_EXAMPLES_MODEL_RUNNER_MICRO_API_H_

// Expose a C friendly interface for main functions.
#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>

// Initializes all data needed for the example. The name is important, and needs
// to be setup() for Arduino compatibility.
int32_t micro_model_setup(const void* model_data, int32_t kTensorArenaSize,
                      unsigned char* tensor_arena);

// Runs one iteration of data gathering and inference. This should be called
// repeatedly from the application code. The name needs to be loop() for Arduino
// compatibility.
int32_t micro_model_invoke(unsigned char *input_data, int32_t num_inputs, float *results,
                       int32_t num_outputs, float scale_factor, int32_t zero_bias);

#ifdef __cplusplus
}
#endif

#endif  // TENSORFLOW_LITE_MICRO_EXAMPLES_MODEL_RUNNER_MICRO_API_H_
