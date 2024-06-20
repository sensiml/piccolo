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

//      mean.c
//
//	Return the arithmetic mean of the elements in an array.
//
//      This is the integer optimized version of mean.c
//      It calls the inline routine get_axis_data(), which returns an int16.
//      The input data values are therefore in -32k..32k (16 bits).
//      The routine get_axis_data() is in ../include/rb.h.
//
//	Note that there is a small danger of integer overflow if more than
//	64k data elements are input.
//
//	Note that we are now supporting both FLOAT and int32 return values.
//	Note that we lose a small amount of  precision when the int32 divide
//	takes place, at the end of the function.

FLOAT mean(ringb *pringb, int32_t base_index, int32_t len)
{
    if ((!pringb) || (!len))
    {
        return 0;
    }

    int32_t irow;
    int64_t sum = 0;

    for (irow = base_index; irow < (base_index + len); irow++)
    {
        sum += MOD_READ_RINGBUF(pringb, irow);
    }

    return ((FLOAT)sum / len);
}

int32_t i_mean(ringb *pringb, int32_t base_index, int32_t len)
{
    int32_t irow;
    int32_t sum = 0;

    for (irow = base_index; irow < (base_index + len); irow++)
    {
        sum += MOD_READ_RINGBUF(pringb, irow); // add int16 to int32
    }

    return (int32_t)(sum / len);
}

int32_t i_mean_buff(rb_data_t *buff, int32_t len)
{
    int32_t irow;
    int32_t sum = 0;

    for (irow = 0; irow < len; irow++)
    {
        sum += buff[irow]; // add int16 to int32
    }

    return (int32_t)(sum / len);
}
