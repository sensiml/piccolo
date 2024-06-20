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

int32_t fg_physical_variance_movement_intensity(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
	if (!kb_model || !cols_to_use || kb_model->sg_length <= 0 || cols_to_use->size <= 0 || params->size != 0 || !pFV)
	{
		return 0;
	}
#endif

	int32_t colndx, row;
	FLOAT AI, SumOfNorms = 0.0, SumOfVI, vival;
	int32_t num_rows = kb_model->sg_length; // kb_model->sg_length could be used throughout this function instead of setting num_rows here
	ringb *rb;

	for (row = 0; row < num_rows; row++)
	{
		FLOAT sumOfSquares = 0.0;
		for (colndx = 0; colndx < cols_to_use->size; colndx++)
		{
			rb = kb_model->pdata_buffer->data + cols_to_use->data[colndx];
			FLOAT fval = MOD_READ_RINGBUF(rb, (row + kb_model->sg_index));

			// Compute sum of norms from the columns data for each row
			sumOfSquares += fval * fval;
		}
		SumOfNorms += SQRT(sumOfSquares);
	}
	// Compute average intensity
	AI = SumOfNorms / num_rows;

	SumOfVI = 0.0;

	// Now compute the Variance Intensity
	// First sum the all the (norm[i]-AI)**2
	for (row = 0; row < num_rows; row++)
	{
		FLOAT sumOfSquares = 0.0;

		for (colndx = 0; colndx < cols_to_use->size; colndx++)
		{
			rb = kb_model->pdata_buffer->data + cols_to_use->data[colndx];
			FLOAT fval = MOD_READ_RINGBUF(rb, (row + kb_model->sg_index));

			// Compute sum of norms from the columns data for each row
			sumOfSquares += fval * fval;
		}
		vival = SQRT(sumOfSquares) - AI;
		SumOfVI += (vival * vival);
	}
	*pFV = SumOfVI / num_rows;
	return 1;
}
