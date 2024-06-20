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


// FILL_SENSIML_EMBEDDED_SDK

#include "kbalgorithms.h"

int32_t fg_amplitude_min_max_sum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
	int32_t icol;
	int32_t min, max;

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || params->size != 0 || !params || !pFV)
	{
		return 0;
	}
#endif

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		buffer_min_max(kb_model->pdata_buffer->data + cols_to_use->data[icol], kb_model->sg_index, kb_model->sg_length, 0, &min, &max);
		pFV[icol] = (FLOAT)(max + min);
	}

	return cols_to_use->size;
}