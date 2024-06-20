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




#include "kbutils.h"
#include "fftr_64_utils.h"
// #include <stdio.h>

static FLOAT calc_spectral_entropy_64(int16_t *input_data, int32_t len)
{
	int32_t i;
	int32_t sum = 0;
	FLOAT entropy = 0.0f;
	FLOAT PSDval, P, logP;
	struct compx_int16_t *data;

	data = fftr_64_rm_as(input_data, len);

	// printf("val = [\n");

	for (i = 0; i < NUM_FFTR_64_CMPX; i++)
	{
		sum += data[i].real * data[i].real + data[i].imag * data[i].imag;

		//       printf("%d, ", data[i].real); //put in the value you want to look at here
	}
	// printf("]\n");
	if (sum == 0)
		sum = 1;

	for (i = 0; i < NUM_FFTR_64_CMPX; i++)
	{
		PSDval = (FLOAT)(data[i].real * data[i].real + data[i].imag * data[i].imag);
		P = PSDval / (FLOAT)sum;
		logP = log10(P + 1e-12);
		entropy += P * logP;
	}
	return -entropy;
}

int32_t spectral_entropy_64(kb_model_t *kb_model, int16_data_t *cols_to_use, FLOAT *params, int32_t num_params, FLOAT *pFV)
{
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || params->size != 0 || !params || !pFV)
	{
		return 0;
	}
	int32_t icol;
	ringb *rb;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		int32_t i;
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

		for (i = 0; i < kb_model->sg_length; i++)
		{
			sortedData[i] = get_axis_data(rb, kb_model->sg_index + i);
		}

		pFV[icol] = calc_spectral_entropy_64(sortedData, kb_model->sg_length);
	}

	return cols_to_use->size;
}
