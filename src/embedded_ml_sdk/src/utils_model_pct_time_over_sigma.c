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

int32_t utils_model_pct_time_over_sigma(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t sigma_level)
{

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !pFV)
	{
		return 0;
	}
#endif
	int32_t icol;
	int32_t base_index = kb_model->sg_index;
	ringb *rb;
	int32_t start_index;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		int32_t irow;
		int32_t sum = 0;
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

		FLOAT tmp = mean(rb, base_index, kb_model->sg_length) + sigma_level * kb_std(rb, base_index, kb_model->sg_length);
		start_index = base_index & rb->mask;
		for (irow = 0; irow < kb_model->sg_length; irow++)
		{
			FLOAT val = (FLOAT)MOD_READ_RINGBUF(rb, start_index++);
			if (val > tmp)
			{
				sum++;
			}
		}

		pFV[icol] = (FLOAT)sum / (FLOAT)kb_model->sg_length;
	}

	return cols_to_use->size;
}
