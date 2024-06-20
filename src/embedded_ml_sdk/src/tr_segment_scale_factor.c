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

int32_t tr_segment_scale_factor(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define TR_SEGMENT_SCALE_FACTOR_NUM_PARAMS 2
#define TR_SEGMENT_SCALE_FACTOR_TYPE_PARAM_IDX 0
#define TR_SEGMENT_SCALE_FACTOR_SCALE_FACTOR_PARAM_IDX 1
	int32_t icol;
	ringb *rb;

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != 2)
	{
		return 0;
	}
#endif

	int32_t mode = (int32_t)params->data[TR_SEGMENT_SCALE_FACTOR_TYPE_PARAM_IDX];

	int32_t irow;
	int32_t base_index = kb_model->sg_index;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		float scale_factor = params->data[TR_SEGMENT_SCALE_FACTOR_SCALE_FACTOR_PARAM_IDX];

		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

		switch (mode)
		{
		case (0):
			scale_factor = buffer_standard_deviation(rb, kb_model->sg_index, 0, kb_model->sg_length);
			break;
		case (1):
			scale_factor = buffer_median(rb, kb_model->sg_index, kb_model->sg_length);
			break;
		case (2):
			scale_factor = params->data[1];
			break;
		}

		scale_factor = 1 / scale_factor;

		for (irow = base_index; irow < base_index + kb_model->sg_length; irow++)
		{
			multiply_axis_data_float(rb, irow, scale_factor);
		}
	}

	return cols_to_use->size;
}
