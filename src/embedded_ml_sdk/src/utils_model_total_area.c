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

int32_t utils_model_total_area(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t abs_val)
{
#define FG_AREA_TOTAL_AREA_NUM_PARAMS 1
#define FG_AREA_TOTAL_AREA_SAMPLE_RATE_PARAM_IDX 0

	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size < FG_AREA_TOTAL_AREA_NUM_PARAMS || !pFV)
		return 0;

	int32_t fsum;
	int32_t naxes, i;
	ringb *rb;
	int32_t start_index;

	for (naxes = 0; naxes < cols_to_use->size; naxes++)
	{
		fsum = 0;
		rb = kb_model->pdata_buffer->data + cols_to_use->data[naxes];
		start_index = kb_model->sg_index & rb->mask;
		for (i = 0; i < kb_model->sg_length; i++)
		{
			if (abs_val)
				fsum += abs(rb->buff[start_index]);
			else
				fsum += rb->buff[start_index];
			start_index = (start_index + 1) & rb->mask;
		}
		*pFV++ = ((float)fsum) / params->data[FG_AREA_TOTAL_AREA_SAMPLE_RATE_PARAM_IDX];
	}
	return cols_to_use->size;
}
