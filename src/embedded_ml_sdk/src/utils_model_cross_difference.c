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

#define NUM_PARAMS 0

int32_t utils_model_cross_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t min_max)
{

#if SML_DEBUG
    if (!kb_model || !cols_to_use || kb_model->sg_length <= 0 || cols_to_use->size <= 0 || params->size != NUM_PARAMS || !pFV)
    {
        return 0;
    }
#endif

    int32_t i, index_col1, index_col2;
    int16_t val_col1, val_col2, max_col1, max_col2;
    ringb *rb1;
    ringb *rb2;
    int32_t base_index = kb_model->sg_index;

    rb1 = kb_model->pdata_buffer->data + cols_to_use->data[0];
    rb2 = kb_model->pdata_buffer->data + cols_to_use->data[1];

    index_col1 = base_index;
    index_col2 = base_index;

    max_col1 = KB_SHORT_INT_MIN;
    max_col2 = KB_SHORT_INT_MIN;
    int32_t final_index = base_index + kb_model->sg_length;

    for (i = base_index; i < final_index; i++)
    {
        val_col1 = MOD_READ_RINGBUF(rb1, i);
        val_col2 = MOD_READ_RINGBUF(rb2, i);

        if (val_col1 < max_col1)
        {
            max_col1 = val_col1;
            index_col1 = i;
        }

        if (val_col2 < max_col2)
        {
            max_col2 = val_col2;
            index_col2 = i;
        }
    }

    if (min_max)
    {
        if (max_col1 > max_col2)
        {
            *pFV = (FLOAT)(max_col1 - rb2->buff[index_col1 & rb2->mask]);
        }
        else
        {
            *pFV = (FLOAT)(max_col2 - rb1->buff[index_col2 & rb1->mask]);
        }
    }
    else
    {
        *pFV = (FLOAT)(max_col1 - max_col2);
    }

    return 1;
}
