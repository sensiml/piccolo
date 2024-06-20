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
#define FG_ROC_THRESHOLD_CROSSING_RATE_NUM_PARAMS 1
#define FG_ROC_THRESHOLD_CROSSING_RATE_THRESHOLD_PARAM_IDX 0

int32_t fg_roc_threshold_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
	if (!kb_model || !cols_to_use || !pFV || !params || cols_to_use->size <= 0 || params->size != FG_ROC_THRESHOLD_CROSSING_RATE_NUM_PARAMS || kb_model->sg_length <= 0)
		return 0;
#endif

	int32_t icol;
	ringb *rb;

	int32_t threshold = (int32_t)params->data[FG_ROC_THRESHOLD_CROSSING_RATE_THRESHOLD_PARAM_IDX];

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

		copy_segment_to_buff(rb, sortedData, kb_model->sg_index, kb_model->sg_length);

		int32_t num_crossings = (float)calculate_zc_with_threshold_xor(sortedData, kb_model->sg_length, threshold);

		*pFV++ = (float)num_crossings / (kb_model->sg_length - 1);
	}
	return cols_to_use->size;
}
