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

//      std.c
//
//      Return square root of the arithmetic mean of the square of the
//      elements in an array.  It is called the "root mean square",
//      or the Standard Deviation.
//
//      std = SQRT(mean(abs(x - x.mean())**2))
//
//      This is the integer optimized version of std.c
//      It calls the inline routine get_axis_data(), which returns an int16.
//      The input data values are therefore in -32k..32k (16 bits).
//      The routine get_axis_data() is in ../include/rb.h.
//
//      Note that there is a small danger of integer overflow if more than
//      64k data elements are input.
//
//      Note that we are now supporting both FLOAT and int32 return values.
//      Note that we lose a small amount of  precision when the int32 divide
//      takes place, at the end of the function.

int32_t i_mean(ringb *pringb, int32_t base_index, int32_t len);

FLOAT f_std(ringb *pringb, int32_t base_index, int32_t len)
{
    int32_t irow;
    FLOAT sum = 0.0;
    FLOAT tmp;
    FLOAT xmean;

    // Compute the mean of the input data
    xmean = mean(pringb, base_index, len);

    for (irow = 0; irow < len; irow++)
    {
        tmp = MOD_READ_RINGBUF(pringb, base_index++) - xmean;
        sum += tmp * tmp;
    }

    return SQRT(sum / len);
}

int32_t i_std(ringb *pringb, int32_t base_index, int32_t len)
//
//      Returns the standard deviation, as computed using integers.
//
{
    int32_t irow;
    int32_t tmp;
    int32_t xmean;
    int64_t sum = 0.0;

    // Compute the mean of the input data
    xmean = i_mean(pringb, base_index, len);

    for (irow = 0; irow < len; irow++)
    {
        tmp = MOD_READ_RINGBUF(pringb, base_index++) - xmean;
        sum += tmp * tmp; // don't need 64-bit multiply
    }

    return (int32_t)(SQRT((FLOAT)sum / (FLOAT)len));
}

int32_t i_std_buffer(rb_data_t *buffer, int32_t len)
//
//      Returns the standard deviation, as computed using integers.
//
{
    int32_t irow;
    int32_t tmp;
    int32_t xmean;
    int64_t sum = 0.0;

    // Compute the mean of the input data
    xmean = i_mean_buff(buffer, len);

    for (irow = 0; irow < len; irow++)
    {
        tmp = buffer[irow] - xmean;
        sum += tmp * tmp; // don't need 64-bit multiply
    }

    return (int32_t)(SQRT((FLOAT)sum / (FLOAT)len));
}

FLOAT kb_std(ringb *pringb, int32_t base_index, int32_t len)
//
//      Generic version, for compatibility
//
{
    return f_std(pringb, base_index, len);
}
