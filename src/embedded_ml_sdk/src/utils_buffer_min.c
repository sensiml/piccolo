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
    min value in buffer

    Return the min of the elements in an array.
    @param pringb - pointer to ring buffer
    @param offset -offset to start at in ring buffer
    @param col - the axis of the data to get form the ring buffer
    @param datalen - the len of the data to use in the ring buffer

*/

int16_t buffer_min(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen)
{
    int32_t irow;
    int16_t val;
    int32_t start_index = (base_index + offset) & pringb->mask;
    int16_t fmin = pringb->buff[start_index];

    for (irow = 0; irow < datalen; irow++)
    {
        val = MOD_READ_RINGBUF(pringb, start_index++);
        if (fmin > val)
            fmin = val;
    }

    return fmin;
}
