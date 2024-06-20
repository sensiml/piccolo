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



#include "linear_regression.h"

linear_regression_model_rows_t *ModelTable;

// FILL_MAX_LINEAR_REGRESSION_TMP_PARAMETERS

float linear_regression_model_predict(linear_regression_model_t *model, float *feature_vector)
{
    float result = 0;
    for (int i = 0; i < model->num_coefficients; i++)
    {
        result += model->coefficients[i] * feature_vector[i];
    }

    return result + model->intercept;
}

float linear_regression_predict(uint8_t model_index, float *feature_vector)
{
    float result = 0;
    for (int i = 0; i < ModelTable[model_index].model->num_coefficients; i++)
    {
        result += ModelTable[model_index].model->coefficients[i] * feature_vector[i];
    }

    return result + ModelTable[model_index].model->intercept;
}

int linear_regression_simple_submit(uint8_t model_index, feature_vector_t *feature_vector, model_results_t *model_results)
{

    model_results->result = linear_regression_predict(model_index, (float *)feature_vector->data);

    return 1;
}

/*
 * Inititalize the PME
 */
void linear_regression_init(linear_regression_model_rows_t *model_table, const uint8_t num_classifiers)
{
    ModelTable = model_table;
}
