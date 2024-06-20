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

#ifndef __KB_OPT_H__
#define __KB_OPT_H__

#include <stdint.h>
#include <limits.h>
// clang-format off
#ifdef OPT_ARM_M4_DSP
#if defined(__arm__)        
    #include "cmsis_armcc.h"
#elif defined(__GNUC__)
    #include "cmsis_gcc.h"
#else
#include "arm_math.h"
#endif
#endif
// clang-format on

#include "kbutils.h"

#ifdef __cplusplus
extern "C"
{
#endif

    void lsup_distance(uint8_t *pSrcA, uint8_t *pSrcB, uint8_t *pDist, uint8_t *pMaxDist, uint32_t blockSize);
    void l1_distance(uint8_t *pSrcA, uint8_t *pSrcB, uint32_t *pDist, uint32_t blockSize);
    void compute_distance_matrix(unsigned char *x, unsigned char *y, int32_t x_size, int32_t y_size, uint8_t num_channels);
    int32_t compute_warping_distance(int32_t x_size, int32_t y_size);
    int32_t get_distance_matrix_value(int32_t i, int32_t j);
    int32_t get_globdist(int32_t i, int32_t j);

#ifdef __cplusplus
}
#endif
// clang-format on

#endif //__KB_OPT_H__
