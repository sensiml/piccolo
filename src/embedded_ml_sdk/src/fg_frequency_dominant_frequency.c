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
#include "fftr_utils.h"

#define NUM_PARAMS 1
#define SAMPLE_RATE_PARAM_IDX 0

static FLOAT calc_dominant_frequency(int16_t *input_data, int32_t len, FLOAT fs)
{
    int32_t i;
    struct compx_int16_t *data;

    data = fftr_rm_as(input_data, len);

    int32_t max = 0;
    int32_t ndx = 0;
    int32_t val;
    for (i = 1; i < NUM_FFTR_CMPX; i++)
    {

        val = (abs(data[i].real) + abs(data[i].imag));
        if (val > max)
        {
            max = val;
            ndx = i;
        }
    }

    return (FLOAT)(ndx * fs / len);
}

int32_t fg_frequency_dominant_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

    int32_t icol;
    int32_t len;
    ringb *rb;
    int32_t start_index;

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || params->size != NUM_PARAMS || !params || !pFV)
    {
        return 0;
    }
#endif

    FLOAT sample_rate = params->data[SAMPLE_RATE_PARAM_IDX];

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        int32_t i;
        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
        start_index = kb_model->sg_index;
        if (kb_model->sg_length > NUM_FFTR)
        {
            len = NUM_FFTR;
        }
        else
        {
            len = kb_model->sg_length;
        }

        for (i = 0; i < len; i++)
        {
            sortedData[i] = MOD_READ_RINGBUF(rb, start_index++);
        }

        pFV[icol] = calc_dominant_frequency(sortedData, kb_model->sg_length, sample_rate);
    }

    return cols_to_use->size;
}
