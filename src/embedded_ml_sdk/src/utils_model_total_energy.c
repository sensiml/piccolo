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

int32_t utils_model_total_energy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t abs_val)
{
#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || params->size != 0 || !pFV)
	{
		return 0;
	}
#endif

	float sum = 0;
	int32_t row, icol;
	short data;
	int32_t base_index = kb_model->sg_index;
	ringb *rb;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		base_index = kb_model->sg_index;

		for (row = 0; row < kb_model->sg_length; row++)
		{
			data = MOD_READ_RINGBUF(rb, base_index++);
			if (abs_val)
				sum += abs(data);
			else
				sum += data * data;
		}
	}
	if (abs_val)
		*pFV = (float)sum;
	else
		*pFV = ((float)sum) / kb_model->sg_length;

	return 1;
}
