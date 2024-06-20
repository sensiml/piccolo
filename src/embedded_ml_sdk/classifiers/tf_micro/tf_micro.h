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




#ifndef __TF_MICRO_H__
#define __TF_MICRO_H__

#include "micro_api.h"
#include "kbutils.h"

// FILL_TF_MICRO_MAX_TMP_PARAMETERS
#define TF_MICRO_UNINITIALIZED 255
#ifndef TF_MICRO_MAX_NUMBER_REULTS
#define TF_MICRO_MAX_NUMBER_REULTS 10
#endif
#ifndef TF_MICRO_MAX_NUMBER_INPUTS
#define TF_MICRO_MAX_NUMBER_INPUTS 10
#endif

#define ESTIMATOR_TYPE_CLASSIFICATION 0
#define ESTIMATOR_TYPE_REGRESSION 1
// clang-format off

#ifdef __cplusplus
extern "C"
{
#endif

typedef struct tf_micro_classifier_rows
{
    uint16_t num_inputs;
    uint8_t num_outputs;
    const uint8_t *model_data;
    float threshold;
    int32_t kTensorArenaSize;
    uint8_t *tensor_arena;
    float scale_factor;
    int32_t zero_bias;
    uint8_t estimator_type;
} tf_micro_classifier_rows_t;


void tf_micro_init(tf_micro_classifier_rows_t *classifier_table, const uint8_t num_classifiers);
uint8_t tf_micro_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results);
void tf_micro_model_results_object(int32_t classifier_id, model_results_t *model_results);

#ifdef __cplusplus
}
#endif

// clang-format on

#endif //__TF_MICRO_H__
