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
 * \brief Downsample incomming sensor data by taking the average over filter length
 *
 * \param ringbuffer pointer to the ring buffer to add data too
 * \param input_data Pointer to the data which will be transformed
 */
int32_t streaming_downsample_by_decimation(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, int32_t filter_length)
{
    ringb *rb = pringb;

    if (rb->stat < filter_length - 1)
    {
        rb->stat += 1;
        return -1;
    }

    rb->stat = 0;

    return 1;
}
