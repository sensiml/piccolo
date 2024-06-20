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

/*
    Check if buffer has value greater than some threshold

    Return true if buffer has value greater than threshold else false
    @param pringb - pointer to ring buffer
    @param offset -offset to start at in ring buffer
    @param col - the axis of the data to get form the ring buffer
    @param datalen - the len of the data to use in the ring buffer
    @param threshold - value to check against

*/

bool buffer_pass_threshold(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t threshold)
{
    int32_t irow;
    int32_t start_index = base_index + offset;
    for (irow = 0; irow < datalen; irow++)
    {
        if (abs(MOD_READ_RINGBUF(pringb, start_index++)) > threshold)
        {
            return true;
        }
    }

    return false;
}

bool buffer_pass_threshold_peak_ratio(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t threshold_upper, int32_t threshold_lower, float_t ratio_limit)
{
    int32_t irow;
    int32_t start_index = base_index + offset;

    int32_t sum = 0;
    int32_t peak = 0;
    int32_t sample;
    float_t mean = 0;

    for (irow = 0; irow < datalen; irow++)
    {
        sample = abs(MOD_READ_RINGBUF(pringb, start_index++));
        sum += sample;
        if (sample > peak)
        {
            peak = sample;
        }
    }

    mean = (float_t)sum / datalen;

    if ((peak / (mean + 0.00001) > ratio_limit && peak > threshold_lower) || (peak > threshold_upper))
    {
        return true;
    }

    return false;
}
