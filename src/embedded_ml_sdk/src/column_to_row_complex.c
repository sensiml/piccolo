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

void column_to_row_complex(ringb *pringb, int32_t col, int32_t nrows, struct compx *cmpxData, int32_t complen)
{
	int32_t irow;
	int32_t base_index = 0; // REPLACE THIS WHNE THE FUNCTION IS UPDATED
	ringb *rb;

	if (nrows > complen)
		nrows = complen;

	rb = pringb + col;

	for (irow = 0; irow < nrows; irow++) // For each value in the row
	{
		cmpxData[irow].real = (FLOAT)MOD_READ_RINGBUF(rb, base_index++); // Copy sensor data to real part
		cmpxData[irow].imag = 0.0f;
	}

	for (; irow < complen; irow++)
	{
		cmpxData[irow].real = 0.0f;
		cmpxData[irow].imag = 0.0f;
	}
}
