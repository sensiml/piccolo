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

#ifndef __SML_RECOGNITION_RUN_H__
#define __SML_RECOGNITION_RUN_H__

#ifdef __cplusplus
extern "C"
{
#endif

int32_t get_last_segment_length();
int32_t get_last_result_model();
int32_t get_last_result_class();
int32_t get_last_feature_bank_number();
extern int32_t get_feature_vector_size(int model_index);
extern int32_t copy_output_tensor(float *output_tensor);
extern int32_t copy_feature_vector_float(int model_index, float *feature_vector);
extern int32_t get_output_tensor_size();
extern void sml_output_results(int32_t model, int32_t classification);
extern int32_t sml_recognition_run(signed short *data, int32_t num_sensors);
extern int32_t sml_recognition_run(signed short *data, int32_t num_sensors);


#ifdef __cplusplus
}
#endif
#endif //__SML_RECOGNITION_RUN_H__
