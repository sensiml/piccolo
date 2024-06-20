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




#include "kbutils.h"
#include "kb_post_processing.h"

void setup_feature_set(feature_set_t *feature_set, uint16_t size, uint16_t feature_length, FLOAT *pbuffer)
{

    feature_set->data = pbuffer;
    feature_set->sum = pbuffer + size * feature_length;
    feature_set->average = pbuffer + size * feature_length + feature_length;

    feature_set->size = size;
    feature_set->feature_length = feature_length;

    init_feature_set(feature_set);
}

uint_fast16_t get_buffer_size(uint16_t size, uint16_t feature_length)
{
    return size * feature_length + feature_length + feature_length;
}

int init_feature_set(feature_set_t *feature_set)
{
    if (feature_set == NULL)
    {
        return 1;
    }
    feature_set->index = 0;
    feature_set->num_elements = 0;

    for (int i = 0; i < (int)feature_set->feature_length * feature_set->size; i++)
    {
        feature_set->data[i] = 0;
    }

    for (int i = 0; i < (int)feature_set->feature_length; i++)
    {
        feature_set->sum[i] = 0;
        feature_set->average[i] = 0;
    }

    return 0;
}

int push_feature(feature_set_t *feature_set, FLOAT *feature)
{
    if (feature_set == NULL)
        return 1;

    int ix = (int)feature_set->index;
    int N = (int)feature_set->feature_length;

    for (int i = 0; i < N; i++)
    {
        feature_set->sum[i] += (feature[i] - feature_set->data[ix * N + i]);
        feature_set->data[ix * N + i] = feature[i];
    }

    feature_set->num_elements = min(feature_set->num_elements + 1, feature_set->size);

    for (int i = 0; i < N; i++)
    {
        feature_set->average[i] = (FLOAT)feature_set->sum[i] / feature_set->num_elements;
    }

    feature_set->index = MOD(feature_set->index + 1, feature_set->size);

    return 0;
}

int pop_first_feature(feature_set_t *feature_set)
{
    if (feature_set == NULL)
        return 1;

    if (feature_set->num_elements == 0)
        return 2;

    int N = (int)feature_set->feature_length;
    uint16_t head_index = head_index_feature_set(feature_set);

    for (int i = 0; i < N; i++)
    {
        feature_set->sum[i] -= feature_set->data[head_index * N + i];
    }

    feature_set->num_elements = feature_set->num_elements - 1;

    for (int i = 0; i < N; i++)
    {
        feature_set->average[i] = (FLOAT)feature_set->sum[i] / feature_set->num_elements;
    }

    return 0;
}

int pop_last_feature(feature_set_t *feature_set)
{
    if (feature_set == NULL)
        return 1;

    if (feature_set->num_elements == 0)
        return 2;

    int N = (int)feature_set->feature_length;
    uint16_t tail_index = tail_index_feature_set(feature_set);

    for (int i = 0; i < N; i++)
    {
        feature_set->sum[i] -= feature_set->data[tail_index * N + i];
    }

    feature_set->num_elements = feature_set->num_elements - 1;

    for (int i = 0; i < N; i++)
    {
        feature_set->average[i] = (FLOAT)feature_set->sum[i] / feature_set->num_elements;
    }

    feature_set->index = MOD(feature_set->index - 1, feature_set->size);

    return 0;
}

uint16_t head_index_feature_set(feature_set_t *feature_set)
{
    return MOD(feature_set->index - feature_set->num_elements, feature_set->size);
}

uint16_t tail_index_feature_set(feature_set_t *feature_set)
{
    return MOD(feature_set->index - 1, feature_set->size);
}

uint16_t base_index_feature_set(feature_set_t *feature_set)
{
    return MOD(feature_set->index - feature_set->num_elements, feature_set->size);
}

void get_feature_at_index(feature_set_t *feature_set, uint16_t index, FLOAT *feature)
{
    uint16_t i = MOD(base_index_feature_set(feature_set) + index, feature_set->size);

    get_feature_at_dynamic_index_(feature_set, i, feature);
}

void get_feature_at_dynamic_index_(feature_set_t *feature_set, uint16_t i, FLOAT *feature)
{
    for (int j = 0; j < feature_set->feature_length; j++)
    {
        feature[j] = feature_set->data[feature_set->feature_length * i + j];
    }
}

void get_head_feature_set(feature_set_t *feature_set, FLOAT *head)
{
    uint16_t index = head_index_feature_set(feature_set);
    get_feature_at_dynamic_index_(feature_set, index, head);
}

void get_tail_feature_set(feature_set_t *feature_set, FLOAT *tail)
{
    uint16_t index = tail_index_feature_set(feature_set);
    get_feature_at_dynamic_index_(feature_set, index, tail);
}
