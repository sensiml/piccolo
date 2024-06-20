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

int32_t i_sum(ringb *pringb, int32_t base_index, int32_t num_rows)
{
    int32_t sum;
    int32_t irow;

    sum = 0;

    for (irow = 0; irow < num_rows; irow++)
    {
        sum += MOD_READ_RINGBUF(pringb, base_index++); // 16-bit elements, added to 32-bit accumulator
    }

    return sum;
}

FLOAT sum(ringb *pringb, int32_t base_index, int32_t num_rows)
{
    return (FLOAT)i_sum(pringb, base_index, num_rows);
}
