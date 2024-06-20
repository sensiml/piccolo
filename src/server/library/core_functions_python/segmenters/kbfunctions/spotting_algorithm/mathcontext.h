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




#ifndef MATH_CONTEXT_H
#define MATH_CONTEXT_H
#include "common_algo.h"
#include <stdint.h>

#ifdef __cplusplus
extern "C"{
#endif /* __cplusplus */ 

    unsigned int int_sqrt(unsigned int squared);
    uint32_t int_cbrt(uint64_t cubic);

#define inline

    int m_sqrt(int x);

    static inline int m_abs(int x)
    {
        return (x) >= 0 ? (x) : (-(x));
    }

    int m_mean(int* buffer, int length);

    int m_var(int* data, int length);

    int m_std(int* data, int length);

    int m_max_min(int* buffer, int length, int* max, int* min);

    int m_norm_sq(int* buffer, int length);



#ifdef __cplusplus
}
#endif /* __cplusplus */



#endif
