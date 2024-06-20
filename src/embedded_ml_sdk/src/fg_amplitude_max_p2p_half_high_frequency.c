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

#define NSAMPLE_RATE 10
#define FLAG_DC_AC 1
#define FLAG_USE_SAMPLE_RATE 0
#define FLAG_ABS_BEFORE_SUM 0
#define FLAG_ABS_AFTER_SUM 0

int32_t fg_amplitude_max_p2p_half_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define MAX_P2P_HALF_HIGH_FREQUENCY_NUM_PARAMS 1
#define MAX_P2P_HALF_HIGH_FREQUENCY_SMOOTHING_FACTOR_PARAM_IDX 0
	int32_t icol;
	int32_t sf = (int32_t)params->data[MAX_P2P_HALF_HIGH_FREQUENCY_SMOOTHING_FACTOR_PARAM_IDX];

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		MA_Symmetric(kb_model->pdata_buffer->data, kb_model->sg_index, kb_model->sg_length / 2, sf, cols_to_use->data[icol], NSAMPLE_RATE, FLAG_DC_AC, FLAG_USE_SAMPLE_RATE,
					 FLAG_ABS_BEFORE_SUM, FLAG_ABS_AFTER_SUM, max_p2p_half_high_frequency_name, &pFV[icol]);
	}
	return cols_to_use->size;
}
