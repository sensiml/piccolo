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

int32_t fg_roc_second_sigma_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
	int32_t icol;
	ringb *rb;

#if SML_DEBUG
	if (!kb_model || !cols_to_use || cols_to_use->size <= 0 || params->size != 0 || kb_model->sg_length <= 0 || !pFV)
		return 0;
#endif

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		int stdval = 0.0f;

		copy_segment_to_buff(rb, sortedData, kb_model->sg_index, kb_model->sg_length);

		// Compute standard deviation
		if (kb_model->sg_length >= 2)
		{
			stdval = i_std_buffer(sortedData, kb_model->sg_length) * 2;
		}

		int32_t num_crossings = calculate_zc_with_threshold_xor(sortedData, kb_model->sg_length, stdval);

		*pFV++ = (float)num_crossings / (kb_model->sg_length - 1);
	}
	return cols_to_use->size;
}
