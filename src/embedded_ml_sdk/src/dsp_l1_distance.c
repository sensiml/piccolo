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




#include "kb_opt.h"

/**
 * @brief L1 Distance Calculation for uint8_t vectors
 *
 * @param[in]       *pSrcA points to the first input vector
 * @param[in]       *pSrcB points to the second input vector
 * @param[out]      *pDst points to output distance
 * @param[in]       blockSize number of samples in each vector
 * @return none.
 *
 * <b>Scaling and Overflow Behavior:</b>
 * \par
 * The function uses saturating arithmetic.
 * Results outside of the allowable Q7 range [0x80 0x7F] will be saturated.
 */

void l1_distance(
    uint8_t *pSrcA,
    uint8_t *pSrcB,
    uint32_t *pDist,
    uint32_t blockSize)
{
    uint32_t blkCnt; /* loop counter */
    uint32_t sum = 0;

#ifdef OPT_ARM_M4_DSP

    /* Run the below code for Cortex-M4 and Cortex-M3 */

    /*loop Unrolling */
    blkCnt = blockSize >> 2u;

    /* First part of the processing with loop unrolling.  Compute 4 outputs at a time.
     ** a second loop below computes the remaining 1 to 3 samples. */
    while (blkCnt > 0u)
    {
        /* C = A - B */
        /* Subtract and then store the results in the destination buffer 4 samples at a time. */
        sum = __USADA8(*__SIMD32(pSrcA)++, *__SIMD32(pSrcB)++, sum);

        /* Decrement the loop counter */
        blkCnt--;
    }

    /* If the blockSize is not a multiple of 4, compute any remaining output samples here.
     ** No loop unrolling is used. */
    blkCnt = blockSize % 0x4u;

    while (blkCnt > 0u)
    {
        /* C = A - B */
        /* Subtract and then store the result in the destination buffer. */
        sum += bitwise_absolute_value(*pSrcA++ - *pSrcB++);

        /* Decrement the loop counter */
        blkCnt--;
    }

#else

    /* Run the below code for Cortex-M0 */

    /* Initialize blkCnt with number of samples */
    blkCnt = blockSize;

    while (blkCnt > 0u)
    {
        /* C = A - B */
        /* Subtract and then store the result in the destination buffer. */
        sum += bitwise_absolute_value(*pSrcA++ - *pSrcB++);

        /* Decrement the loop counter */
        blkCnt--;
    }

#endif /* #ifndef ARM_MATH_CM0_FAMILY */

    *pDist = sum;
}
