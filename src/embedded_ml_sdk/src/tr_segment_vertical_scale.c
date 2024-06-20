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

// Initial unoptimized implemetnation
int32_t tr_segment_vertical_scale(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != 0)
    {
        return 0;
    }
#endif

    int32_t icol;
    ringb *rb;

    for (icol = 0; icol < cols_to_use->size; icol++)
    {

        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];

        buffer_autoscale(rb, kb_model->sg_index, kb_model->sg_length);
    }

    return cols_to_use->size;
}