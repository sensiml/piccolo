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

#define NUM_PARAMS 1
#define SAMPLE_FREQUENCY_PARAM_IDX 0

int32_t fg_cross_column_correlation(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#if SML_DEBUG
    if (!kb_model || !cols_to_use || kb_model->sg_length <= 0 || cols_to_use->size <= 0 || params->size != NUM_PARAMS || !pFV)
    {
        *pFV++ = 0;
        return 0;
    }
#endif

    uint64_t sum = 0;
    int32_t sample_frequency = params->data[SAMPLE_FREQUENCY_PARAM_IDX];
    int32_t row, icol, slope_1, slope_2;
    int16_t y0_1, y1_1, y0_2, y1_2;
    ringb *rb1;
    ringb *rb2;
    int16_t data, max_value;
    int32_t start_index1, start_index2;

    rb1 = kb_model->pdata_buffer->data + cols_to_use->data[0];
    rb2 = kb_model->pdata_buffer->data + cols_to_use->data[1];
    start_index1 = kb_model->sg_index & rb1->mask;
    start_index2 = kb_model->sg_index & rb2->mask;

    for (row = 0; row < kb_model->sg_length - 1; row += sample_frequency)
    {
        y0_1 = rb1->buff[start_index1];
        y1_1 = rb1->buff[(start_index1 + 1) & rb1->mask];
        start_index1 = (start_index1 + sample_frequency) & rb1->mask;

        y0_2 = rb2->buff[start_index2];
        y1_2 = rb2->buff[(start_index2 + 1) & rb2->mask];
        start_index2 = (start_index2 + sample_frequency) & rb2->mask;

        slope_1 = y1_1 - y0_1;
        slope_2 = y1_2 - y0_2;

        if (slope_1 * slope_2 > 0)
        {
            sum += 1;
        }
    }

    *pFV++ = (FLOAT)((FLOAT)sum / kb_model->sg_length);

    return 1;
}
