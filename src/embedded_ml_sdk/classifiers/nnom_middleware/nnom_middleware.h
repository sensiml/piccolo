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




#ifndef __NNOM_MIDDLEWARE_H__
#define __NNOM_MIDDLEWARE_H__

#include "nnom.h"
#include "weights.h"
#include "kbutils.h"

// FILL_NNOM_MAX_TMP_PARAMETERS
#define NNOM_UNINITIALIZED 255
#ifndef NNOM_MAX_NUMBER_REULTS
#define NNOM_MAX_NUMBER_REULTS 10
#endif
#ifndef NNOM_MAX_NUMBER_INPUTS
#define NNOM_MAX_NUMBER_INPUTS 10
#endif

#define ESTIMATOR_TYPE_CLASSIFICATION 0
#define ESTIMATOR_TYPE_REGRESSION 1
// clang-format off

#ifdef __cplusplus
extern "C"
{
#endif

typedef struct nnom_classifier_rows
{
    uint16_t num_inputs;
    uint8_t num_outputs;
    float threshold;
    uint8_t estimator_type;
    nnom_model_t* model;
} nnom_classifier_rows_t;


void nnom_init(nnom_classifier_rows_t *classifier_table, const uint8_t num_classifiers);
uint8_t nnom_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results);
void nnom_results_object(int32_t classifier_id, model_results_t *model_results);

#ifdef __cplusplus
}
#endif

// clang-format on

#endif //__NNOM_MIDDLEWARE_H__
