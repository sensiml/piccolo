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
 * \file fftr_utils.h
 * \brief utility functions for using in-place 512 bin FFTR
 */

#ifndef _FFTR_UTILS_H_
#define _FFTR_UTILS_H_

#include "kb_typedefs.h" // struct compx

// for unit testing with C++ framework:
#ifdef __cplusplus
extern "C"
{
#endif

// number of floats expected:
#define NUM_FFTR (512)
#define NUM_FFTR_CMPX (256)

    // FLOAT-based and int16-based wrappers for FFTR_512()
    //
    // params:
    // -- <input_data> ... points to a buffer containing up to 512 FLOAT values
    //    Because this buffer is re-used to return results, it must be large
    //    enough to hold 512 FLOAT values.
    // -- <len> ... FFT length, must be <= 512 and must be a multiple of 2;
    //    input data will be padded out to a len of 512 by adding zeroes.
    //
    // return:
    // -- on success ... pointer to 256 compx structs, each containing a FLOAT real and a FLOAT imaginary;
    //                   actually, just a cast of the pointer to the buffer containing the input data.
    // -- otherwise .... NULL, indicating an input parameter error
    //

    // The basic float-based wrapper, applies Hanning window to data, converts FLOAT inputs to int16, calls FFTR_512(),
    // and converts results back to FLOAT.
    struct compx *fftr_fl(FLOAT *input_data, int32_t len);

    // This applies Hanning and then auto-scales:
    struct compx *fftr_fl_as(FLOAT *input_data, int32_t len);

    // This removes the mean, applies Hanning, and then auto-scales:
    struct compx *fftr_fl_rm_as(FLOAT *input_data, int32_t len);

    // The basic int16-based wrapper, applies Hanning window and calls FFTR_512():
    struct compx_int16_t *fftr(int16_t *input_data, int32_t len);

    // This applies Hanning and then auto-scales:
    struct compx_int16_t *fftr_as(int16_t *input_data, int32_t len);

    // This removes the mean, applies Hanning, and then auto-scales:
    struct compx_int16_t *fftr_rm_as(int16_t *input_data, int32_t len);

#ifdef __cplusplus
}
#endif

#endif // defind _FFTR_UTILS_H_
