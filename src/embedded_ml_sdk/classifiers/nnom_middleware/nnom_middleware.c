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




#include "nnom_middleware.h"


float results[NNOM_MAX_NUMBER_REULTS];

nnom_classifier_rows_t NNOMClassifierTable;

uint8_t tf_micro_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results)
{
    uint8_t y = 1;
    float max_result = 0;

    if (last_nnom_initialized != classifier_id)
    {
        micro_model_setup(NNOMClassifierTable[classifier_id].model_data, NNOMClassifierTable[classifier_id].kTensorArenaSize, NNOMClassifierTable[classifier_id].tensor_arena);
        last_nnom_initialized = classifier_id;
    }

    memcpy(nnom_input_data, feature_vector.data, feature_vector.size);
    nnom_predict(NNOMClassifierTable[classifier_id].model, &model_results.result, &model_results.output_tensor);


    // regression
    if (NNOMClassifierTable[classifier_id].estimator_type == ESTIMATOR_TYPE_REGRESSION)
    {
        return (uint8_t)results[0];
    }

    // classification
    max_result = results[0];
    model_results->output_tensor->data[0] = (int16_t)results[0];
    for (int32_t i = 1; i < NNOMClassifierTable[classifier_id].num_outputs; i++)
    {
        if (results[i] > max_result)
        {
            max_result = results[i];
            y = i + 1;
        }
        model_results->output_tensor->data[i] = (int16_t)results[i];
    }

    if (max_result < NNOMClassifierTable[classifier_id].threshold)
    {
        model_results->result = 0.0f;
        return 0;
    }

    model_results->result = (float)y;

    return y;
}

void nnom_init(tf_micro_classifier_rows_t *classifier_table, const uint8_t num_classifiers)
{
    model = nnom_model_create();
    NNOMClassifierTable = classifier_table;
    NNOMClassifierTable[0].model=model

}

void nnom_model_results_object(int32_t classifier_id, model_results_t *model_results)
{
    for (int32_t i = 0; i < NNOMClassifierTable[classifier_id].num_outputs; i++)
    {
        model_results->output_tensor->data[i] = results[i];
    }
    model_results->output_tensor->size = NNOMClassifierTable[classifier_id].num_outputs;
}