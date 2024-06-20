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
#include "kbutils.h"

#define NUM_PARAMS 0

int32_t fg_cross_column_median_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
    float median_1, median_2;

#if SML_DEBUG
    // Validate required inputs
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size != 2 || !pFV)
    {
        return 0;
    }
#endif

    median_1 = buffer_median(kb_model->pdata_buffer->data + cols_to_use->data[0], kb_model->sg_index, kb_model->sg_length);
    median_2 = buffer_median(kb_model->pdata_buffer->data + cols_to_use->data[1], kb_model->sg_index, kb_model->sg_length);

    *pFV++ = median_1 - median_2;

    return 1;
}
