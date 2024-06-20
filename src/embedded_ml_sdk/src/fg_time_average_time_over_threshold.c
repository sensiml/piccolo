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

int32_t fg_time_avg_time_over_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_TIME_AVG_TIME_OVER_THRESHOLD_NUM_PARAMS 1
#define FG_TIME_AVG_TIME_OVER_THRESHOLD_THRESHOLD_PARAM_IDX 0

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !pFV)
		return 0;
#endif

	int32_t icol;
	int32_t base_index = kb_model->sg_index;
	int32_t threshold = (int32_t)params->data[FG_TIME_AVG_TIME_OVER_THRESHOLD_THRESHOLD_PARAM_IDX];
	ringb *rb;
	int16_t val;
	int32_t start_index;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		int32_t irow;
		bool last = false;
		int32_t time_last_cross = 1;
		int32_t avg_cross_time_sum = 0;
		int32_t cross = 0;

		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		start_index = base_index & rb->mask;
		val = rb->buff[start_index++];

		if (val >= threshold)
		{
			last = true;
		}

		for (irow = 1; irow < kb_model->sg_length; irow++)
		{
			val = MOD_READ_RINGBUF(rb, start_index++);
			if (last)
			{
				if (val < threshold)
				{
					avg_cross_time_sum += time_last_cross;
					cross++;
					time_last_cross = 0;
					last = false;
				}
			}
			else
			{
				if (val >= threshold)
				{
					time_last_cross = 0;
					last = true;
				}
			}
			time_last_cross++;
		}

		if (cross > 0)
		{
			pFV[icol] = (FLOAT)(avg_cross_time_sum / cross);
		}
		else
		{
			pFV[icol] = 0.f;
		}
	}

	return cols_to_use->size;
}
