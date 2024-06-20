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

/***
 * Divide samples into num segments, compute the mean of each segment.
 *
 * Inputs:
 *         num_rows - total number of frames.
 *         cols_to_use - array of offsets into the sensor frame of data to be downsampled.
 *         num_cols - size of cols array.
 *		  params - array of function parameters.
 *		  num_params - count of function parameters.
 *         pFV -        Pointer to the next location in feature vector to be filled.
 *
 * Outputs: pFV[0]-pFV[num_cols] - downsampled feature vectors
 *
 * Returns: num_cols if successful.
 */
int32_t fg_sampling_downsample(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_SAMPLING_DOWNSAMPLE_NUM_PARAMS 1
#define FG_SAMPLING_DOWNSAMPLE_NEW_LENGTH_PARAM_IDX 0

#if SML_DEBUG
	if (!kb_model ||
		kb_model->sg_length <= 0 ||
		!cols_to_use ||
		cols_to_use->size <= 0 ||
		!params ||
		!pFV ||
		params->size != FG_SAMPLING_DOWNSAMPLE_NUM_PARAMS)
	{
		return 0;
	}
#endif

	int32_t icol;
	int32_t iseg;
	ringb *rb;
	int32_t base_index = kb_model->sg_index;

	int32_t numsegs = (int32_t)params->data[FG_SAMPLING_DOWNSAMPLE_NEW_LENGTH_PARAM_IDX];
	int32_t nspseg = kb_model->sg_length / numsegs;

	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

		for (iseg = 0; iseg < numsegs; iseg++)
		{
			*pFV++ = mean(rb, base_index + iseg * nspseg, nspseg);
		}
	}

	return cols_to_use->size * numsegs;
}
