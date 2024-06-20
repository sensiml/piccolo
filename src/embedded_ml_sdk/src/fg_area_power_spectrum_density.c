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

int32_t fg_area_power_spectrum_density(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#define FG_AREA_POWER_SPECTRUM_DENSITY_NUM_PARAMS 1
#define FG_AREA_POWER_SPECTRUM_DENSITY_SAMPLE_RATE_PARAM_IDX 0
	int32_t row, icol;
	int32_t sum;
	int32_t base_index = kb_model->sg_index;
	ringb *rb;

#if SML_DEBUG
	if (kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || params->size != 1 || !params || !pFV)
	{
		return 0;
	}
#endif

	FLOAT sample_rate = params->data[FG_AREA_POWER_SPECTRUM_DENSITY_SAMPLE_RATE_PARAM_IDX];

	for (icol = 0, sum = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		base_index = kb_model->sg_index;
		for (row = 0; row < kb_model->sg_length; row++)
		{
			int32_t data = MOD_READ_RINGBUF(rb, base_index++);
			sum += data * data;
		}
	}

	*pFV = sum * sample_rate;

	return 1;
}
