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




#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include "kbutils.h"
#include "imfcc.h"
#include "imfcc_rom.h"
#include "kbalgorithms.h"

int32_t fg_frequency_mfcc(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{

#define FG_MFCC_NUM_PARAMS 2
#define FG_MFCC_SAMPLE_RATE_PARAM_IDX 0
#define FG_MFCC_CEPSTRA_COUNT_PARAM_IDX 1

    int32_t icol, irow, i, len;
    ringb *rb;
    int32_t start_index;

#if SML_DEBUG
    // we dont need frame shift because it will be taken care by windowing segmenter
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != FG_MFCC_NUM_PARAMS || !pFV)
        return 0;
#endif

    // num_cols has to be 1 else prior will be corrupted. design of pre_emphasis_prior need to be revisited
    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
        start_index = kb_model->sg_index & rb->mask;
        if (kb_model->sg_length > 512)
        {
            len = 512;
        }
        else
        {
            len = kb_model->sg_length;
        }

        for (irow = 0; irow < len; irow++)
        {
            sortedData[irow] = MOD_READ_RINGBUF(rb, start_index++);
            // printf("sortedData[%3d]: %10d\n", irow, sortedData[irow]);
        }

        IMFCC_ProcessFrame((int16_t *)sortedData,
                           512,
                           len,
                           (int32_t)params->data[FG_MFCC_CEPSTRA_COUNT_PARAM_IDX]);

        // at this point, the tempbuff is overwritten with dct_outputs in int32, which the feature we need
        int32_t *mfcc = (int32_t *)sortedData;

        for (i = 0; i < params->data[FG_MFCC_CEPSTRA_COUNT_PARAM_IDX]; i++)
        {
            *pFV++ = (FLOAT)mfcc[i];
        }
    }

    // return the first nth coefficient
    return params->data[FG_MFCC_CEPSTRA_COUNT_PARAM_IDX];
}
