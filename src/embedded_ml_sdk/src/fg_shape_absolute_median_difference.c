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

int32_t fg_shape_absolute_median_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define FG_SHAPE_ABSOLUTE_MEDIAN_DIFFERENCE_NUM_PARAMS 1
#define FG_SHAPE_ABSOLUTE_MEDIAN_DIFFERENCE_CENTER_RATIO_PARAM_IDX 0

#if SML_DEBUG
    if (!kb_model || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != 1 || kb_model->sg_length <= 0 || !pFV)
    {
        return 0;
    }
#endif // SML_DEBUG

    int32_t icol;
    FLOAT secondhalf, firsthalf;
    float center_ratio = params->data[FG_SHAPE_ABSOLUTE_MEDIAN_DIFFERENCE_CENTER_RATIO_PARAM_IDX];

    int32_t center_point = (int32_t)kb_model->sg_length * center_ratio;
    int32_t final_index = kb_model->sg_length - center_point;

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        firsthalf = buffer_median(kb_model->pdata_buffer->data + cols_to_use->data[icol], kb_model->sg_index, center_point);
        secondhalf = buffer_median(kb_model->pdata_buffer->data + cols_to_use->data[icol], kb_model->sg_index + center_point, final_index);

        *pFV++ = fabs(firsthalf - secondhalf);
    }
    return cols_to_use->size;
}
