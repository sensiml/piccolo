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

#define NUM_PARAMS 1
#define OFFSET_PARAM_IDX 0
int32_t utils_model_mean_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, FLOAT *pFV, int32_t offset)
{

#if SML_DEBUG
    if (!kb_model || !cols_to_use || cols_to_use->size != 2 || kb_model->sg_length <= 0 || !pFV)
    {
        return 0;
    }
#endif

    int32_t sum = 0;
    int32_t base_index = kb_model->sg_index;
    ringb *rb;

    rb = kb_model->pdata_buffer->data + cols_to_use->data[0];

    for (int32_t i = 0; i < kb_model->sg_length; i++)
    {
        sum += MOD_READ_RINGBUF(rb, base_index++); // mean = sum << num_bits(mask);
    }

    sum = offset + sum / kb_model->sg_length;

    rb = kb_model->pdata_buffer->data + cols_to_use->data[1];

    copy_segment_to_buff(rb, sortedData, kb_model->sg_index, kb_model->sg_length);

    float num_crossings = (float)calculate_zc_with_threshold_xor(sortedData, kb_model->sg_length, sum / kb_model->sg_length);

    *pFV++ = num_crossings / kb_model->sg_length;

    return 1;
}
