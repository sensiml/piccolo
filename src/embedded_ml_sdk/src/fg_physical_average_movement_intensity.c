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




#include "kbalgorithms.h"

int32_t fg_physical_average_movement_intensity(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
	if (!kb_model || !cols_to_use || kb_model->sg_length <= 0 || cols_to_use->size <= 0 || params->size != 0 || !pFV)
	{
		return 0;
	}
#endif // SML_DEBUG

	int32_t col, row;
	int16_t val;
	uint32_t sumOfSquares;
	uint32_t SumOfNorms = 0;
	ringb *rb;

	for (row = 0; row < kb_model->sg_length; row++)
	{
		sumOfSquares = 0;

		for (col = 0; col < cols_to_use->size; col++)
		{
			rb = kb_model->pdata_buffer->data + cols_to_use->data[col];
			val = rb->buff[(row + kb_model->sg_index) & rb->mask];
			sumOfSquares += val * val;
		}
		SumOfNorms += SQRT(sumOfSquares);
	}

	*pFV = SumOfNorms / kb_model->sg_length;

	return 1;
}
