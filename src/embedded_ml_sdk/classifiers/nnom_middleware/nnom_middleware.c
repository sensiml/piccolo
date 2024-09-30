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

nnom_classifier_rows_t nnom_classifier_rows;
float probability;
int32_t label;

int last_nnom_initialized = 0;
nnom_model_t* model;
uint8_t nnom_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results)
{
    uint8_t y = 1;
    float max_result = 0;

    if (last_nnom_initialized != classifier_id)
    {
            model = nnom_model_create();
            //nnom_classifier_rows[0].model=model
            last_nnom_initialized = classifier_id;
    }

    memcpy(nnom_input_data, feature_vector->data, feature_vector->size);
    nnom_predict(nnom_classifier_rows[classifier_id].model, &label, &probability);


    // regression
    if (nnom_classifier_rows[classifier_id].estimator_type == ESTIMATOR_TYPE_REGRESSION)
    {
        return (uint8_t)label;
    }

    // classification
    /*
    max_result = results[0];
    model_results->output_tensor->data[0] = (int16_t)results[0];
    for (int32_t i = 1; i < nnom_classifier_rows[classifier_id].num_outputs; i++)
    {
        if (results[i] > max_result)
        {
            max_result = results[i];
            y = i + 1;
        }
        model_results->output_tensor->data[i] = (int16_t)results[i];
    }


    if (max_result < nnom_classifier_rows[classifier_id].threshold)
    {
        model_results->result = 0.0f;
        return 0;
    }
    
    */
    model_results->result = (float)label;
    
    return float(label);
}

void nnom_init(nnom_classifier_rows_t *classifier_table, const uint8_t num_classifiers)
{
    model = nnom_model_create();
    nnom_classifier_rows = classifier_table;
    nnom_classifier_rows[0].model=model
    last_nnom_initialized=0

}

void nnom_model_results_object(int32_t classifier_id, model_results_t *model_results)
{
    for (int32_t i = 0; i < nnom_classifier_rows[classifier_id].num_outputs; i++)
    {
        model_results->output_tensor->data[i] = results[i];
    }
    model_results->output_tensor->size = nnom_classifier_rows[classifier_id].num_outputs;
}