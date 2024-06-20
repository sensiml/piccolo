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

static seg_params *pParams = NULL;

// This segmenter resets by flushing the ring buffer
//
// @params pringb - pointer to an array of ringbuffers
// @params num_rb - the number of ring buffers to flush on reset
//
void windowing_threshold_segmenter_init(kb_model_t *kb_model, seg_params *segParams)
{

    kb_model->sg_index += kb_model->sg_length;
    kb_model->sg_length = 0;
}
///
//
// Windowing threshold segmenter is a segmentation algorithm which follows the following algorithm.
// 1. Take input sample and add it to the ring buffer.
// 2. Check to see if the ringbuffer has filled up with window_size of samples.
// 3. Compute the threshold value in the selected threshold space for the threshold_width size from the start of the window + offset
// 4. If the value is less slide take another sample and recomupte the threshold space value at window + offset and return -1
// 5. If the threshold value is larger than the specified threshold in segparams take it as a segment and return 1.
//
// @params kb_model - pointer to the kb_model struct
// @param pSample - array of sensor data of a single point in time
// @param framelen - the len of pSample
// @columns - an array of column indexes (column[0] is the axis to use in the threshold space)
// @num_cols - the number of columns in cols
// @segParams - a data struct that contains parameters used by the segmenter.
//

int32_t windowing_threshold_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams)
{

    int32_t segment_value = 0;
    ringb *rb = kb_model->pdata_buffer->data + columns->data[0];

    kb_model->sg_length += 1;

    if (kb_model->sg_length == segParams->window_size)
    {
        // the offset is the position in the ring buffer we want to check for being above the threshold

        switch (segParams->thresholding_space)
        {
        case (1):
            segment_value = buffer_standard_deviation(rb, kb_model->sg_index, segParams->offset, segParams->threshold_space_width);
            break;
        case (2):
            segment_value = buffer_absolute_cumulative_sum(rb, kb_model->sg_index, segParams->offset, segParams->threshold_space_width);
            break;
        case (3):
            segment_value = buffer_variance(rb, kb_model->sg_index, segParams->offset, segParams->threshold_space_width);
            break;
        case (4):
            segment_value = buffer_absolute_cumulative_sum(rb, kb_model->sg_index, segParams->offset, segParams->threshold_space_width);
            break;
        case (5):
            segment_value = buffer_absolute_mean(rb, kb_model->sg_index, segParams->offset, segParams->threshold_space_width);
            break;
        case (6):
            segment_value = buffer_cumulative_sum(rb, kb_model->sg_index, segParams->offset, segParams->threshold_space_width);
            break;
        }

        // Still at beginning of segment
        switch (segParams->comparison)
        {
        case (0):
            if (segment_value >= segParams->vt_threshold)
            {
                // When our ring buffer changes to a head tail paradigm this will have to be updated used again
                // rb_truncate(pringb, 0, framelen, rb_items(pringb + 0) - segParams->window_size, segParams->window_size);
                return 1;
            }
            break;
        case (1):
            if (segment_value <= segParams->vt_threshold)
            {
                // When our ring buffer changes to a head tail paradigm this will have to be updated used again
                // rb_truncate(pringb, 0, framelen, rb_items(pringb + 0) - segParams->window_size, segParams->window_size);
                return 1;
            }
        }

        kb_model->sg_index += 1;
        kb_model->sg_length -= 1;
    }
    return 0;
}