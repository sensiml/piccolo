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

enum twist_states
{
	TS_0QUIET,
	TS_1SEARCHING,
	TS_1TWIST,
	TS_2SEARCHING,
	TS_2TWIST,
	TS_RECORDING,
	TS_RECOG
};

int32_t double_peak_key_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams)
{
	int16_t value;

	ringb *rb = kb_model->pdata_buffer->data + columns->data[0];

	value = rb->buff[(kb_model->sg_index + kb_model->sg_length) & rb->mask];

	switch (segParams->ts_state)
	{
	case TS_0QUIET: // Wait for quiescence, then start searching for start again.
		if (value > segParams->twist_threshold)
		{
			segParams->ts_state = TS_1SEARCHING;
		}
		kb_model->sg_index += 1;
		break;

	case TS_1SEARCHING:							// Wait for activity above threshold, record start time, and
		if (value < segParams->twist_threshold) //  move to '1-twist detected' state.
		{
			segParams->ts_state = TS_1TWIST;
			segParams->lasttwist = kb_model->sg_index;
		}
		kb_model->sg_index += 1;
		break;

	case TS_1TWIST: // Wait for end of first twist
		if (value > segParams->end_twist_threshold)
		{
			segParams->ts_state = TS_2SEARCHING;
		}

		// check if we should reset segment state
		else if ((kb_model->sg_index - segParams->lasttwist) > segParams->max_peak_to_peak)
		{
			segParams->ts_state = TS_0QUIET;
		}

		kb_model->sg_index += 1;
		break;

	case TS_2SEARCHING: // Wait for start of 2nd twist
		if (value < segParams->twist_threshold)
		{
			segParams->ts_state = TS_2TWIST;

			if ((kb_model->sg_index - segParams->lasttwist) < segParams->min_peak_to_peak)
			{
				segParams->ts_state = TS_0QUIET;
			}
		}

		// check if we should reset segmenter state
		else if ((kb_model->sg_index - segParams->lasttwist) > segParams->max_peak_to_peak)
		{
			segParams->ts_state = TS_0QUIET;
		}

		kb_model->sg_index += 1;
		break;

	case TS_2TWIST: // Wait until the end of the 2nd twist
		if (value > segParams->end_twist_threshold)
		{
			segParams->ts_state = TS_RECORDING;
		}
		if ((kb_model->sg_index - segParams->lasttwist) > 4 * segParams->min_peak_to_peak)
		{
			segParams->ts_state = TS_0QUIET;
		}
		kb_model->sg_index += 1;
		break;

	case TS_RECORDING: // Collect the sensor data for the feature generators.
		kb_model->sg_length += 1;
		if (kb_model->sg_length > segParams->max_segment_length)
		{
			segParams->ts_state = TS_0QUIET;
			kb_model->sg_index += kb_model->sg_length;
			kb_model->sg_length = 0;
			segParams->lasttwist = 0;
			break;
		}
		if (value < segParams->last_twist_threshold) // Keep collecting until the peak is found (exclude peak value.)
		{
			segParams->ts_state = TS_RECOG;
			return 1;
		}
		break;

	case TS_RECOG: // Send sensor data to recognizer
		return 1;
		break;
	}

	return 0;
}

void double_peak_key_segmenter_init(kb_model_t *kb_model, seg_params *segParams)
{
	kb_model->sg_index += kb_model->sg_length;
	kb_model->sg_length = 0;
	segParams->ts_state = TS_0QUIET;
	segParams->lasttwist = 0;
}
