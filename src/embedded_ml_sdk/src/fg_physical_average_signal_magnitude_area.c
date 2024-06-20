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

int32_t fg_physical_average_signal_magnitude_area(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
    if (!kb_model || !cols_to_use || kb_model->sg_length <= 0 || cols_to_use->size <= 0 || params->size != 0 || !pFV)
    {
        return 0;
    }
#endif // SML_DEBUG

    int32_t col, idx;
    int32_t sum = 0;
    ringb *rb;
    int32_t start_index;

    for (col = 0; col < cols_to_use->size; col++)
    {
        rb = kb_model->pdata_buffer->data + cols_to_use->data[col];
        start_index = kb_model->sg_index & rb->mask;
        for (idx = 0; idx < kb_model->sg_length; idx++)
        {
            sum += MOD_READ_RINGBUF(rb, start_index++);
            // printf("%d\n", sum);
        }
    }

    // printf("%d\n", sum);

    *pFV = (float)(sum / kb_model->sg_length);

    return 1;
}
