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




/*
 *  Copyright (c) 2012 The WebRTC project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree. An additional intellectual property rights grant can be found
 *  in the file PATENTS.  All contributing project authors may
 *  be found in the AUTHORS file in the root of the source tree.
 */
//copied from LICENCE
/*
 *  Copyright (c) 2011, The WebRTC project authors. All rights reserved.
 *
 *  Redistribution and use in source and binary forms, with or without
 *  modification, are permitted provided that the following conditions are
 *  met:
 *
 *    * Redistributions of source code must retain the above copyright
 *      notice, this list of conditions and the following disclaimer.
 *
 *    * Redistributions in binary form must reproduce the above copyright
 *      notice, this list of conditions and the following disclaimer in
 *      the documentation and/or other materials provided with the
 *      distribution.
 *
 *    * Neither the name of Google nor the names of its contributors may
 *      be used to endorse or promote products derived from this software
 *      without specific prior written permission.
 *
 *  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 *  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 *  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 *  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
 *  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 *   SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 *  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 *  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 *  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 *  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 *  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#ifndef _VAD_WEBRTC_H_
#define _VAD_WEBRTC_H_

#include "kb_common.h"
#include "kbutils.h"

/*
The following files are modified and copied here

From webRTC/src/common_audio/vad folder
  1.webrtc_vad.h
  2.vad_core.h
  3.vad_filterbank.h
  4.vad_gmm.h
  5.vad_sp.h
*/

//copied from webrtc_vad.h file

/*
 * This header file includes the VAD API calls. Specific function calls are
 * given below.
 */

#ifndef COMMON_AUDIO_VAD_INCLUDE_WEBRTC_VAD_H_  // NOLINT
#define COMMON_AUDIO_VAD_INCLUDE_WEBRTC_VAD_H_

//#include <stddef.h>
//#include <stdint.h>

typedef struct WebRtcVadInst VadInst;

#ifdef __cplusplus
extern "C" {
#endif

// Creates an instance to the VAD structure.
VadInst* WebRtcVad_Create(void);

// Frees the dynamic memory of a specified VAD instance.
//
// - handle [i] : Pointer to VAD instance that should be freed.
void WebRtcVad_Free(VadInst* handle);

// Initializes a VAD instance.
//
// - handle [i/o] : Instance that should be initialized.
//
// returns        : 0 - (OK),
//                 -1 - (null pointer or Default mode could not be set).
int32_t WebRtcVad_Init(VadInst* handle);

// Sets the VAD operating mode. A more aggressive (higher mode) VAD is more
// restrictive in reporting speech. Put in other words the probability of being
// speech when the VAD returns 1 is increased with increasing mode. As a
// consequence also the missed detection rate goes up.
//
// - handle [i/o] : VAD instance.
// - mode   [i]   : Aggressiveness mode (0, 1, 2, or 3).
//
// returns        : 0 - (OK),
//                 -1 - (null pointer, mode could not be set or the VAD instance
//                       has not been initialized).
int32_t WebRtcVad_set_mode(VadInst* handle, int32_t mode);

// Calculates a VAD decision for the `audio_frame`. For valid sampling rates
// frame lengths, see the description of WebRtcVad_ValidRatesAndFrameLengths().
//
// - handle       [i/o] : VAD Instance. Needs to be initialized by
//                        WebRtcVad_Init() before call.
// - fs           [i]   : Sampling frequency (Hz): 8000, 16000, or 32000
// - audio_frame  [i]   : Audio frame buffer.
// - frame_length [i]   : Length of audio frame buffer in number of samples.
//
// returns              : 1 - (Active Voice),
//                        0 - (Non-active Voice),
//                       -1 - (Error)
int32_t WebRtcVad_Process(VadInst* handle,
                      int32_t fs,
                      const int16_t* audio_frame,
                      int32_t frame_length);

// Checks for valid combinations of `rate` and `frame_length`. We support 10,
// 20 and 30 ms frames and the rates 8000, 16000 and 32000 Hz.
//
// - rate         [i] : Sampling frequency (Hz).
// - frame_length [i] : Speech frame buffer length in number of samples.
//
// returns            : 0 - (valid combination), -1 - (invalid combination)
int32_t WebRtcVad_ValidRateAndFrameLength(int32_t rate, int32_t frame_length);

#ifdef __cplusplus
}
#endif

#endif  // COMMON_AUDIO_VAD_INCLUDE_WEBRTC_VAD_H_  // NOLINT

//copied from vad_core.h file

/*
 * This header file includes the descriptions of the core VAD calls.
 */

#ifndef COMMON_AUDIO_VAD_VAD_CORE_H_
#define COMMON_AUDIO_VAD_VAD_CORE_H_

//#include "../inc/signal_processing_library.h"

// TODO(https://bugs.webrtc.org/14476): When converted to C++, remove the macro.
//#if defined(__cplusplus)
//#define CONSTEXPR_INT(x) constexpr int32_tx
//#else
#define CONSTEXPR_INT(x) enum { x }
//#endif

CONSTEXPR_INT(kNumChannels = 6);  // Number of frequency bands (named channels).
CONSTEXPR_INT(
    kNumGaussians = 2);  // Number of Gaussians per channel in the GMM.
CONSTEXPR_INT(kTableSize = kNumChannels * kNumGaussians);
CONSTEXPR_INT(
    kMinEnergy = 10);  // Minimum energy required to trigger audio signal.

typedef struct VadInstT_ {
  int32_t vad;
  int32_t downsampling_filter_states[4];
  //WebRtcSpl_State48khzTo8khz state_48_to_8;
  int16_t noise_means[kTableSize];
  int16_t speech_means[kTableSize];
  int16_t noise_stds[kTableSize];
  int16_t speech_stds[kTableSize];
  // TODO(bjornv): Change to `frame_count`.
  int32_t frame_counter;
  int16_t over_hang;  // Over Hang
  int16_t num_of_speech;
  // TODO(bjornv): Change to `age_vector`.
  int16_t index_vector[16 * kNumChannels];
  int16_t low_value_vector[16 * kNumChannels];
  // TODO(bjornv): Change to `median`.
  int16_t mean_value[kNumChannels];
  int16_t upper_state[5];
  int16_t lower_state[5];
  int16_t hp_filter_state[4];
  int16_t over_hang_max_1[3];
  int16_t over_hang_max_2[3];
  int16_t individual[3];
  int16_t total[3];

  int32_t init_flag;
} VadInstT;

// Initializes the core VAD component. The default aggressiveness mode is
// controlled by `kDefaultMode` in vad_core.c.
//
// - self [i/o] : Instance that should be initialized
//
// returns      : 0 (OK), -1 (null pointer in or if the default mode can't be
//                set)
int32_t WebRtcVad_InitCore(VadInstT* self);

/****************************************************************************
 * WebRtcVad_set_mode_core(...)
 *
 * This function changes the VAD settings
 *
 * Input:
 *      - inst      : VAD instance
 *      - mode      : Aggressiveness degree
 *                    0 (High quality) - 3 (Highly aggressive)
 *
 * Output:
 *      - inst      : Changed  instance
 *
 * Return value     :  0 - Ok
 *                    -1 - Error
 */

int32_t WebRtcVad_set_mode_core(VadInstT* self, int32_t mode);

/****************************************************************************
 * WebRtcVad_CalcVad48khz(...)
 * WebRtcVad_CalcVad32khz(...)
 * WebRtcVad_CalcVad16khz(...)
 * WebRtcVad_CalcVad8khz(...)
 *
 * Calculate probability for active speech and make VAD decision.
 *
 * Input:
 *      - inst          : Instance that should be initialized
 *      - speech_frame  : Input speech frame
 *      - frame_length  : Number of input samples
 *
 * Output:
 *      - inst          : Updated filter states etc.
 *
 * Return value         : VAD decision
 *                        0 - No active speech
 *                        1-6 - Active speech
 */
int32_t WebRtcVad_CalcVad48khz(VadInstT* inst,
                           const int16_t* speech_frame,
                           int32_t frame_length);
int32_t WebRtcVad_CalcVad32khz(VadInstT* inst,
                           const int16_t* speech_frame,
                           int32_t frame_length);
int32_t WebRtcVad_CalcVad16khz(VadInstT* inst,
                           const int16_t* speech_frame,
                           int32_t frame_length);
int32_t WebRtcVad_CalcVad8khz(VadInstT* inst,
                          const int16_t* speech_frame,
                          int32_t frame_length);

#endif  // COMMON_AUDIO_VAD_VAD_CORE_H_

//copied from vad_filterbank.h file

/*
 * This file includes feature calculating functionality used in vad_core.c.
 */

#ifndef COMMON_AUDIO_VAD_VAD_FILTERBANK_H_
#define COMMON_AUDIO_VAD_VAD_FILTERBANK_H_

//#include "../inc/vad_core.h"

// Takes `data_length` samples of `data_in` and calculates the logarithm of the
// energy of each of the `kNumChannels` = 6 frequency bands used by the VAD:
//        80 Hz - 250 Hz
//        250 Hz - 500 Hz
//        500 Hz - 1000 Hz
//        1000 Hz - 2000 Hz
//        2000 Hz - 3000 Hz
//        3000 Hz - 4000 Hz
//
// The values are given in Q4 and written to `features`. Further, an approximate
// overall energy is returned. The return value is used in
// WebRtcVad_GmmProbability() as a signal indicator, hence it is arbitrary above
// the threshold `kMinEnergy`.
//
// - self         [i/o] : State information of the VAD.
// - data_in      [i]   : Input audio data, for feature extraction.
// - data_length  [i]   : Audio data size, in number of samples.
// - features     [o]   : 10 * log10(energy in each frequency band), Q4.
// - returns            : Total energy of the signal (NOTE! This value is not
//                        exact. It is only used in a comparison.)
int16_t WebRtcVad_CalculateFeatures(VadInstT* self,
                                    const int16_t* data_in,
                                    int32_t data_length,
                                    int16_t* features);

#endif  // COMMON_AUDIO_VAD_VAD_FILTERBANK_H_

//copied from vad_gmm.h file

// Gaussian probability calculations internally used in vad_core.c.

#ifndef COMMON_AUDIO_VAD_VAD_GMM_H_
#define COMMON_AUDIO_VAD_VAD_GMM_H_

//#include <stdint.h>

// Calculates the probability for `input`, given that `input` comes from a
// normal distribution with mean and standard deviation (`mean`, `std`).
//
// Inputs:
//      - input         : input sample in Q4.
//      - mean          : mean input in the statistical model, Q7.
//      - std           : standard deviation, Q7.
//
// Output:
//
//      - delta         : input used when updating the model, Q11.
//                        `delta` = (`input` - `mean`) / `std`^2.
//
// Return:
//   (probability for `input`) =
//    1 / `std` * exp(-(`input` - `mean`)^2 / (2 * `std`^2));
int32_t WebRtcVad_GaussianProbability(int16_t input,
                                      int16_t mean,
                                      int16_t std,
                                      int16_t* delta);

#endif  // COMMON_AUDIO_VAD_VAD_GMM_H_

//copied from vad_sp.h file

// This file includes specific signal processing tools used in vad_core.c.

#ifndef COMMON_AUDIO_VAD_VAD_SP_H_
#define COMMON_AUDIO_VAD_VAD_SP_H_

//#include "../inc/vad_core.h"

// Downsamples the signal by a factor 2, eg. 32->16 or 16->8.
//
// Inputs:
//      - signal_in     : Input signal.
//      - in_length     : Length of input signal in samples.
//
// Input & Output:
//      - filter_state  : Current filter states of the two all-pass filters. The
//                        `filter_state` is updated after all samples have been
//                        processed.
//
// Output:
//      - signal_out    : Downsampled signal (of length `in_length` / 2).
void WebRtcVad_Downsampling(const int16_t* signal_in,
                            int16_t* signal_out,
                            int32_t* filter_state,
                            int32_t in_length);

// Updates and returns the smoothed feature minimum. As minimum we use the
// median of the five smallest feature values in a 100 frames long window.
// As long as `handle->frame_counter` is zero, that is, we haven't received any
// "valid" data, FindMinimum() outputs the default value of 1600.
//
// Inputs:
//      - feature_value : New feature value to update with.
//      - channel       : Channel number.
//
// Input & Output:
//      - handle        : State information of the VAD.
//
// Returns:
//                      : Smoothed minimum value for a moving window.
int16_t WebRtcVad_FindMinimum(VadInstT* handle,
                              int16_t feature_value,
                              int32_t channel);

#endif  // COMMON_AUDIO_VAD_VAD_SP_H_

//copied from signal_processing_library.h file

/*
 * This header file includes all of the fix point32_t signal processing library
 * (SPL) function descriptions and declarations. For specific function calls,
 * see bottom of file.
 */

#ifndef COMMON_AUDIO_SIGNAL_PROCESSING_INCLUDE_SIGNAL_PROCESSING_LIBRARY_H_
#define COMMON_AUDIO_SIGNAL_PROCESSING_INCLUDE_SIGNAL_PROCESSING_LIBRARY_H_

 // Macros specific for the fixed point32_t implementation
#define WEBRTC_SPL_WORD16_MAX 32767
#define WEBRTC_SPL_MUL(a, b) ((int32_t)((int32_t)(a) * (int32_t)(b)))
//note: this is modified
#define WEBRTC_SPL_MUL_16_16_RSFT(a, b, c) ((int32_t)((int32_t)a * (int32_t)b) >> (c))


//Note: not copied the rest


#endif  // COMMON_AUDIO_SIGNAL_PROCESSING_INCLUDE_SIGNAL_PROCESSING_LIBRARY_H_

#endif //_VAD_WEBRTC_H_