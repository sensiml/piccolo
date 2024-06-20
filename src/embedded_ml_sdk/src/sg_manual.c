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
 * seg_windowing
 *
 */
int32_t sg_manual(kb_model_t *model, int16_data_t *columns, seg_params *segParams)
{

    if (model->sg_length <= segParams->window_size)
    {
        model->sg_length += 1;
        return 0;
    }

    return 1;
}

void sg_manual_init(kb_model_t *model, seg_params *segParams)
{
    model->sg_index += model->sg_length;
    model->sg_length = 0;

    return;
}
