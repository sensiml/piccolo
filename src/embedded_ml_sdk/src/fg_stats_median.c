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
#include "kb_defines.h"

FLOAT get_median(int16_t *sorted, int32_t n, int32_t column)
{
    FLOAT fret;

    int32_t mid_index = n >> 1; // mid_index = n/2 where n is number of samples

    if (n & 1) // if n is odd, return the element in the middle
    {
        fret = (FLOAT)sorted[mid_index];
    }
    else // if there is an even number of elements, return mean of the two elements in the middle
    {
        fret = ((sorted[mid_index] + sorted[mid_index - 1]) / 2.0);
    }
    return fret;
}

int32_t fg_stats_median(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
    FLOAT median;
    int32_t icol;
    int16_t *pdata;

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !pFV)
        return 0;
#endif

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        pdata = sorted_copy(kb_model->pdata_buffer->data + cols_to_use->data[icol], kb_model->sg_index, kb_model->sg_length, 0);
        if (pdata)
        {
            median = get_median(pdata, kb_model->sg_length, 0);
            pFV[icol] = median;
        }
        else
        {
            break;
        }
    }
    return cols_to_use->size;
}
