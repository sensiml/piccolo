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
 * @brief LSUP Distance Calculation for uint8_t vectors
 *
 * @param[in]       *pSrcA points to the first input vector
 * @param[in]       *pSrcB points to the second input vector
 * @param[out]      *pDst points to an array that can hold the distances computed
 * @param[out]      *pDist points to the
 * @param[in]       blockSize number of samples in each vector
 * @return none.
 *
 * <b>Scaling and Overflow Behavior:</b>
 * \par
 * The function uses saturating arithmetic.
 * Results outside of the allowable Q7 range [0x80 0x7F] will be saturated.
 */

void lsup_distance(
    uint8_t *pSrcA,
    uint8_t *pSrcB,
    uint8_t *pDist,
    uint8_t *pMaxDist,
    uint32_t blockSize)
{
    uint32_t blkCnt; /* loop counter */

    /* Run the below code for Cortex-M4 and Cortex-M3 */

    /*loop Unrolling */
    blkCnt = blockSize;

    /* First part of the processing with loop unrolling.  Compute 4 outputs at a time.
     ** a second loop below computes the remaining 1 to 3 samples. */
    while (blkCnt > 0u)
    {
        /* C = |A - B| */
        /* Absolute Difference. */
        *pDist++ = (uint8_t)bitwise_absolute_value(*pSrcA++ - *pSrcB++);

        /* Decrement the loop counter */
        blkCnt--;
    }

    array_max_uint8(pDist - blockSize, blockSize, pMaxDist);
}
