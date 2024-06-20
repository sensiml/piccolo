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

/**
 * Return 1 if the input data passes the mse threshold.
 */

int32_t sg_filter_mse(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{

#define SG_FILTER_MSE_NUM_PARAMS 2
#define SG_FILTER_MSE_MSE_TARGET_PARAM_IDX 0
#define SG_FILTER_MSE_MSE_THRESHOLD_PARAM_IDX 1

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != SG_FILTER_MSE_NUM_PARAMS)
	{
		printf("Invalid Parameters for SG_FILTER_THRESHOLD");
		return -1;
	}
#endif

	int32_t sum = 0;
	float f_sum = 0.0f;
	int32_t icol;
	int32_t bias = (int32_t)params->data[0];
	float threshold = params->data[1];
	int32_t base_index = kb_model->sg_index;
	int32_t val;
	ringb *rb;
	int32_t start_index;
	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		int32_t irow;
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		start_index = base_index;
		for (irow = 0; irow < kb_model->sg_length; irow++)
		{
			val = (int32_t)MOD_READ_RINGBUF(rb, start_index++) - bias;
			sum += val * val;
		}
	}

	f_sum = (float)sum / (float)(kb_model->sg_length * cols_to_use->size);

	return f_sum > threshold ? 1 : 0;
}

void reset_sg_filter_mse()
{
}