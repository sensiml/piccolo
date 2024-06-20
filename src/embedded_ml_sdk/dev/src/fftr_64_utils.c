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




/**
 * \file fftr_utils.c
 * \brief wrapper functions for in-place 512 bin FFTR
 */

#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include "fftr_64_utils.h"
#include "fftr_64.h"
#include "kbutils.h"

#ifdef UTEST
// comment out the next line before committing:
// #define DBG_UTEST
#endif
#ifdef DBG_UTEST
#include <stdio.h>
#endif

// local params:
static uint8_t autoScale = false;
static uint8_t removeMean = false;

#ifdef DBG_UTEST

static void dump_data_int(int16_t *pData, int32_t len)
{
    int32_t idx;
    int32_t cnt = 0;

    for (idx = 0; idx < len; idx++)
    {
        printf("%5d, ", *pData++);
        cnt++;
        if ((cnt % 8) == 0)
        {
            printf("\n");
        }
    }
    if (len % 8)
    {
        printf("\n");
    }
}

static void dump_FFTR(int16_t *pData)
{
    int32_t idx;

    for (idx = 0; idx < NUM_FFTR_64; idx += 2)
    {
        printf("%5d, %5d\n", pData[idx], pData[idx + 1]);
    }
}
#endif

// The basic int16-based wrapper, applies Hanning window and calls FFTR_512():
struct compx_int16_t *fftr_64(int16_t *input_data, int32_t len)
{
    int32_t rShifts;
    int32_t idx;

    // check inputs:
    if ((!input_data) || (len < 8) || (len > NUM_FFTR_64))
    {
        return NULL;
    }

#ifdef DBG_UTEST
    printf("\nInput Data:\n");
    dump_data_int(input_data, len);
#endif

    // first, remove the mean
    if (removeMean)
    {
        remove_mean_data_int(input_data, len);
        removeMean = false;
#ifdef DBG_UTEST
        printf("\nDemeaned data:\n");
        dump_data_int(input_data, len);
#endif
    }

    // apply Hanning window
    apply_hanning_int(input_data, len);
#ifdef DBG_UTEST
    printf("\nHanning applied to Data:\n");
    dump_data_int(input_data, len);
#endif

    // handle auto-scaling
    if (autoScale)
    {
        autoscale_data_int(input_data, NUM_FFTR_64);
        autoScale = false;
#ifdef DBG_UTEST
        printf("\nAutoscaled data:\n");
        dump_data_int(input_data, len);
#endif
    }

    // if len < expected, zero pad at the end:
    if (len < NUM_FFTR_64)
    {
        for (idx = len; idx < NUM_FFTR_64; idx++)
        {
            input_data[idx] = 0;
        }
    }

    // get FFT (results returned in given buffer):
    rShifts = FFTR_64(input_data);
#ifdef DBG_UTEST
    printf("\nfftr results (rShifts = %d):\n", rShifts);
    dump_FFTR(input_data);
#else
    // ignore rShifts:
    (void)rShifts;
#endif

    // done!
    return ((struct compx_int16_t *)input_data);
}

// This applies Hanning and then auto-scales:
struct compx_int16_t *fftr_64_as(int16_t *input_data, int32_t len)
{
    struct compx_int16_t *pRet;

    autoScale = true;
    removeMean = false;
    pRet = fftr_64(input_data, len);
    return pRet;
}

// This removes the mean, applies Hanning, and then auto-scales:
struct compx_int16_t *fftr_64_rm_as(int16_t *input_data, int32_t len)
{
    struct compx_int16_t *pRet;

    autoScale = true;
    removeMean = true;
    pRet = fftr_64(input_data, len);
    return pRet;
}
