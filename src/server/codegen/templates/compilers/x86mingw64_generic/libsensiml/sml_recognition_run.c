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

#include "kb.h"
#include "kb_typedefs.h"
#include "sml_recognition_run.h"
#ifdef SML_USE_TEST_DATA
#include "testdata.h"
int32_t td_index = 0;
#endif // SML_USE_TEST_DATA

static int32_t last_model_result;
static int32_t last_class_result;
static int32_t last_segment_length;
static int32_t last_feature_bank_number;
static model_results_t *model_result;

int32_t get_last_segment_length()
{
    return last_segment_length;
}

int32_t get_last_feature_bank_number()
{
    return last_feature_bank_number;
}

int32_t get_last_result_model()
{
    return last_model_result;
}

int32_t get_last_result_class()
{
    return (int32_t)model_result->result;
}

int32_t get_output_tensor_size()
{
    return model_result->output_tensor->size;
}

int32_t copy_output_tensor(float *output_tensor)
{
    for (int i = 0; i < model_result->output_tensor->size; i++)
    {
        output_tensor[i] = model_result->output_tensor->data[i];
    }

    return model_result->output_tensor->size;
}

int32_t get_feature_vector_size(int model_index)
{
    feature_vector_t *pfeature_vector;
    pfeature_vector = get_feature_vector_pointer(model_index);
    return (int32_t)pfeature_vector->size;
}

int32_t copy_feature_vector_float(int model_index, float *feature_vector)
{
    feature_vector_t *pfeature_vector;
    pfeature_vector = get_feature_vector_pointer(model_index);

    uint8_t *arr_uint8t = (uint8_t *)pfeature_vector->data;
    float *arr_float = (float *)pfeature_vector->data;

    for (int i = 0; i < pfeature_vector->size; i++)
    {
        if (pfeature_vector->typeID == 1)
        {
            feature_vector[i] = (float)arr_uint8t[i];
        }
        else
        {
            feature_vector[i] = arr_float[i];
        }
    }

    return (int32_t)pfeature_vector->size;
}

void sml_output_results(int32_t model, int32_t classification)
{
    last_model_result = model;
    model_result = kb_get_model_result_info(model);
    last_segment_length = kb_get_segment_length(model);
    last_feature_bank_number = sml_get_feature_bank_number(model);
}

int32_t sml_recognition_run(signed short *data, int32_t num_sensors)
{
    int32_t ret = -1;
    // FILL_RUN_MODEL_CUSTOM
    // FILL_RUN_MODEL_AUDIO
    // FILL_RUN_MODEL_MOTION
    return ret;
}
