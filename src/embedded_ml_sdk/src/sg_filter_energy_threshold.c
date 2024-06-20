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
 * Return 0 if any of the data is outside the threshold range.
 * Return 1 if the segment isn't filtered out.
 */

static bool pass_threshold = false;
static bool pass_delay = false;
static int32_t counter = 0;

int32_t sg_filter_energy_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define SG_FILTER_ENERGY_THRESHOLD_NUM_PARAMS 3
#define THRESHOLD_PARAM_IDX 0
#define BACKOFF_PARAM_IDX 1
#define DELAY_PARAM_IDX 2

    // printf("pass_threshold %s\n", pass_threshold ? "true" : "false");
    // printf("pass_delay %s\n", pass_delay ? "true" : "false");
    // printf("counter %d\n", counter);

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != SG_FILTER_ENERGY_THRESHOLD_NUM_PARAMS)
    {
        return -1;
    }
#endif

    ringb *rb = kb_model->pdata_buffer->data + cols_to_use->data[0];
    int32_t base_index = kb_model->sg_index;
    int32_t threshold = (int32_t)params->data[THRESHOLD_PARAM_IDX];
    int32_t backoff = (int32_t)params->data[BACKOFF_PARAM_IDX];
    int32_t delay = (int32_t)params->data[DELAY_PARAM_IDX];

    if (pass_threshold == true)
    {
        if (pass_delay == true)
        {

            // if (buffer_pass_threshold(rb, base_index, 0, kb_model->sg_length, threshold))
            ///{
            //    counter=0;
            //}

            if (backoff <= counter)
            {
                counter = 0;
                pass_delay = false;
                pass_threshold = false;
                return 1;
            }
            counter++;
            return 1;
        }
        else
        {
            if (delay <= counter)
            {

                if (backoff == 0)
                {
                    pass_delay = 0;
                    pass_threshold = 0;
                    counter = 0;
                }
                else
                {
                    pass_delay = true;
                    counter = 1;
                }
                return 1;
            }
            counter++;
            return 0;
        }
    }
    pass_threshold = buffer_pass_threshold(rb, base_index, 0, kb_model->sg_length, threshold);

    if (pass_threshold && delay == 0)
    {
        if (backoff == 0)
        {
            pass_threshold = false;
            counter = 0;
            return 1;
        }
        pass_delay = true;
        counter = 1;
        return 1;
    }
    else if (pass_threshold)
    {
        counter++;
    }

    return 0;
}

void reset_sg_filter_energy_threshold()
{
    pass_threshold = false;
    pass_delay = false;
    counter = 0;
}