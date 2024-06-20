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

int32_t fg_stats_variance(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
	FLOAT mean = 0.0;
	FLOAT M2 = 0.0;
	int32_t irow, icol, base_index, num_rows;
	FLOAT delta, datapoint;
	ringb *rb;
	int32_t start_index;
	base_index = kb_model->sg_index;
	num_rows = kb_model->sg_length;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		start_index = base_index;
		short n = 0;

		for (irow = 0; irow < num_rows; irow++)
		{
			n++;
			datapoint = MOD_READ_RINGBUF(rb, start_index++);
			delta = datapoint - mean;
			mean += delta / n;
			M2 += delta * (datapoint - mean);
		}
		if (n < 2)
		{
			pFV[icol] = 0;
		}
		else
		{
			pFV[icol] = M2 / (n - 1);
		}
	}
	return cols_to_use->size;
}
