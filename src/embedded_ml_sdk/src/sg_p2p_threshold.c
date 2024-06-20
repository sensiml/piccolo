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

/*
 *
 * Returns: 1 if a segment was detected and stored, 0 otherwise.
 *
 */

enum segmenter_state
{
    TS_0QUIET,
    TS_1SEARCHING,
    TS_RECOG
};

int32_t p2p_threshold(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams)
{
    int16_t value;

    ringb *rb;

    switch (segParams->seg_state)
    {
    case TS_0QUIET: // Wait for quiescence, then start searching for start again.
        kb_model->sg_length++;
        if (kb_model->sg_length > segParams->min_segment_length)
        {
            segParams->seg_state = TS_1SEARCHING;
        }
        break;
    case TS_1SEARCHING: // Wait for activity above threshold, record start time, and

        for (int32_t i = 0; i < columns->size; i++)
        {
            rb = kb_model->pdata_buffer->data + columns->data[i];
            value = rb->buff[(kb_model->sg_index + kb_model->sg_length) & rb->mask];
            if (segParams->absolute_value)
            {
                value = abs(value);
            }
            if (value > segParams->max_value)
            {
                segParams->max_value = value;
                segParams->max_index = kb_model->sg_length + 1;
            }
        }
        kb_model->sg_length++;
        if (kb_model->sg_length >= segParams->max_segment_length)
        {
            if (segParams->max_value > segParams->threshold)
            {
                kb_model->sg_length = segParams->max_index;
            }
            else
            {
                kb_model->sg_length = segParams->min_segment_length;
            }
            segParams->seg_state = TS_RECOG;

            return 1;
        }
        break;

    case TS_RECOG: // Send sensor data to recognizer
        return 1;
        break;
    }

    return 0;
}

void p2p_threshold_init(kb_model_t *kb_model, seg_params *segParams)
{
    kb_model->sg_index += kb_model->sg_length;
    kb_model->sg_length = 0;
    kb_model->last_read_idx = kb_model->sg_index;
    segParams->seg_state = TS_0QUIET;
    segParams->max_value = KB_SHORT_INT_MIN;
}
