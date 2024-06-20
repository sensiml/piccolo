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

int32_t fg_fixed_width_histogram(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_FIXED_WIDTH_HISTOGRAM_NUM_PARAMS 4
#define FG_FIXED_WIDTH_HISTOGRAM_NUMBER_OF_BINS_PARAM_IDX 0
#define FG_FIXED_WIDTH_HISTOGRAM_RANGE_LEFT_PARAM_IDX 1
#define FG_FIXED_WIDTH_HISTOGRAM_RANGE_RIGHT_PARAM_IDX 2
#define FG_FIXED_WIDTH_HISTOGRAM_SCALING_FACTOR_PARAM_IDX 3

#if SML_DEBUG
	if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != FG_FIXED_WIDTH_HISTOGRAM_NUM_PARAMS || !pFV)
	{
		return 0;
	}
#endif

	int32_t i;
	int32_t num_bins;
	float min_range;
	float max_range;
	int32_t scaling_factor;
	int32_t icol;
	int32_t row;
	int32_t bin;
	int32_t val;
	float width;
	ringb *rb;
	int32_t start_index;

	num_bins = (int32_t)params->data[FG_FIXED_WIDTH_HISTOGRAM_NUMBER_OF_BINS_PARAM_IDX];
	min_range = (int32_t)params->data[FG_FIXED_WIDTH_HISTOGRAM_RANGE_LEFT_PARAM_IDX];
	max_range = (int32_t)params->data[FG_FIXED_WIDTH_HISTOGRAM_RANGE_RIGHT_PARAM_IDX];
	scaling_factor = (int32_t)params->data[FG_FIXED_WIDTH_HISTOGRAM_SCALING_FACTOR_PARAM_IDX];

	if (num_bins <= 0 || min_range >= max_range || !scaling_factor)
	{
		return 0;
	}

	// reset the sortedData array
	memset(sortedData, 0, sizeof(int16_t) * num_bins);

	width = ABS(max_range - min_range) / num_bins;

	// Error check TBD: Ensure total input buffer size is smaller then the maximum int32_t value otherwise bin will overflow
	// This check has to be there in the KB cloud side tool as well
	// Histogram computation
	for (icol = 0; icol < cols_to_use->size; icol++)
	{
		rb = kb_model->pdata_buffer->data + cols_to_use->data[icol]; // Combined histogram of input axis of the data
		start_index = kb_model->sg_index;
		for (row = 0; row < kb_model->sg_length; row++) // Histogram of each axis
		{
			val = MOD_READ_RINGBUF(rb, start_index++);
			bin = (int32_t)((val - min_range) / width);
			if (bin >= 0 && bin < num_bins)
			{
				sortedData[bin]++;
			}
		}
	}

	for (i = 0; i < num_bins; i++)
	{
		pFV[i] = (FLOAT)sortedData[i];
	}

	// Scale histogram feature vector between 0-255
	for (bin = 0; bin < num_bins; bin++) // Scan each bin range
	{
		pFV[bin] = pFV[bin] / (cols_to_use->size * kb_model->sg_length) * (scaling_factor);
		pFV[bin] = (float)((int32_t)(pFV[bin] + 0.5f));
	}

	return num_bins; /* return the number of feature vectors generated */
}
