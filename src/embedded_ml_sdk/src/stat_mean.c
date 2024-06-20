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

FLOAT stat_mean(ringb *rb, int32_t base_index, int32_t len)
{
    FLOAT t = 0;
    int32_t irow;
    int32_t start_index = base_index;

    for (irow = 0; irow < len; irow++)
    {
        t += MOD_READ_RINGBUF(rb, start_index++);
    }
    return t / len;
}
