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




#include "kbalgorithms.h"
#include <stdio.h>

// Initial unoptimized implemetnation
//  We will optimize this later (an use dsp for interpolate, can also make an integer grid to get the distance)
//
int16_t interpolate(int16_t y1, int16_t y2, float x)
{
    // printf("%d %d %f ", y1, y2, x);
    return (int16_t)((y2 - y1) * x) + y1;
}

int32_t tr_segment_horizontal_scale(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define TR_HORIZONTAL_SCALE_NUM_PARAMS 1
#define TR_HORIZONTAL_SCALE_NEW_LENGTH_PARAM_IDX 0

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 2 || !cols_to_use || cols_to_use->size <= 0 || params->size != 1)
    {
        printf("ERROR WITH HORIZONTAL SCALE INPUT");
        return -1;
    }
#endif

    int32_t icol, irow;
    ringb *rb;
    int32_t start_data1, start_data2;
    int32_t base_index = kb_model->sg_index;
    int32_t length = kb_model->sg_length;
    int32_t new_length = (int32_t)params->data[TR_HORIZONTAL_SCALE_NEW_LENGTH_PARAM_IDX];

    float delta = (float)(length - 1) / (params->data[TR_HORIZONTAL_SCALE_NEW_LENGTH_PARAM_IDX] - 1);

    int32_t x0 = 0;
    float x = 0;

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
        x0 = 0;
        x = 0;
        sortedData[0] = rb->buff[base_index & rb->mask];

        for (irow = 1; irow < new_length - 1; irow++)
        {
            x += delta;
            x0 = (int32_t)x;
            start_data1 = rb->buff[(base_index + x0) & rb->mask];
            start_data2 = rb->buff[(base_index + x0 + 1) & rb->mask];
            sortedData[irow] = interpolate(start_data1, start_data2, x - x0);
        }

        sortedData[new_length - 1] = rb->buff[(base_index + length - 1) & rb->mask];

        for (irow = 0; irow < new_length; irow++)
        {
            rb->buff[irow] = sortedData[irow];
        }

        rb->tail = 0;
        rb->head = new_length;
    }
    kb_model->sg_length = new_length;

    return cols_to_use->size;
}