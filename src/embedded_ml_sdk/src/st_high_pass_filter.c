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

/*!
 * \brief Simple IIR filter
 *
 * \param pringb pointer to the ring buffer to add data too
 * \param pSample Pointer to the data which will be transformed
 * \param cols_to_use columns to transform
 * \param num_cols number of columns ub in col_to_use
 * \param alpha attenuation coefficient
 */

int32_t streaming_high_pass_filter(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, float alpha)
{
    ringb *rb;
    int32_t col;
    if (rb_status(pringb) == false)
    {
        for (int32_t i = 0; i < cols_to_use->size; i++)
        {
            rb = pringb + i;
            rb->stat = pSample[cols_to_use->data[i]];
            rb_lock(rb);
        }
        return -1;
    }

    for (int32_t i = 0; i < cols_to_use->size; i++)
    {
        rb = pringb + i;
        col = cols_to_use->data[i];
        {
            pSample[col] = (int16_t)(pringb->stat + (int16_t)(alpha * (float)(pSample[col] - rb->stat)));
            rb->stat = pSample[col];
        }
    }

    // printf("moving avg %d\n" , get_col_data(rbuff_index, index));

    return 1;
}
