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




#ifndef _AVSASR_ROCKHOPPER_MINI_FRONTEND_SRC_IMFCC_H_
#define _AVSASR_ROCKHOPPER_MINI_FRONTEND_SRC_IMFCC_H_

/**
 * \file imfcc.h
 * \brief Integer Rockhopper MFCC frontend
 */

#include <stdint.h>
#include "kb_typedefs.h"
#include "rb.h"

#define IMFCC_FFT_SIZE 512
#define IMFCC_MAX_NUM_FEATURES 23

#ifdef __cplusplus
extern "C" {
#endif

/**
 * \brief Extract features for one frame of audio
 *
 * Note that feature extraction is done in-place meaning that the samples
 * buffer is overwritten.
 *
 * The samples buffer must have the size of IMFCC_GetFFTSize() + 2, not
 * IMFCC_GetWindowSize() and the spare values must all be 0.
 *
 * \param context Context that holds internal data of feature extraction
 * \param samples Array of audio samples
 * \param features Array that calculated features are stored in
 */
void IMFCC_ProcessFrame(    int16_t *samples,
                            int16_t sample_nrow,
                            int16_t window_size,
                            int32_t num_cepstra);

void IMFE_ProcessFrame(    int16_t *samples,
                            int16_t sample_nrow,
                            int16_t window_size);

// Exposing the following functions
void IMFCC_PreEmphasis(int16_t * data, int16_t length);
int32_t IMFCC_HannWindow(	int16_t *buffer);
void IMFCC_PowerTriFilter(	const int16_t *samples,
                                int32_t shift, int32_t *output);
void IMFCC_DCT(int32_t *input, int32_t *output, int32_t num_cepstra);
void IMFCC_Liftering(int32_t *MFCCs, int32_t num_cepstra);

#ifdef __cplusplus
}
#endif

#endif  /* define _AVSASR_ROCKHOPPER_MINI_DECODER_SRC_WFST_ON_THE_FLY_DECODER_H_ */
