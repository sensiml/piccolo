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
#include "fftr_utils.h"
// #include <stdio.h>
//  This function is giving different results

static FLOAT calc_spectral_entropy(int16_t *input_data, int32_t len)
{
	int32_t i;
	FLOAT sum = 0.0f;
	FLOAT entropy = 0.0f;
	FLOAT PSDval, P, logP;
	struct compx_int16_t *data;

	data = fftr(input_data, len);

	// printf("val = [\n");

	for (i = 0; i < NUM_FFTR_CMPX; i++)
	{
		sum += (FLOAT)(data[i].real * data[i].real + data[i].imag * data[i].imag);

		//       printf("%d, ", data[i].real); //put in the value you want to look at here
	}
	// printf("]\n");

	if (sum == 0)
	{
		return 0;
	}

	for (i = 0; i < NUM_FFTR_CMPX; i++)
	{
		PSDval = (FLOAT)(data[i].real * data[i].real + data[i].imag * data[i].imag);
		P = PSDval / sum;
		logP = log10(P + 1e-12);
		entropy += P * logP;
	}
	return -entropy;
}

int32_t fg_frequency_spectral_entropy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || params->size != 0 || !params || !pFV)
	{
		return 0;
	}
#endif

	int32_t icol;
	ringb *rb;
	int32_t len = 0;
	int32_t start_index;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		int32_t i;
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
		start_index = kb_model->sg_index;
		if (kb_model->sg_length > NUM_FFTR)
		{
			len = NUM_FFTR;
		}
		else
		{
			len = kb_model->sg_length;
		}

		for (i = 0; i < len; i++)
		{
			sortedData[i] = MOD_READ_RINGBUF(rb, start_index++);
		}

		pFV[icol] = calc_spectral_entropy(sortedData, len);
	}

	return cols_to_use->size;
}
