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

int32_t fg_area_total_area_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_AREA_TOTAL_AREA_HIGH_FREQUENCY_NUM_PARAMS 2
#define FG_AREA_TOTAL_AREA_HIGH_FREQUENCY_SAMPLE_RATE_PARAM_IDX 0
#define FG_AREA_TOTAL_AREA_HIGH_FREQUENCY_SMOOTHING_FACTOR_PARAM_IDX 1
	int32_t icol;
	FLOAT sample_rate;
	int32_t smoothing_factor;

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size < FG_AREA_TOTAL_AREA_HIGH_FREQUENCY_NUM_PARAMS || !pFV)
		return 0;
#endif

	sample_rate = params->data[FG_AREA_TOTAL_AREA_HIGH_FREQUENCY_SAMPLE_RATE_PARAM_IDX];
	smoothing_factor = (int32_t)params->data[FG_AREA_TOTAL_AREA_HIGH_FREQUENCY_SMOOTHING_FACTOR_PARAM_IDX];

	for (icol = 0; icol < cols_to_use->size; icol++)
		MA_Symmetric(kb_model->pdata_buffer->data, kb_model->sg_index, kb_model->sg_length, smoothing_factor, cols_to_use->data[icol], sample_rate, 1, 1, 0, 1, total_area_high_frequency_name, pFV);

	return cols_to_use->size;
}
