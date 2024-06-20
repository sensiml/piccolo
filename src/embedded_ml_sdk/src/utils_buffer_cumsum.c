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

FLOAT buffer_cumulative_sum_0(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t abs_val)
{
    int32_t i;
    int32_t sum = 0;
    int32_t start_index = (base_index + offset) & pringb->mask;

    for (i = 0; i < datalen; i++)
    {
        if (abs_val)
            sum += abs(pringb->buff[start_index]);
        else
            sum += pringb->buff[start_index];
        start_index = (start_index + 1) & pringb->mask;
    }

    return (FLOAT)sum;
}

FLOAT buffer_cumulative_sum(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen)
{
    return buffer_cumulative_sum_0(pringb, base_index, offset, datalen, BUFFER_NO_ABS);
}

#if 0 // these 2 loops makes the code clumsy 
FLOAT buffer_cumulative_sum_0(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t abs_val)
{
    int32_t i;
    int32_t sum = 0;
    int32_t start_index = (base_index + offset) & pringb->mask;;
    int32_t rb_length = pringb->mask + 1;
    int32_t final_index = start_index + datalen;

    if(final_index > pringb->mask)
    {
        for (i = start_index; i < rb_length; i++)
        {
            if(abs_val)
                sum += abs(pringb->buff[i]);
            else
                sum += pringb->buff[i];
        }
        start_index = 0;
        final_index = final_index - rb_length;
    }
    if(final_index > 0)
    {
        for (i = start_index; i < final_index; i++)
        {
            if(abs_val)
                sum += abs(pringb->buff[i]);
            else
                sum += pringb->buff[i];
        }
    }

    return (FLOAT)sum;
}

#endif