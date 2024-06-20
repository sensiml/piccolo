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

void buffer_autoscale(ringb *pringb, int32_t base_index, int32_t length)
{

    int32_t idx;
    int16_t value = 0;
    int32_t min = KB_SHORT_INT_MAX;
    int32_t max = KB_SHORT_INT_MIN;
    float sf = 0;
    int32_t start_index = base_index;

    // find min,max:
    for (idx = 0; idx < length; idx++)
    {
        value = MOD_READ_RINGBUF(pringb, start_index++);
        if (value < min)
        {
            min = value;
        }
        if (value > max)
        {
            max = value;
        }
    }

    // get abs of min,max:
    if (max < 0)
    {
        max *= -1;
    }
    if (min < 0)
    {
        min *= -1;
    }

    // calc scale factor based on larger abs value:
    if (max >= min)
    {
        if (max > 0)
        {
            sf = 32767 / (float)max;
        }
    }
    else
    {
        if (min > 0)
        {
            sf = 32767 / (float)min;
        }
    }

    if (sf <= 1.)
    {
        return;
    }

    for (idx = base_index; idx < base_index + length; idx++)
    {
        multiply_axis_data_float(pringb, idx, sf);
    }
}
