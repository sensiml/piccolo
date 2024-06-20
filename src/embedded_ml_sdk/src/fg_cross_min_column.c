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

#define NUM_PARAMS 0

int32_t fg_cross_column_min_column(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
	if (!kb_model || !cols_to_use || kb_model->sg_length <= 0 || cols_to_use->size <= 0 || params->size != NUM_PARAMS || !pFV)
	{
		return 0;
	}
#endif

	uint64_t sum = 0;
	int32_t row, icol;
	int16_t min_col = 1;
	ringb *rb;
	int32_t base_index = kb_model->sg_index;
	int16_t data, min_value;
	rb = kb_model->pdata_buffer->data + cols_to_use->data[0];
	min_value = MOD_READ_RINGBUF(rb, base_index);
	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		base_index = kb_model->sg_index;
		for (row = 0; row < kb_model->sg_length; row++)
		{
			data = MOD_READ_RINGBUF(rb, base_index++);
			if (data < min_value)
			{
				min_col = icol + 1;
				min_value = data;
			}
		}
	}
	*pFV = (FLOAT)min_col;

	return 1;
}
