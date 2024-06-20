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

int32_t fg_interleave_signal(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_INTERLEAVE_SIGNAL_NUM_PARAMS 2
#define FG_INTERLEAVE_SIGNAL_CUTOFF_PARAM_IDX 0
#define FG_INTERLEAVE_SIGNAL_DELTA_PARAM_IDX 1

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || !pFV || params->size != FG_INTERLEAVE_SIGNAL_NUM_PARAMS)
    {
        return 0;
    }
#endif
    int32_t cutoff = params->data[FG_INTERLEAVE_SIGNAL_CUTOFF_PARAM_IDX];
    int32_t delta = params->data[FG_INTERLEAVE_SIGNAL_DELTA_PARAM_IDX];
    int32_t pad;

    ringb *rb;
    int32_t base_index = kb_model->sg_index;
    int32_t icol, irow;
    int32_t count = 0;
    int32_t start_index;

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        count = icol;
        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
        start_index = base_index & rb->mask;
        for (irow = 0; irow < cutoff; irow += delta)
        {
            pFV[count] = (FLOAT)rb->buff[start_index];
            start_index = (start_index + delta) & rb->mask;
            count += cols_to_use->size;
        }
    }

    // 0 PAD WHEN CUTOFF IS GREATER THAN SG_LENGTH

    if (kb_model->sg_length < cutoff)
    {
        pad = (cutoff - kb_model->sg_length) / delta;
    }
    else
    {
        pad = 0;
    }

    for (irow = 0; irow < pad; irow++)
    {
        for (icol = 0; icol < cols_to_use->size; icol++)
        {
            pFV[count++] = 0.0;
        }
    }

    return (cutoff / delta) * cols_to_use->size;
}
