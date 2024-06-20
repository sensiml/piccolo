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

int32_t utils_model_stats_max_min(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t max)
{
	int32_t icol;
	ringb *rb;
	int16_t data, max_value, min_value;
	int32_t start_index;

#if SML_DEBUG
	if (kb_model == NULL || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !pFV || !params)
	{
		return 0;
	}
#endif

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		start_index = kb_model->sg_index & rb->mask;
		max_value = rb->buff[start_index];
		min_value = max_value;
		for (int32_t row = 0; row < kb_model->sg_length; row++)
		{
			data = MOD_READ_RINGBUF(rb, start_index++);
			if (max == FIND_MAX_VAL)
			{
				if (data > max_value)
					max_value = data;
			}
			else
			{
				if (data < min_value)
					min_value = data;
			}
		}
		if (max == FIND_MAX_VAL)
			pFV[icol] = (FLOAT)max_value;
		else
			pFV[icol] = (FLOAT)min_value;
	}

	return cols_to_use->size;
}
