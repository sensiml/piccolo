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

int32_t fg_sampling_downsample_max_with_normalization(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_SAMPLING_DOWNSAMPLE_MAX_WITH_NORMALIZATION_NUM_PARAMS 1
#define FG_SAMPLING_DOWNSAMPLE_MAX_WITH_NORMALIZATION_NEW_LENGTH_PARAM_IDX 0

#if SML_DEBUG
    if (!kb_model ||
        kb_model->sg_length <= 0 ||
        !cols_to_use ||
        cols_to_use->size <= 0 ||
        !params ||
        !pFV ||
        params->size != FG_SAMPLING_DOWNSAMPLE_MAX_WITH_NORMALIZATION_NUM_PARAMS)
    {
        return 0;
    }
#endif

    int32_t iseg;
    ringb *rb;
    int32_t base_index = kb_model->sg_index;
    int32_t numsegs = (int32_t)params->data[FG_SAMPLING_DOWNSAMPLE_MAX_WITH_NORMALIZATION_NEW_LENGTH_PARAM_IDX];
    int32_t nspseg = kb_model->sg_length / numsegs;

    rb = kb_model->pdata_buffer->data + cols_to_use->data[0];

    for (iseg = 0; iseg < numsegs; iseg++)
    {
        sortedData[iseg] = (int16_t)buffer_max(rb, base_index, iseg * nspseg, nspseg);
    }

    int32_t min = KB_SHORT_INT_MAX;
    int32_t max = KB_SHORT_INT_MIN;
    for (iseg = 0; iseg < numsegs; iseg++)
    {
        if (sortedData[iseg] < min)
        {
            min = sortedData[iseg];
        }
        else if (sortedData[iseg] > max)
        {
            max = sortedData[iseg];
        }
    }

    float delta = (float)(max - min);
    float scale_factor = 0.0f;
    if (delta != 0.0f)
    {
        scale_factor = 255.0f / delta;
    }

    for (iseg = 0; iseg < numsegs; iseg++)
    {
        *pFV++ = (float)(sortedData[iseg] - min) * scale_factor;
    }

    return numsegs;
}
