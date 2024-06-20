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




#ifndef __LINEAR_REGRESSION_H__
#define __LINEAR_REGRESSION_H__

// clang-format off
#ifdef __cplusplus
extern "C"
{
#endif

#include "kbutils.h"

typedef struct linear_regression_model
{
    float_t *coefficients;
    int32_t num_coefficients;
    float_t intercept;
} linear_regression_model_t;




typedef struct linear_regression_model_rows
{
    linear_regression_model_t *model;
} linear_regression_model_rows_t;


float linear_regression_model_predict(linear_regression_model_t *model, float *feature_vector);
float linear_regression_predict(uint8_t model_id, float *feature_vector);
void linear_regression_model_results_object(int32_t model_id, model_results_t *model_results);
int linear_regression_simple_submit(uint8_t model_index, feature_vector_t *feature_vector, model_results_t *model_results);
void linear_regression_init(linear_regression_model_rows_t *model_table, const uint8_t num_classifiers);

#ifdef __cplusplus
}
#endif

// clang-format on

#endif // __LINEAR_REGRESSION_H__
