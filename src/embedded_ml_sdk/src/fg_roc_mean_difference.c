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

int32_t fg_roc_mean_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
	if (!kb_model || !cols_to_use || cols_to_use->size <= 0 || params->size != 0 || kb_model->sg_length <= 0 || !pFV)
	{
		return 0;
	}
#endif

	int32_t icol, i;
	FLOAT fSumTemp = 0.0, d1, d2;
	ringb *rb;
	int32_t start_index;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		start_index = kb_model->sg_index & rb->mask;
		d1 = rb->buff[start_index++];
		fSumTemp = 0;
		for (i = 1; i < kb_model->sg_length; i++)
		{
			d2 = MOD_READ_RINGBUF(rb, start_index++);
			fSumTemp += (d2 - d1);
			d1 = d2;
		}
		*pFV++ = (fSumTemp / (kb_model->sg_length - 1));
	}
	return cols_to_use->size;
}
