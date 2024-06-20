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
 * Return 0 if any of the data is outside the threshold range.
 * Return 1 if the segment isn't filtered out.
 */

int32_t sg_filter_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define SG_FILTER_THRESHOLD_NUM_PARAMS 2
#define SG_FILTER_THRESHOLD_THRESHOLD_PARAM_IDX 0
#define SG_FILTER_THRESHOLD_COMPARE_PARAM_IDX 1

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != SG_FILTER_THRESHOLD_NUM_PARAMS)
	{
		return -1;
	}
#endif

	ringb *rb;
	int32_t start_index;
	int32_t threshold = (int32_t)params->data[SG_FILTER_THRESHOLD_THRESHOLD_PARAM_IDX];
	int32_t compare = (int32_t)params->data[SG_FILTER_THRESHOLD_COMPARE_PARAM_IDX];
	int32_t irow, icol;

	switch (compare)
	{
	case (0):
		for (icol = 0; icol < cols_to_use->size; icol++)
		{
			rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
			start_index = kb_model->sg_index & rb->mask;
			for (irow = 0; irow < kb_model->sg_length; irow++)
			{
				if (MOD_READ_RINGBUF(rb, start_index++) > threshold)
				{
					return 0;
				}
			}
		}
		break;
	case (1):
		for (icol = 0; icol < cols_to_use->size; icol++)
		{
			rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
			start_index = kb_model->sg_index & rb->mask;
			for (irow = 0; irow < kb_model->sg_length; irow++)
			{
				if (MOD_READ_RINGBUF(rb, start_index++) < threshold)
				{
					return 0;
				}
			}
		}
		break;
	}

	return 1;
}

void reset_sg_filter_threshold()
{
}