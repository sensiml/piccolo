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




#ifndef _FFTR_128_H_
#define _FFTR_128_H_

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * \file fftr.h
 * \brief In-place 512 bin FFTR
 */

/**
 * \brief Calculates 128-bin in-place FFT
 *
 * \return applied number of right-shifts to fit 16-bit
 */
int32_t FFTR_128(int16_t *samples);

/**
 * Get the size of the ROM in Bytes.
 */
int32_t FFTR_128_GetRomSize128(void);

#ifdef __cplusplus
}
#endif

#endif  /* define FFTR_128_H_ */
