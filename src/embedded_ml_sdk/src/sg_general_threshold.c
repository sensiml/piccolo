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

///
//
// General Trheshold Segmenter is a segmentation algorithm which follows the following algorithm.
// 1. Take input sample and add it to the ring buffer, increment segment_length counter by 1.
// 2. Check to see if the sg_length is equal to min_segment_length of samples.
// 3. Compute the threshold value in the selected threshold space for the threshhold width starting at position begin segment index
// 4. Check if the threshold value meets the user criteria if not decriment segment length and increment segment index. go back to step 1
// 5. If the threshold value meets the user criteria set the found segment start flag and go to step 6.
//
// 6. We are now searching for the end of the segment. Starting at position sg_length, which at first is min_segmnet_length.
// 7. check the threshold value from sg_length - threshold_width if it meets teh user criteria we have found the end of the segment.
// 8. If it doesn't, wait for another sample and check again
// 9. If the user gets max_segment_length samples before finding the end, call this the end of the segment.
//
// @params kb_model - pointer to the kb_model struct
// @param pSample - array of sensor data of a single point in time
// @param framelen - the len of pSample
// @columns - an array of column indexes (column[0] is the axis to use in the threshold space)
// @num_cols - the number of columns in cols
// @segParams - a data struct that contains parameters used by the segmenter.
//

static seg_params *pParams = NULL;

void general_threshold_segmenter_init(kb_model_t *kb_model, seg_params *segParams)
{
    kb_model->sg_index += kb_model->sg_length;
    kb_model->sg_length = 0;
}

int32_t general_threshold_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams)
{

    FLOAT segment_value = 0.0f;
    ringb *rb_locate_start = kb_model->pdata_buffer->data + columns->data[0];
    ringb *rb_locate_end = kb_model->pdata_buffer->data + columns->data[1];
    int32_t offset;

    // Increment the segment length because we have just added to the ring buffer
    kb_model->sg_length += 1;

    segParams->valid_segment_flag = 0;

    if (kb_model->sg_length >= segParams->min_segment_length)
    {
        if (segParams->searching_segment_flag == 0)
        {
            // There are several different threshold spaces that can be computed in, this allows a user to pick the one that separates their data the best
            switch (segParams->first_thresholding_space)
            {
            case (1):
                segment_value = buffer_standard_deviation(rb_locate_start, kb_model->sg_index, 0, segParams->threshold_space_width);
                break;
            case (2):
                segment_value = buffer_absolute_cumulative_sum(rb_locate_start, kb_model->sg_index, 0, segParams->threshold_space_width);
                break;
            case (3):
                segment_value = buffer_variance(rb_locate_start, kb_model->sg_index, 0, segParams->threshold_space_width);
                break;
            case (4):
                segment_value = buffer_absolute_cumulative_sum(rb_locate_start, kb_model->sg_index, 0, segParams->threshold_space_width);
                break;
            case (5):
                segment_value = buffer_absolute_mean(rb_locate_start, kb_model->sg_index, 0, segParams->threshold_space_width);
                break;
            case (6):
                segment_value = buffer_cumulative_sum(rb_locate_start, kb_model->sg_index, 0, segParams->threshold_space_width);
                break;
            }

            // Allow the user to set > or <
            switch (segParams->first_comparison)
            {
            case (1):
                if (segment_value >= segParams->first_vt_threshold)
                {
                    segParams->searching_segment_flag = 1;
                }
                else
                {
                    kb_model->sg_length -= 1;
                    kb_model->sg_index += 1;
                }
                break;
            case (2):
                if (segment_value <= segParams->first_vt_threshold)
                {
                    segParams->searching_segment_flag = 1;
                }
                else
                {
                    kb_model->sg_length -= 1;
                    kb_model->sg_index += 1;
                }
                break;
            }
        }
    }
    if (segParams->searching_segment_flag)
    {
        // There are several different threshold spaces that can be computed in, this allows a user to pick the one that separates their data the best
        offset = kb_model->sg_length - segParams->threshold_space_width;
        switch (segParams->second_thresholding_space)
        {
        case (1):
            segment_value = buffer_standard_deviation(rb_locate_end, kb_model->sg_index, offset, segParams->threshold_space_width);
            break;
        case (2):
            segment_value = buffer_absolute_cumulative_sum(rb_locate_end, kb_model->sg_index, offset, segParams->threshold_space_width);
            break;
        case (3):
            segment_value = buffer_variance(rb_locate_end, kb_model->sg_index, offset, segParams->threshold_space_width);
            break;
        case (4):
            segment_value = buffer_absolute_cumulative_sum(rb_locate_end, kb_model->sg_index, offset, segParams->threshold_space_width);
            break;
        case (5):
            segment_value = buffer_absolute_mean(rb_locate_end, kb_model->sg_index, offset, segParams->threshold_space_width);
            break;
        case (6):
            segment_value = buffer_cumulative_sum(rb_locate_end, kb_model->sg_index, offset, segParams->threshold_space_width);
            break;
        }

        // Allow the user to set > or <
        switch (segParams->second_comparison)
        {

        case (1):
            if (segment_value >= segParams->second_vt_threshold)
            {
                segParams->valid_segment_flag = 1;
            }
            break;
        case (2):
            if (segment_value <= segParams->second_vt_threshold)
            {
                segParams->valid_segment_flag = 1;
            }
            break;
        }
        // Once we get to max_segment_length we take teh segment regardless of finding the end
        if (kb_model->sg_length == segParams->max_segment_length)
        {
            segParams->valid_segment_flag = 1;
        }
    }
    if (segParams->valid_segment_flag)
    {
        segParams->searching_segment_flag = 0;
    }

    return (segParams->valid_segment_flag);
}
