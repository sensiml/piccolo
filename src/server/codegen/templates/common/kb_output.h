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




#ifndef _KB_DEBUG_H_
#define _KB_DEBUG_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include "kb_typedefs.h"
#include "kb_defines.h"
#include "kb.h"

/**
* @brief Generates a string containing the model result information
*
* @param[in] model_index Model index to use
* @param[in] result result from most recent classification
* @param[in] pbuf char buffer to hold the string
* @param[in] feature_vector a bool, true to add feature vector information
* @param[in] fv_arr an arrary to store the feature vector results in
* @returns length of data put into pbuf
*/
int32_t kb_sprint_model_result(int32_t model_index, char *pbuf, bool segment_info, bool feature_vectors, bool output_tensor);

/**
* @brief Fills a string with a json of the model output tensor
*
* @param[in] model_index Model index to use
* @param[in] result result from most recent classification
* @param[in] pbuf char buffer to hold the string
* @returns length of data put into pbuf
*/
int32_t kb_sprint_model_output_tensor(int32_t model_index, char *pbuf);


/**
* @brief Prints the model class map to a char string
*
* @param[in] model_index Model index to use
*/
void kb_print_model_class_map(int32_t model_index, char *output);
#define sml_print_model_class_map kb_print_model_class_map

void kb_print_model_map();

int32_t kb_sprint_model_cycles(
int32_t model_index, char *pbuf, uint32_t *cycles);
int32_t kb_sprint_model_times(
int32_t model_index, char *pbuf, float *times);

#ifdef __cplusplus
}
#endif

#endif // _KB_DEBUG_H_
