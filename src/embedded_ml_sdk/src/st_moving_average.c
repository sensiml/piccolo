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
 * \brief Moving average for incomming sensor data by taking the average over filter order
 *
 * \param ringbuffer pointer to the ring buffer to add data too
 * \param input_data Pointer to the data which will be transformed
 */
int16_t ma_filter_full(ringb *pringb, int32_t filter_order)
{
    int32_t val = 0;
    int32_t num_vals = 2 * filter_order + 1;

    for (int32_t i = 0; i < num_vals; i++)
    {
        val += rb_read_offset(pringb, i);
    }

    return val / num_vals;
}

int16_t time_lapse(ringb *pringb, int32_t filter_order)
{
    return rb_read_offset(pringb, filter_order);
}

int32_t streaming_moving_average(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, int32_t filter_order)
{
    saveSensorData(pringb, pSample, cols_to_use->size);
    ringb *rb;

    if (rb_items(pringb) < (2 * filter_order))
    {
        return -1;
    }

    for (int32_t i = 0; i < cols_to_use->size; i++)
    {
        rb = pringb + i;
        if (cols_to_use->data[i])
        {
            pSample[i] = (int16_t)ma_filter_full(rb, filter_order);
        }
        else
        {
            pSample[i] = (int16_t)time_lapse(rb, filter_order);
        }
        rb_step_head(rb, 1);
    }

    // printf("moving avg %d\n" , get_col_data(rbuff_index, index));

    return 1;
}
