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




#ifndef TENSORFLOW_LITE_MICRO_C_API_H_
#define TENSORFLOW_LITE_MICRO_C_API_H_

#include <stdint.h>
    
void tf_micro_model_setup(const void *model_data, unsigned char *tensor_arena, int32_t kTensorArenaSize);

void tf_micro_model_invoke(float *input_data, int32_t num_inputs, float *results, int32_t num_outputs, float scale_factor, int32_t zero_bias);

#endif //TENSORFLOW_LITE_MICRO_C_API_H_