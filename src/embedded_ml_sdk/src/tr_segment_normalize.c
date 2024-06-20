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

int32_t tr_segment_normalize(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define TR_SEGMENT_NORMALIZE_NUM_PARAMS 1
#define TR_SEGMENT_NORMALIZE_TYPE_PARAM_IDX 0
    int32_t icol;
    ringb *rb;

    int32_t mode = (int32_t)params->data[TR_SEGMENT_NORMALIZE_TYPE_PARAM_IDX];

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != 1)
    {
        return 0;
    }
#endif

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        int16_t fm = 0;

        int32_t irow;
        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

        switch (mode)
        {
        case (0):
            fm = (int16_t)buffer_mean(rb, kb_model->sg_index, 0, kb_model->sg_length);
            break;
        case (1):
            fm = (int16_t)buffer_median(rb, kb_model->sg_index, kb_model->sg_length);
            break;
        case (2):
            fm = 0;
            break;
        case (3):
            fm = MOD_READ_RINGBUF(rb, kb_model->sg_index);
            break;
        default:
            break;
        }
        fm *= -1;

        if (fm != 0)
        {
            for (irow = 0; irow < kb_model->sg_length; irow++)
            {
                add_axis_data(rb, kb_model->sg_index + irow, fm);
            }
        }

        buffer_autoscale(rb, kb_model->sg_index, kb_model->sg_length);
    }
    return cols_to_use->size;
}
