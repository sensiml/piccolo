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

int32_t state_mean_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define STATE_MEAN_DIFFERENCE_NUM_PARAMS 2
#define STATE_MEAN_DIFFERENCE_THRESHOLD_PARAM_IDX 0
#define STATE_MEAN_DIFFERENCE_SPLIT_PARAM_IDX 1

    int32_t icol;
    int32_t diff = 0;
    int32_t threshold = 1000;
    int32_t split = 2;

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !pFV)
    {
        return 0;
    }

#endif

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        diff += abs(mean(kb_model->pdata_buffer->data + cols_to_use->data[icol], kb_model->sg_index, kb_model->sg_length / split) -
                    mean(kb_model->pdata_buffer->data + cols_to_use->data[icol], kb_model->sg_index + kb_model->sg_length / split, kb_model->sg_length / split));
    }
    if (diff > threshold)
    {
        pFV[icol] = (FLOAT)diff;
    }
    else
    {
        pFV[icol] = 0.0f;
    }

    return 1;
}
