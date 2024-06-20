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




#include "kbutils.h"

void array_max_uint8(
    uint8_t *pSrc,
    uint32_t blockSize,
    uint8_t *pResult)
{
#ifndef ARM_MATH_CM0_FAMILY
    /* Run the below code for Cortex-M4 and Cortex-M3 */

    uint8_t maxVal1, maxVal2, out; /* Temporary variables to store the output value. */
    uint32_t blkCnt, count;        /* loop counter */

    /* Initialise the count value. */
    count = 0u;
    /* Load first input value that act as reference value for comparision */
    out = *pSrc++;

    /* Loop unrolling */
    blkCnt = (blockSize - 1u) >> 2u;

    /* Run the below code for Cortex-M4 and Cortex-M3 */
    while (blkCnt > 0u)
    {
        /* Initialize maxVal to the next consecutive values one by one */
        maxVal1 = *pSrc++;

        maxVal2 = *pSrc++;

        /* compare for the maximum value */
        if (out < maxVal1)
        {
            /* Update the maximum value and its index */
            out = maxVal1;
        }

        maxVal1 = *pSrc++;

        /* compare for the maximum value */
        if (out < maxVal2)
        {
            /* Update the maximum value and its index */
            out = maxVal2;
        }

        maxVal2 = *pSrc++;

        /* compare for the maximum value */
        if (out < maxVal1)
        {
            /* Update the maximum value and its index */
            out = maxVal1;
        }

        /* compare for the maximum value */
        if (out < maxVal2)
        {
            /* Update the maximum value and its index */
            out = maxVal2;
        }

        count += 4u;

        /* Decrement the loop counter */
        blkCnt--;
    }

    /* if (blockSize - 1u) is not multiple of 4 */
    blkCnt = (blockSize - 1u) % 4u;

#else

    /* Run the below code for Cortex-M0 */
    uint8_t maxVal1, out;      /* Temporary variables to store the output value. */
    uint32_t blkCnt, outIndex; /* loop counter */

    /* Initialise the index value to zero. */
    outIndex = 0u;
    /* Load first input value that act as reference value for comparision */
    out = *pSrc++;

    blkCnt = (blockSize - 1u);

#endif /* #ifndef ARM_MATH_CM0_FAMILY */

    while (blkCnt > 0u)
    {
        /* Initialize maxVal to the next consecutive values one by one */
        maxVal1 = *pSrc++;

        /* compare for the maximum value */
        if (out < maxVal1)
        {
            /* Update the maximum value and it's index */
            out = maxVal1;
        }
        /* Decrement the loop counter */
        blkCnt--;
    }

    /* Store the maximum value and its index into destination pointers */
    *pResult = out;
}