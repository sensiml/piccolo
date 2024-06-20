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

void PreEmphasis(ringb *rb, int32_t base_index, int16_t window_size, int32_t pre_emphasis_factor, int32_t pre_emphasis_prior)
{
    /* Signal is shifted right by 1 to avoid overflow */
    int32_t prior = pre_emphasis_prior;
    int32_t i;
    int32_t start_index = base_index & rb->mask;

    for (i = 0; i < window_size; i++)
    {
        int32_t sample = (int32_t)rb->buff[start_index];
        rb->buff[start_index] = (int16_t)(((sample << 15) - (prior * pre_emphasis_factor)) >> 16);
        start_index = (start_index + 1) & rb->mask;
        prior = sample;
    }

    // pre_emphasis_prior = prior;
    // return pre_emphasis_prior;
    // prior design need to be revisited
}

/**
 * For each sample set (column) subtract the set mean/min from the samples.
 *
 * Inputs:
 *         num_rows - number of frames in the input_data array
 *         cols_to_use - array of columns to process
 *         num_cols - number of elements in cols
 *
 * Outputs: Returns num_cols if successful, 0 otherwise.
 *         Modifies the data in input_data (original data is lost)
 */
int32_t tr_segment_pre_emphasis_filter(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define TR_PRE_EMPHASIS_FILTER_NUM_PARAMS 2
#define TR_PRE_EMPHASIS_FILTER_ALPHA_PARAM_IDX 0
#define TR_PRE_EMPHASIS_FILTER_PRIOR_PARAM_IDX 1

    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != TR_PRE_EMPHASIS_FILTER_NUM_PARAMS)
        return 0;

    // Converting the alpha factor to Q.15
    int32_t pre_emphasis_factor = (int32_t)(params->data[TR_PRE_EMPHASIS_FILTER_ALPHA_PARAM_IDX] * 32768.0f);

    // user should always set this to zero
    int32_t prior = (int32_t)params->data[TR_PRE_EMPHASIS_FILTER_PRIOR_PARAM_IDX];

    int32_t icol;

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        int32_t col = cols_to_use->data[icol];

        PreEmphasis(kb_model->pdata_buffer->data + col,
                    kb_model->sg_index,
                    kb_model->sg_length,
                    pre_emphasis_factor,
                    prior);
    }
    return cols_to_use->size;
}
