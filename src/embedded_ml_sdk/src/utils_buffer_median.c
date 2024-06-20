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

FLOAT buffer_median(ringb *pringb, int32_t index, int32_t datalen)
{

    int16_t *psorted;

    psorted = sorted_copy(pringb, index, datalen, 0);

    int32_t mid_index = datalen >> 1; // mid_index = n/2 where n is number of samples

    if (datalen & 1) // if n is odd, return the element in the middle
    {
        return (FLOAT)psorted[mid_index];
    }
    else // if there is an even number of elements, return mean of the two elements in the middle
    {
        return ((FLOAT)(psorted[mid_index] + psorted[mid_index - 1])) / 2.0;
    }
}
