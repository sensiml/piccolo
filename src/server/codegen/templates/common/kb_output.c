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

#include "kb_output.h"

int32_t sprint_model_feature_vector(char *pbuf, int index)
{
    int32_t count = 0;
    float test = 0;
    uint16_t size = kb_get_feature_vector_size(index);
    uint16_t fv_len;

    count += sprintf(pbuf + count, "[");
    if (get_feature_vector_type(index) == 1)
    {
        uint8_t *arr;
        get_feature_vector_data_pointer(index, (void **)&arr);
        for (int i = 0; i < size - 1; i++)
        {
            count += sprintf(pbuf + count, "%d,", arr[i]);
        }
        count += sprintf(pbuf + count, "%d]", arr[size - 1]);
    }
    else
    {
        float *arr;
        get_feature_vector_data_pointer(index, (void **)&arr);
        for (int i = 0; i < size - 1; i++)
        {
            count += sprintf(pbuf + count, "%f,", arr[i]);
        }
        count += sprintf(pbuf + count, "%f]", arr[size - 1]);
    }

    return count;
}

int32_t kb_sprint_model_output_tensor(int32_t model_index, char *pbuf)
{

    int32_t count = 0;
    int32_t j = 0;

    model_results_t *pmodel_result;
    pmodel_result = kb_get_model_result_info(model_index);

    count += sprintf(pbuf + count, "[");

    if (pmodel_result->output_tensor->size > 0)
    {
        for (j = 0; j < pmodel_result->output_tensor->size - 1; j++)
        {
            count += sprintf(pbuf + count, "%f,", pmodel_result->output_tensor->data[j]);
        }
        count += sprintf(pbuf + count, "%f]", pmodel_result->output_tensor->data[j]);
    }
    else
    {
        count += sprintf(pbuf + count, "]");
    }
    return count;
}

int32_t kb_sprint_model_result(
    int32_t model_index, char *pbuf, bool segment_info, bool feature_vectors, bool output_tensor)
{
    int32_t count = 0;
    model_results_t *pmodel_result;

    count += sprintf(
        pbuf + count,
        "{\"ModelNumber\":%d",
        model_index);

    pmodel_result = kb_get_model_result_info(model_index);
    if (pmodel_result->model_type == 1)
    {
        count += sprintf(pbuf + count, ",\"Classification\":%d", (int)pmodel_result->result);
    }
    else if (pmodel_result->model_type == 2)
    {
        count += sprintf(pbuf + count, ",\"Result\":%f", pmodel_result->result);
    }

    if (segment_info)
    {
        count += sprintf(pbuf + count,
                         ",\"SegmentStart\":%d,\"SegmentLength\":%d",
                         kb_get_segment_start(model_index),
                         kb_get_segment_length(model_index));
    }

    if (feature_vectors)
    {
        uint16_t fv_size = kb_get_feature_vector_size(model_index);
        count += sprintf(pbuf + count, ",\"FeatureVectorLength\":%d, \"FeatureVector\":", fv_size);
        count += sprint_model_feature_vector(pbuf + count, model_index);
    }
    if (output_tensor)
    {
        model_results_t *pmodel_result;
        pmodel_result = kb_get_model_result_info(model_index);
        count += sprintf(pbuf + count, ",\"OutputSize\":%d,\"OutputTensor\":", pmodel_result->output_tensor->size);
        count += kb_sprint_model_output_tensor(model_index, pbuf + count);
    }

    count += sprintf(pbuf + count, "}");

    return count;
}

void kb_print_model_class_map(int32_t model_index, char *output)
{
    printf("\n");
    switch (model_index)
    {

    default:
        break;
    }
}

void kb_print_model_map()
{
    // FILL_MODEL_MAP
    printf("\n");
}

int32_t kb_sprint_model_cycles(
    int32_t model_index, char *pbuf, uint32_t *cycles)
{
    uint16_t fv_len;
    int32_t count = 0;
    float classifier_time;
    uint32_t classifier_cycles;

    if (!kb_is_profiling_enabled(model_index))
    {
        count += sprintf(pbuf, "Model %d does not have profiling enabled\n", model_index);
        return count;
    }

    count += sprintf(
        pbuf,
        "{\"ModelNumber\":%d,\"Type\":\"Cycles\"",
        model_index);

    fv_len = kb_get_feature_vector_size(model_index);
    kb_get_feature_gen_cycles(model_index, cycles);
    classifier_cycles = kb_get_classifier_cycles(model_index);

    count += sprintf(pbuf + count, ", \"FeatureCycles\":[");
    for (int32_t j = 0; j < fv_len - 1; j++)
    {
        count += sprintf(pbuf + count, "%d,", cycles[j]);
    }
    count += sprintf(pbuf + count, "%d],", cycles[fv_len - 1]);

    count += sprintf(pbuf + count, "\"ClassifierCycles\": %d", classifier_cycles);
    count += sprintf(pbuf + count, "}\n");

    return count;
}

int32_t kb_sprint_model_times(
    int32_t model_index, char *pbuf, float *times)
{
    uint16_t fv_len;
    int32_t count = 0;
    float classifier_time;
    uint32_t classifier_cycles;

    if (!kb_is_profiling_enabled(model_index))
    {
        count += sprintf(pbuf, "Model %d does not have profiling enabled\n", model_index);
        return count;
    }

    count += sprintf(
        pbuf,
        "{\"ModelNumber\":%d,\"Type\":\"Times\"",
        model_index);
    fv_len = kb_get_feature_vector_size(model_index);
    kb_get_feature_gen_times(model_index, times);
    classifier_time = kb_get_classifier_time(model_index);

    count += sprintf(pbuf + count, ", \"FeatureTimes\":[");
    for (int32_t j = 0; j < fv_len - 1; j++)
    {
        count += sprintf(pbuf + count, "%.9f,", times[j]);
    }
    count += sprintf(pbuf + count, "%.9f], ", times[fv_len - 1]);
    count += sprintf(pbuf + count, "\"ClassifierTime\": %.9f, ", classifier_time);
    count += sprintf(pbuf + count, "}\n");

    return count;
}
