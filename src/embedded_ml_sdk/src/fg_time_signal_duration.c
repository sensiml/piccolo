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

int32_t fg_time_signal_duration(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define SIGNAL_DURATION_NUM_PARAMS 1
#define SIGNAL_DURATION_SAMPLE_RATE_PARAM_IDX 0
	FLOAT sample_rate, fval;
	int32_t icol;

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size < SIGNAL_DURATION_NUM_PARAMS || !pFV)
		return 0;
#endif

	sample_rate = params->data[SIGNAL_DURATION_SAMPLE_RATE_PARAM_IDX];
	fval = (FLOAT)kb_model->sg_length / sample_rate;
	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		pFV[icol] = fval;
	}
	return cols_to_use->size;
}
