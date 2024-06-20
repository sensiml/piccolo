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
// copied from LICENCE
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

/*
Note: The following code is from webRTC
   From https://webrtc.googlesource.com/src
   Used the following in command prompt -
   git clone https://webrtc.googlesource.com/src

The following files are modified and copied here

From webRTC/src/common_audio/signal_processing folder
  1.spl_inl.h
  2.devision_operations.c
  3.get_scaling_square.c
  4.energy.c

From webRTC/src/common_audio/vad folder
  5.webrtc_vad.c
  6.vad_core.c
  7.vad_filterbank.c
  8.vad_gmm.c
  9.vad_sp.c

*/
/*
 *
 * Note: Replaced int with int32_t, size_t with int32_t
 *
 */

#include "kbalgorithms.h"
#include "vad_webrtc.h"

#define WEBRTC_AUDIO_SAMPLE_RATE (16000)
#define WEBRTC_FRAME_LENGTH (30 * 16) // in samples - should be 30ms

#define WEBRTC_MOVING_AVG_SIZE (2 * 15) // 30ms*15*2 = 2*450ms of speech

static VadInstT vad;
static const int32_t kInitCheck = 42;
static int32_t remaining_audio_length = 0;
static int16_t audio_frame[WEBRTC_FRAME_LENGTH];
static int8_t webrtc_vad_flags[WEBRTC_MOVING_AVG_SIZE];
static int32_t webrtc_vad_counter = 0;

void reset_sg_filter_vad_webrtc()
{
}

int32_t sg_filter_vad_webrtc_init(void)
{
  WebRtcVad_InitCore(&vad);
  vad.init_flag = kInitCheck;
  WebRtcVad_set_mode_core(&vad, 0); // 0 is quality mode, 2 is aggressive mode
  remaining_audio_length = 0;
  webrtc_vad_counter = 0;
  return 0;
}

int32_t get_webrtc_sum(int32_t vad_flag, int8_t *vad_flags, int32_t buff_size)
{
  int32_t sum = 0;
  int32_t start_count;

  if (vad_flag > 0)
    vad_flag = 1;
  webrtc_vad_flags[webrtc_vad_counter++] = vad_flag;
  if (webrtc_vad_counter >= buff_size)
    webrtc_vad_counter = 0;

  start_count = webrtc_vad_counter;
  for (int32_t i = 0; i < buff_size; i++)
  {
    sum += webrtc_vad_flags[start_count++];
    if (start_count >= buff_size)
      start_count = 0;
  }
  // printf(" %d ", sum);
  return sum;
}
void clear_webrtc_vad(int32_t buff_size)
{
  int32_t counter = webrtc_vad_counter;
  // clear only half of the buffer
  for (int32_t i = 0; i < buff_size; i++)
  {
    webrtc_vad_flags[counter++] = 0;
    if (counter >= buff_size)
      counter = 0;
  }
  return;
}
/**
 * Return 0 if any of the data is outside the threshold range.
 * Return 1 if the segment isn't filtered out.
 */
int32_t sg_filter_vad_webrtc(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define SG_FILTER_VAD_WEBRTC_NUM_PARAMS 2
#define WEBRTC_THRESHOLD_PARAM_IDX 0
#define WEBRTC_CIRC_BUFFER_PARAM_IDX 1

  ringb *rb;
  int16_t base_index;
  int32_t vad_flag = 0;
  int32_t i, j, z;
  int32_t ret_val = 0;
  int32_t sum = 0;

#if SML_DEBUG // this shoul be there for python test
  if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != 2)
  {
    return -1;
  }
#endif

  rb = kb_model->pdata_buffer->data + cols_to_use->data[0];
  base_index = kb_model->sg_index;
  int32_t threshold = (int32_t)params->data[WEBRTC_THRESHOLD_PARAM_IDX];
  int32_t buff_size = (int32_t)params->data[WEBRTC_CIRC_BUFFER_PARAM_IDX];

  // Note: buff_size should be greater than threshold, else the sum will never be threshold
  if (buff_size < (threshold + 2))
    buff_size = (threshold + 2);
  if (buff_size > WEBRTC_MOVING_AVG_SIZE)
    buff_size = WEBRTC_MOVING_AVG_SIZE;

  // initialize if not done
  if (vad.init_flag == 0)
  {
    sg_filter_vad_webrtc_init();
  }

  // copy the data into audio frame only if it fits the frame length
  for (i = remaining_audio_length; i < kb_model->sg_length;)
  {
    if ((kb_model->sg_length - i) >= WEBRTC_FRAME_LENGTH)
      z = WEBRTC_FRAME_LENGTH; // full frame
    else
      z = kb_model->sg_length - i; // partial frame

    for (j = remaining_audio_length; j < z; j++)
    {
      // since audio is 2 bytes per sample
      audio_frame[j] = rb_read(rb, base_index);
    }
    i += (WEBRTC_FRAME_LENGTH - remaining_audio_length);
    if (z == WEBRTC_FRAME_LENGTH)
    {
      remaining_audio_length = 0;
      // vad_flag = WebRtcVad_Process(&vad, WEBRTC_AUDIO_SAMPLE_RATE, audio_frame, WEBRTC_FRAME_LENGTH);
      vad_flag = WebRtcVad_CalcVad16khz(&vad, audio_frame, WEBRTC_FRAME_LENGTH);
      sum = get_webrtc_sum(vad_flag, webrtc_vad_flags, buff_size);
      if (sum > threshold)
      {
        ret_val = 1;
        // clear vad flags - only half the buffer
        clear_webrtc_vad(buff_size / 2);
      }
    }
    else
    {
      remaining_audio_length = z;
    }
  }

  // return if speech is available
  return ret_val;
}

/*****************************************************************************/
// copied from old spl_inl.h

int16_t WebRtcSpl_GetSizeInBits(uint32_t n)
{
  int16_t bits;

  if (0xFFFF0000 & n)
  {
    bits = 16;
  }
  else
  {
    bits = 0;
  }
  if (0x0000FF00 & (n >> bits))
    bits += 8;
  if (0x000000F0 & (n >> bits))
    bits += 4;
  if (0x0000000C & (n >> bits))
    bits += 2;
  if (0x00000002 & (n >> bits))
    bits += 1;
  if (0x00000001 & (n >> bits))
    bits += 1;

  return bits;
}

int16_t WebRtcSpl_NormW32(int32_t a)
{
  int16_t zeros;

  if (a == 0)
  {
    return 0;
  }
  else if (a < 0)
  {
    a = ~a;
  }

  if (!(0xFFFF8000 & a))
  {
    zeros = 16;
  }
  else
  {
    zeros = 0;
  }
  if (!(0xFF800000 & (a << zeros)))
    zeros += 8;
  if (!(0xF8000000 & (a << zeros)))
    zeros += 4;
  if (!(0xE0000000 & (a << zeros)))
    zeros += 2;
  if (!(0xC0000000 & (a << zeros)))
    zeros += 1;

  return zeros;
}

int16_t WebRtcSpl_NormU32(uint32_t a)
{
  int16_t zeros;

  if (a == 0)
    return 0;

  if (!(0xFFFF0000 & a))
  {
    zeros = 16;
  }
  else
  {
    zeros = 0;
  }
  if (!(0xFF000000 & (a << zeros)))
    zeros += 8;
  if (!(0xF0000000 & (a << zeros)))
    zeros += 4;
  if (!(0xC0000000 & (a << zeros)))
    zeros += 2;
  if (!(0x80000000 & (a << zeros)))
    zeros += 1;

  return zeros;
}

/*****************************************************************************/
// copied from devision_operations.c

int32_t WebRtcSpl_DivW32W16(int32_t num, int16_t den)
{
  // Guard against division with 0
  if (den != 0)
  {
    return (int32_t)(num / den);
  }
  else
  {
    return (int32_t)0x7FFFFFFF;
  }
}
/*****************************************************************************/
// copied from get_scaling_square.c

int16_t WebRtcSpl_GetScalingSquare(int16_t *in_vector,
                                   int32_t in_vector_length,
                                   int32_t times)
{
  int16_t nbits = WebRtcSpl_GetSizeInBits(times);
  int32_t i;
  int16_t smax = -1;
  int16_t sabs;
  int16_t *sptr = in_vector;
  int16_t t;
  int32_t looptimes = in_vector_length;

  for (i = looptimes; i > 0; i--)
  {
    sabs = (*sptr > 0 ? *sptr++ : -*sptr++);
    smax = (sabs > smax ? sabs : smax);
  }
  t = WebRtcSpl_NormW32(WEBRTC_SPL_MUL(smax, smax));

  if (smax == 0)
  {
    return 0; // Since norm(0) returns 0
  }
  else
  {
    return (t > nbits) ? 0 : nbits - t;
  }
}
/*****************************************************************************/
// copied from energy.c

int32_t WebRtcSpl_Energy(int16_t *vector, int32_t vector_length, int *scale_factor)
{
  int32_t en = 0;
  int32_t i;
  int32_t scaling = WebRtcSpl_GetScalingSquare(vector, vector_length, vector_length);
  int32_t looptimes = vector_length;
  int16_t *vectorptr = vector;

  for (i = 0; i < looptimes; i++)
  {
    en += WEBRTC_SPL_MUL_16_16_RSFT(*vectorptr, *vectorptr, scaling);
    vectorptr++;
  }
  *scale_factor = scaling;

  return en;
}

/*****************************************************************************/
// copied from vad_core.c file

// Spectrum Weighting
static const int16_t kSpectrumWeight[kNumChannels] = {6, 8, 10, 12, 14, 16};
static const int16_t kNoiseUpdateConst = 655;   // Q15
static const int16_t kSpeechUpdateConst = 6554; // Q15
static const int16_t kBackEta = 154;            // Q8
// Minimum difference between the two models, Q5
static const int16_t kMinimumDifference[kNumChannels] = {
    544, 544, 576, 576, 576, 576};
// Upper limit of mean value for speech model, Q7
static const int16_t kMaximumSpeech[kNumChannels] = {
    11392, 11392, 11520, 11520, 11520, 11520};
// Minimum value for mean value
static const int16_t kMinimumMean[kNumGaussians] = {640, 768};
// Upper limit of mean value for noise model, Q7
static const int16_t kMaximumNoise[kNumChannels] = {
    9216, 9088, 8960, 8832, 8704, 8576};
// Start values for the Gaussian models, Q7
// Weights for the two Gaussians for the six channels (noise)
static const int16_t kNoiseDataWeights[kTableSize] = {
    34, 62, 72, 66, 53, 25, 94, 66, 56, 62, 75, 103};
// Weights for the two Gaussians for the six channels (speech)
static const int16_t kSpeechDataWeights[kTableSize] = {
    48, 82, 45, 87, 50, 47, 80, 46, 83, 41, 78, 81};
// Means for the two Gaussians for the six channels (noise)
static const int16_t kNoiseDataMeans[kTableSize] = {
    6738, 4892, 7065, 6715, 6771, 3369, 7646, 3863, 7820, 7266, 5020, 4362};
// Means for the two Gaussians for the six channels (speech)
static const int16_t kSpeechDataMeans[kTableSize] = {
    8306, 10085, 10078, 11823, 11843, 6309, 9473, 9571, 10879, 7581, 8180, 7483};
// Stds for the two Gaussians for the six channels (noise)
static const int16_t kNoiseDataStds[kTableSize] = {
    378, 1064, 493, 582, 688, 593, 474, 697, 475, 688, 421, 455};
// Stds for the two Gaussians for the six channels (speech)
static const int16_t kSpeechDataStds[kTableSize] = {
    555, 505, 567, 524, 585, 1231, 509, 828, 492, 1540, 1079, 850};

// Constants used in GmmProbability().
//
// Maximum number of counted speech (VAD = 1) frames in a row.
static const int16_t kMaxSpeechFrames = 6;
// Minimum standard deviation for both speech and noise.
static const int16_t kMinStd = 384;

// Constants in WebRtcVad_InitCore().
// Default aggressiveness mode.
static const short kDefaultMode = 0;
// static const int32_t kInitCheck = 42;

// Constants used in WebRtcVad_set_mode_core().
//
// Thresholds for different frame lengths (10 ms, 20 ms and 30 ms).
//
// Mode 0, Quality.
static const int16_t kOverHangMax1Q[3] = {8, 4, 3};
static const int16_t kOverHangMax2Q[3] = {14, 7, 5};
static const int16_t kLocalThresholdQ[3] = {24, 21, 24};
static const int16_t kGlobalThresholdQ[3] = {57, 48, 57};
// Mode 1, Low bitrate.
static const int16_t kOverHangMax1LBR[3] = {8, 4, 3};
static const int16_t kOverHangMax2LBR[3] = {14, 7, 5};
static const int16_t kLocalThresholdLBR[3] = {37, 32, 37};
static const int16_t kGlobalThresholdLBR[3] = {100, 80, 100};
// Mode 2, Aggressive.
static const int16_t kOverHangMax1AGG[3] = {6, 3, 2};
static const int16_t kOverHangMax2AGG[3] = {9, 5, 3};
static const int16_t kLocalThresholdAGG[3] = {82, 78, 82};
static const int16_t kGlobalThresholdAGG[3] = {285, 260, 285};
// Mode 3, Very aggressive.
static const int16_t kOverHangMax1VAG[3] = {6, 3, 2};
static const int16_t kOverHangMax2VAG[3] = {9, 5, 3};
static const int16_t kLocalThresholdVAG[3] = {94, 94, 94};
static const int16_t kGlobalThresholdVAG[3] = {1100, 1050, 1100};

// Calculates the weighted average w.r.t. number of Gaussians. The `data` are
// updated with an `offset` before averaging.
//
// - data     [i/o] : Data to average.
// - offset   [i]   : An offset added to `data`.
// - weights  [i]   : Weights used for averaging.
//
// returns          : The weighted average.
static int32_t WeightedAverage(int16_t *data, int16_t offset,
                               const int16_t *weights)
{
  int32_t k;
  int32_t weighted_average = 0;

  for (k = 0; k < kNumGaussians; k++)
  {
    data[k * kNumChannels] += offset;
    weighted_average += data[k * kNumChannels] * weights[k * kNumChannels];
  }
  return weighted_average;
}

// An s16 x s32 -> s32 multiplication that's allowed to overflow. (It's still
// undefined behavior, so not a good idea; this just makes UBSan ignore the
// violation, so that our old code can continue to do what it's always been
// doing.)
/*
static inline int32_t RTC_NO_SANITIZE("signed-integer-overflow")
    OverflowingMulS16ByS32ToS32(int16_t a, int32_t b) {
  return a * b;
}
*/
// Calculates the probabilities for both speech and background noise using
// Gaussian Mixture Models (GMM). A hypothesis-test is performed to decide which
// type of signal is most probable.
//
// - self           [i/o] : Pointer to VAD instance
// - features       [i]   : Feature vector of length `kNumChannels`
//                          = log10(energy in frequency band)
// - total_power    [i]   : Total power in audio frame.
// - frame_length   [i]   : Number of input samples
//
// - returns              : the VAD decision (0 - noise, 1 - speech).
static int16_t GmmProbability(VadInstT *self, int16_t *features,
                              int16_t total_power, int32_t frame_length)
{
  int32_t channel, k;
  int16_t feature_minimum;
  int16_t h0, h1;
  int16_t log_likelihood_ratio;
  int16_t vadflag = 0;
  int16_t shifts_h0, shifts_h1;
  int16_t tmp_s16, tmp1_s16, tmp2_s16;
  int16_t diff;
  int32_t gaussian;
  int16_t nmk, nmk2, nmk3, smk, smk2, nsk, ssk;
  int16_t delt, ndelt;
  int16_t maxspe, maxmu;
  int16_t deltaN[kTableSize], deltaS[kTableSize];
  int16_t ngprvec[kTableSize] = {0}; // Conditional probability = 0.
  int16_t sgprvec[kTableSize] = {0}; // Conditional probability = 0.
  int32_t h0_test, h1_test;
  int32_t tmp1_s32, tmp2_s32;
  int32_t sum_log_likelihood_ratios = 0;
  int32_t noise_global_mean, speech_global_mean;
  int32_t noise_probability[kNumGaussians], speech_probability[kNumGaussians];
  int16_t overhead1, overhead2, individualTest, totalTest;

  // Set various thresholds based on frame lengths (80, 160 or 240 samples).
  if (frame_length == 80)
  {
    overhead1 = self->over_hang_max_1[0];
    overhead2 = self->over_hang_max_2[0];
    individualTest = self->individual[0];
    totalTest = self->total[0];
  }
  else if (frame_length == 160)
  {
    overhead1 = self->over_hang_max_1[1];
    overhead2 = self->over_hang_max_2[1];
    individualTest = self->individual[1];
    totalTest = self->total[1];
  }
  else
  {
    overhead1 = self->over_hang_max_1[2];
    overhead2 = self->over_hang_max_2[2];
    individualTest = self->individual[2];
    totalTest = self->total[2];
  }

  if (total_power > kMinEnergy)
  {
    // The signal power of current frame is large enough for processing. The
    // processing consists of two parts:
    // 1) Calculating the likelihood of speech and thereby a VAD decision.
    // 2) Updating the underlying model, w.r.t., the decision made.

    // The detection scheme is an LRT with hypothesis
    // H0: Noise
    // H1: Speech
    //
    // We combine a global LRT with local tests, for each frequency sub-band,
    // here defined as `channel`.
    for (channel = 0; channel < kNumChannels; channel++)
    {
      // For each channel we model the probability with a GMM consisting of
      // `kNumGaussians`, with different means and standard deviations depending
      // on H0 or H1.
      h0_test = 0;
      h1_test = 0;
      for (k = 0; k < kNumGaussians; k++)
      {
        gaussian = channel + k * kNumChannels;
        // Probability under H0, that is, probability of frame being noise.
        // Value given in Q27 = Q7 * Q20.
        tmp1_s32 = WebRtcVad_GaussianProbability(features[channel],
                                                 self->noise_means[gaussian],
                                                 self->noise_stds[gaussian],
                                                 &deltaN[gaussian]);
        noise_probability[k] = kNoiseDataWeights[gaussian] * tmp1_s32;
        h0_test += noise_probability[k]; // Q27

        // Probability under H1, that is, probability of frame being speech.
        // Value given in Q27 = Q7 * Q20.
        tmp1_s32 = WebRtcVad_GaussianProbability(features[channel],
                                                 self->speech_means[gaussian],
                                                 self->speech_stds[gaussian],
                                                 &deltaS[gaussian]);
        speech_probability[k] = kSpeechDataWeights[gaussian] * tmp1_s32;
        h1_test += speech_probability[k]; // Q27
      }

      // Calculate the log likelihood ratio: log2(Pr{X|H1} / Pr{X|H1}).
      // Approximation:
      // log2(Pr{X|H1} / Pr{X|H1}) = log2(Pr{X|H1}*2^Q) - log2(Pr{X|H1}*2^Q)
      //                           = log2(h1_test) - log2(h0_test)
      //                           = log2(2^(31-shifts_h1)*(1+b1))
      //                             - log2(2^(31-shifts_h0)*(1+b0))
      //                           = shifts_h0 - shifts_h1
      //                             + log2(1+b1) - log2(1+b0)
      //                          ~= shifts_h0 - shifts_h1
      //
      // Note that b0 and b1 are values less than 1, hence, 0 <= log2(1+b0) < 1.
      // Further, b0 and b1 are independent and on the average the two terms
      // cancel.
      shifts_h0 = WebRtcSpl_NormW32(h0_test);
      shifts_h1 = WebRtcSpl_NormW32(h1_test);
      if (h0_test == 0)
      {
        shifts_h0 = 31;
      }
      if (h1_test == 0)
      {
        shifts_h1 = 31;
      }
      log_likelihood_ratio = shifts_h0 - shifts_h1;

      // Update `sum_log_likelihood_ratios` with spectrum weighting. This is
      // used for the global VAD decision.
      sum_log_likelihood_ratios +=
          (int32_t)(log_likelihood_ratio * kSpectrumWeight[channel]);

      // Local VAD decision.
      if ((log_likelihood_ratio * 4) > individualTest)
      {
        vadflag = 1;
      }

      // TODO(bjornv): The conditional probabilities below are applied on the
      // hard coded number of Gaussians set to two. Find a way to generalize.
      // Calculate local noise probabilities used later when updating the GMM.
      h0 = (int16_t)(h0_test >> 12); // Q15
      if (h0 > 0)
      {
        // High probability of noise. Assign conditional probabilities for each
        // Gaussian in the GMM.
        tmp1_s32 = (noise_probability[0] & 0xFFFFF000) << 2;           // Q29
        ngprvec[channel] = (int16_t)WebRtcSpl_DivW32W16(tmp1_s32, h0); // Q14
        ngprvec[channel + kNumChannels] = 16384 - ngprvec[channel];
      }
      else
      {
        // Low noise probability. Assign conditional probability 1 to the first
        // Gaussian and 0 to the rest (which is already set at initialization).
        ngprvec[channel] = 16384;
      }

      // Calculate local speech probabilities used later when updating the GMM.
      h1 = (int16_t)(h1_test >> 12); // Q15
      if (h1 > 0)
      {
        // High probability of speech. Assign conditional probabilities for each
        // Gaussian in the GMM. Otherwise use the initialized values, i.e., 0.
        tmp1_s32 = (speech_probability[0] & 0xFFFFF000) << 2;          // Q29
        sgprvec[channel] = (int16_t)WebRtcSpl_DivW32W16(tmp1_s32, h1); // Q14
        sgprvec[channel + kNumChannels] = 16384 - sgprvec[channel];
      }
    }

    // Make a global VAD decision.
    vadflag |= (sum_log_likelihood_ratios >= totalTest);

    // Update the model parameters.
    maxspe = 12800;
    for (channel = 0; channel < kNumChannels; channel++)
    {

      // Get minimum value in past which is used for long term correction in Q4.
      feature_minimum = WebRtcVad_FindMinimum(self, features[channel], channel);

      // Compute the "global" mean, that is the sum of the two means weighted.
      noise_global_mean = WeightedAverage(&self->noise_means[channel], 0,
                                          &kNoiseDataWeights[channel]);
      tmp1_s16 = (int16_t)(noise_global_mean >> 6); // Q8

      for (k = 0; k < kNumGaussians; k++)
      {
        gaussian = channel + k * kNumChannels;

        nmk = self->noise_means[gaussian];
        smk = self->speech_means[gaussian];
        nsk = self->noise_stds[gaussian];
        ssk = self->speech_stds[gaussian];

        // Update noise mean vector if the frame consists of noise only.
        nmk2 = nmk;
        if (!vadflag)
        {
          // deltaN = (x-mu)/sigma^2
          // ngprvec[k] = `noise_probability[k]` /
          //   (`noise_probability[0]` + `noise_probability[1]`)

          // (Q14 * Q11 >> 11) = Q14.
          delt = (int16_t)((ngprvec[gaussian] * deltaN[gaussian]) >> 11);
          // Q7 + (Q14 * Q15 >> 22) = Q7.
          nmk2 = nmk + (int16_t)((delt * kNoiseUpdateConst) >> 22);
        }

        // Long term correction of the noise mean.
        // Q8 - Q8 = Q8.
        ndelt = (feature_minimum << 4) - tmp1_s16;
        // Q7 + (Q8 * Q8) >> 9 = Q7.
        nmk3 = nmk2 + (int16_t)((ndelt * kBackEta) >> 9);

        // Control that the noise mean does not drift to much.
        tmp_s16 = (int16_t)((k + 5) << 7);
        if (nmk3 < tmp_s16)
        {
          nmk3 = tmp_s16;
        }
        tmp_s16 = (int16_t)((72 + k - channel) << 7);
        if (nmk3 > tmp_s16)
        {
          nmk3 = tmp_s16;
        }
        self->noise_means[gaussian] = nmk3;

        if (vadflag)
        {
          // Update speech mean vector:
          // `deltaS` = (x-mu)/sigma^2
          // sgprvec[k] = `speech_probability[k]` /
          //   (`speech_probability[0]` + `speech_probability[1]`)

          // (Q14 * Q11) >> 11 = Q14.
          delt = (int16_t)((sgprvec[gaussian] * deltaS[gaussian]) >> 11);
          // Q14 * Q15 >> 21 = Q8.
          tmp_s16 = (int16_t)((delt * kSpeechUpdateConst) >> 21);
          // Q7 + (Q8 >> 1) = Q7. With rounding.
          smk2 = smk + ((tmp_s16 + 1) >> 1);

          // Control that the speech mean does not drift to much.
          maxmu = maxspe + 640;
          if (smk2 < kMinimumMean[k])
          {
            smk2 = kMinimumMean[k];
          }
          if (smk2 > maxmu)
          {
            smk2 = maxmu;
          }
          self->speech_means[gaussian] = smk2; // Q7.

          // (Q7 >> 3) = Q4. With rounding.
          tmp_s16 = ((smk + 4) >> 3);

          tmp_s16 = features[channel] - tmp_s16; // Q4
          // (Q11 * Q4 >> 3) = Q12.
          tmp1_s32 = (deltaS[gaussian] * tmp_s16) >> 3;
          tmp2_s32 = tmp1_s32 - 4096;
          tmp_s16 = sgprvec[gaussian] >> 2;
          // (Q14 >> 2) * Q12 = Q24.
          tmp1_s32 = tmp_s16 * tmp2_s32;

          tmp2_s32 = tmp1_s32 >> 4; // Q20

          // 0.1 * Q20 / Q7 = Q13.
          if (tmp2_s32 > 0)
          {
            tmp_s16 = (int16_t)WebRtcSpl_DivW32W16(tmp2_s32, ssk * 10);
          }
          else
          {
            tmp_s16 = (int16_t)WebRtcSpl_DivW32W16(-tmp2_s32, ssk * 10);
            tmp_s16 = -tmp_s16;
          }
          // Divide by 4 giving an update factor of 0.025 (= 0.1 / 4).
          // Note that division by 4 equals shift by 2, hence,
          // (Q13 >> 8) = (Q13 >> 6) / 4 = Q7.
          tmp_s16 += 128; // Rounding.
          ssk += (tmp_s16 >> 8);
          if (ssk < kMinStd)
          {
            ssk = kMinStd;
          }
          self->speech_stds[gaussian] = ssk;
        }
        else
        {
          // Update GMM variance vectors.
          // deltaN * (features[channel] - nmk) - 1
          // Q4 - (Q7 >> 3) = Q4.
          tmp_s16 = features[channel] - (nmk >> 3);
          // (Q11 * Q4 >> 3) = Q12.
          tmp1_s32 = (deltaN[gaussian] * tmp_s16) >> 3;
          tmp1_s32 -= 4096;

          // (Q14 >> 2) * Q12 = Q24.
          tmp_s16 = (ngprvec[gaussian] + 2) >> 2;
          // tmp2_s32 = OverflowingMulS16ByS32ToS32(tmp_s16, tmp1_s32); //note: siva -commented out
          tmp2_s32 = tmp_s16 * tmp1_s32;
          // Q20  * approx 0.001 (2^-10=0.0009766), hence,
          // (Q24 >> 14) = (Q24 >> 4) / 2^10 = Q20.
          tmp1_s32 = tmp2_s32 >> 14;

          // Q20 / Q7 = Q13.
          if (tmp1_s32 > 0)
          {
            tmp_s16 = (int16_t)WebRtcSpl_DivW32W16(tmp1_s32, nsk);
          }
          else
          {
            tmp_s16 = (int16_t)WebRtcSpl_DivW32W16(-tmp1_s32, nsk);
            tmp_s16 = -tmp_s16;
          }
          tmp_s16 += 32;       // Rounding
          nsk += tmp_s16 >> 6; // Q13 >> 6 = Q7.
          if (nsk < kMinStd)
          {
            nsk = kMinStd;
          }
          self->noise_stds[gaussian] = nsk;
        }
      }

      // Separate models if they are too close.
      // `noise_global_mean` in Q14 (= Q7 * Q7).
      noise_global_mean = WeightedAverage(&self->noise_means[channel], 0,
                                          &kNoiseDataWeights[channel]);

      // `speech_global_mean` in Q14 (= Q7 * Q7).
      speech_global_mean = WeightedAverage(&self->speech_means[channel], 0,
                                           &kSpeechDataWeights[channel]);

      // `diff` = "global" speech mean - "global" noise mean.
      // (Q14 >> 9) - (Q14 >> 9) = Q5.
      diff = (int16_t)(speech_global_mean >> 9) -
             (int16_t)(noise_global_mean >> 9);
      if (diff < kMinimumDifference[channel])
      {
        tmp_s16 = kMinimumDifference[channel] - diff;

        // `tmp1_s16` = ~0.8 * (kMinimumDifference - diff) in Q7.
        // `tmp2_s16` = ~0.2 * (kMinimumDifference - diff) in Q7.
        tmp1_s16 = (int16_t)((13 * tmp_s16) >> 2);
        tmp2_s16 = (int16_t)((3 * tmp_s16) >> 2);

        // Move Gaussian means for speech model by `tmp1_s16` and update
        // `speech_global_mean`. Note that `self->speech_means[channel]` is
        // changed after the call.
        speech_global_mean = WeightedAverage(&self->speech_means[channel],
                                             tmp1_s16,
                                             &kSpeechDataWeights[channel]);

        // Move Gaussian means for noise model by -`tmp2_s16` and update
        // `noise_global_mean`. Note that `self->noise_means[channel]` is
        // changed after the call.
        noise_global_mean = WeightedAverage(&self->noise_means[channel],
                                            -tmp2_s16,
                                            &kNoiseDataWeights[channel]);
      }

      // Control that the speech & noise means do not drift to much.
      maxspe = kMaximumSpeech[channel];
      tmp2_s16 = (int16_t)(speech_global_mean >> 7);
      if (tmp2_s16 > maxspe)
      {
        // Upper limit of speech model.
        tmp2_s16 -= maxspe;

        for (k = 0; k < kNumGaussians; k++)
        {
          self->speech_means[channel + k * kNumChannels] -= tmp2_s16;
        }
      }

      tmp2_s16 = (int16_t)(noise_global_mean >> 7);
      if (tmp2_s16 > kMaximumNoise[channel])
      {
        tmp2_s16 -= kMaximumNoise[channel];

        for (k = 0; k < kNumGaussians; k++)
        {
          self->noise_means[channel + k * kNumChannels] -= tmp2_s16;
        }
      }
    }
    self->frame_counter++;
  }

  // Smooth with respect to transition hysteresis.
  if (!vadflag)
  {
    if (self->over_hang > 0)
    {
      vadflag = 2 + self->over_hang;
      self->over_hang--;
    }
    self->num_of_speech = 0;
  }
  else
  {
    self->num_of_speech++;
    if (self->num_of_speech > kMaxSpeechFrames)
    {
      self->num_of_speech = kMaxSpeechFrames;
      self->over_hang = overhead2;
    }
    else
    {
      self->over_hang = overhead1;
    }
  }
  return vadflag;
}

// Initialize the VAD. Set aggressiveness mode to default value.
int32_t WebRtcVad_InitCore(VadInstT *self)
{
  int32_t i;

  if (self == NULL)
  {
    return -1;
  }

  // Initialization of general struct variables.
  self->vad = 1; // Speech active (=1).
  self->frame_counter = 0;
  self->over_hang = 0;
  self->num_of_speech = 0;

  // Initialization of downsampling filter state.
  memset(self->downsampling_filter_states, 0,
         sizeof(self->downsampling_filter_states));

  // Initialization of 48 to 8 kHz downsampling.
  // WebRtcSpl_ResetResample48khzTo8khz(&self->state_48_to_8);

  // Read initial PDF parameters.
  for (i = 0; i < kTableSize; i++)
  {
    self->noise_means[i] = kNoiseDataMeans[i];
    self->speech_means[i] = kSpeechDataMeans[i];
    self->noise_stds[i] = kNoiseDataStds[i];
    self->speech_stds[i] = kSpeechDataStds[i];
  }

  // Initialize Index and Minimum value vectors.
  for (i = 0; i < 16 * kNumChannels; i++)
  {
    self->low_value_vector[i] = 10000;
    self->index_vector[i] = 0;
  }

  // Initialize splitting filter states.
  memset(self->upper_state, 0, sizeof(self->upper_state));
  memset(self->lower_state, 0, sizeof(self->lower_state));

  // Initialize high pass filter states.
  memset(self->hp_filter_state, 0, sizeof(self->hp_filter_state));

  // Initialize mean value memory, for WebRtcVad_FindMinimum().
  for (i = 0; i < kNumChannels; i++)
  {
    self->mean_value[i] = 1600;
  }

  // Set aggressiveness mode to default (=`kDefaultMode`).
  if (WebRtcVad_set_mode_core(self, kDefaultMode) != 0)
  {
    return -1;
  }

  self->init_flag = kInitCheck;

  return 0;
}

// Set aggressiveness mode
int32_t WebRtcVad_set_mode_core(VadInstT *self, int32_t mode)
{
  int32_t return_value = 0;

  switch (mode)
  {
  case 0:
    // Quality mode.
    memcpy(self->over_hang_max_1, kOverHangMax1Q,
           sizeof(self->over_hang_max_1));
    memcpy(self->over_hang_max_2, kOverHangMax2Q,
           sizeof(self->over_hang_max_2));
    memcpy(self->individual, kLocalThresholdQ,
           sizeof(self->individual));
    memcpy(self->total, kGlobalThresholdQ,
           sizeof(self->total));
    break;
  case 1:
    // Low bitrate mode.
    memcpy(self->over_hang_max_1, kOverHangMax1LBR,
           sizeof(self->over_hang_max_1));
    memcpy(self->over_hang_max_2, kOverHangMax2LBR,
           sizeof(self->over_hang_max_2));
    memcpy(self->individual, kLocalThresholdLBR,
           sizeof(self->individual));
    memcpy(self->total, kGlobalThresholdLBR,
           sizeof(self->total));
    break;
  case 2:
    // Aggressive mode.
    memcpy(self->over_hang_max_1, kOverHangMax1AGG,
           sizeof(self->over_hang_max_1));
    memcpy(self->over_hang_max_2, kOverHangMax2AGG,
           sizeof(self->over_hang_max_2));
    memcpy(self->individual, kLocalThresholdAGG,
           sizeof(self->individual));
    memcpy(self->total, kGlobalThresholdAGG,
           sizeof(self->total));
    break;
  case 3:
    // Very aggressive mode.
    memcpy(self->over_hang_max_1, kOverHangMax1VAG,
           sizeof(self->over_hang_max_1));
    memcpy(self->over_hang_max_2, kOverHangMax2VAG,
           sizeof(self->over_hang_max_2));
    memcpy(self->individual, kLocalThresholdVAG,
           sizeof(self->individual));
    memcpy(self->total, kGlobalThresholdVAG,
           sizeof(self->total));
    break;
  default:
    return_value = -1;
    break;
  }

  return return_value;
}

// Calculate VAD decision by first extracting feature values and then calculate
// probability for both speech and background noise.
/*
int32_t WebRtcVad_CalcVad48khz(VadInstT* inst, const int16_t* speech_frame,
                           int32_t frame_length) {
  int32_t vad;
  //int32_t i;
  int16_t speech_nb[240];  // 30 ms in 8 kHz.
  // `tmp_mem` is a temporary memory used by resample function, length is
  // frame length in 10 ms (480 samples) + 256 extra.
  int32_t tmp_mem[480 + 256] = { 0 };
  const int32_t kFrameLen10ms48khz = 480;
  const int32_t kFrameLen10ms8khz = 80;
  int32_t num_10ms_frames = frame_length / kFrameLen10ms48khz;

  for (i = 0; i < num_10ms_frames; i++) {
    WebRtcSpl_Resample48khzTo8khz(speech_frame,
                                  &speech_nb[i * kFrameLen10ms8khz],
                                  &inst->state_48_to_8,
                                  tmp_mem);
  }

  // Do VAD on an 8 kHz signal
  vad = WebRtcVad_CalcVad8khz(inst, speech_nb, frame_length / 6);

  return vad;
}

int32_t WebRtcVad_CalcVad32khz(VadInstT* inst, const int16_t* speech_frame,
                           int32_t frame_length)
{
    int32_t len;
    int32_t vad;
    int16_t speechWB[480]; // Downsampled speech frame: 960 samples (30ms in SWB)
    int16_t speechNB[240]; // Downsampled speech frame: 480 samples (30ms in WB)


    // Downsample signal 32->16->8 before doing VAD
    WebRtcVad_Downsampling(speech_frame, speechWB, &(inst->downsampling_filter_states[2]),
                           frame_length);
    len = frame_length / 2;

    WebRtcVad_Downsampling(speechWB, speechNB, inst->downsampling_filter_states, len);
    len /= 2;

    // Do VAD on an 8 kHz signal
    vad = WebRtcVad_CalcVad8khz(inst, speechNB, len);

    return vad;
}
*/
int32_t WebRtcVad_CalcVad16khz(VadInstT *inst, const int16_t *speech_frame,
                               int32_t frame_length)
{
  int32_t len;
  int32_t vad;
  int16_t speechNB[240]; // Downsampled speech frame: 480 samples (30ms in WB)

  // Wideband: Downsample signal before doing VAD
  WebRtcVad_Downsampling(speech_frame, speechNB, inst->downsampling_filter_states,
                         frame_length);

  len = frame_length / 2;
  vad = WebRtcVad_CalcVad8khz(inst, speechNB, len);

  return vad;
}

int32_t WebRtcVad_CalcVad8khz(VadInstT *inst, const int16_t *speech_frame,
                              int32_t frame_length)
{
  int16_t feature_vector[kNumChannels], total_power;

  // Get power in the bands
  total_power = WebRtcVad_CalculateFeatures(inst, speech_frame, frame_length,
                                            feature_vector);

  // Make a VAD
  inst->vad = GmmProbability(inst, feature_vector, total_power, frame_length);

  return inst->vad;
}

/*****************************************************************************/
// copied from vad_filterbank.c

// Constants used in LogOfEnergy().
static const int16_t kLogConst = 24660;         // 160*log10(2) in Q9.
static const int16_t kLogEnergyIntPart = 14336; // 14 in Q10

// Coefficients used by HighPassFilter, Q14.
static const int16_t kHpZeroCoefs[3] = {6631, -13262, 6631};
static const int16_t kHpPoleCoefs[3] = {16384, -7756, 5620};

// Allpass filter coefficients, upper and lower, in Q15.
// Upper: 0.64, Lower: 0.17
static const int16_t kAllPassCoefsQ15[2] = {20972, 5571};

// Adjustment for division with two in SplitFilter.
static const int16_t kOffsetVector[6] = {368, 368, 272, 176, 176, 176};

// High pass filtering, with a cut-off frequency at 80 Hz, if the `data_in` is
// sampled at 500 Hz.
//
// - data_in      [i]   : Input audio data sampled at 500 Hz.
// - data_length  [i]   : Length of input and output data.
// - filter_state [i/o] : State of the filter.
// - data_out     [o]   : Output audio data in the frequency interval
//                        80 - 250 Hz.
static void HighPassFilter(const int16_t *data_in, int32_t data_length,
                           int16_t *filter_state, int16_t *data_out)
{
  int32_t i;
  const int16_t *in_ptr = data_in;
  int16_t *out_ptr = data_out;
  int32_t tmp32 = 0;

  // The sum of the absolute values of the impulse response:
  // The zero/pole-filter has a max amplification of a single sample of: 1.4546
  // Impulse response: 0.4047 -0.6179 -0.0266  0.1993  0.1035  -0.0194
  // The all-zero section has a max amplification of a single sample of: 1.6189
  // Impulse response: 0.4047 -0.8094  0.4047  0       0        0
  // The all-pole section has a max amplification of a single sample of: 1.9931
  // Impulse response: 1.0000  0.4734 -0.1189 -0.2187 -0.0627   0.04532

  for (i = 0; i < data_length; i++)
  {
    // All-zero section (filter coefficients in Q14).
    tmp32 = kHpZeroCoefs[0] * *in_ptr;
    tmp32 += kHpZeroCoefs[1] * filter_state[0];
    tmp32 += kHpZeroCoefs[2] * filter_state[1];
    filter_state[1] = filter_state[0];
    filter_state[0] = *in_ptr++;

    // All-pole section (filter coefficients in Q14).
    tmp32 -= kHpPoleCoefs[1] * filter_state[2];
    tmp32 -= kHpPoleCoefs[2] * filter_state[3];
    filter_state[3] = filter_state[2];
    filter_state[2] = (int16_t)(tmp32 >> 14);
    *out_ptr++ = filter_state[2];
  }
}

// All pass filtering of `data_in`, used before splitting the signal into two
// frequency bands (low pass vs high pass).
// Note that `data_in` and `data_out` can NOT correspond to the same address.
//
// - data_in            [i]   : Input audio signal given in Q0.
// - data_length        [i]   : Length of input and output data.
// - filter_coefficient [i]   : Given in Q15.
// - filter_state       [i/o] : State of the filter given in Q(-1).
// - data_out           [o]   : Output audio signal given in Q(-1).
static void AllPassFilter(const int16_t *data_in, int32_t data_length,
                          int16_t filter_coefficient, int16_t *filter_state,
                          int16_t *data_out)
{
  // The filter can only cause overflow (in the w16 output variable)
  // if more than 4 consecutive input numbers are of maximum value and
  // has the the same sign as the impulse responses first taps.
  // First 6 taps of the impulse response:
  // 0.6399 0.5905 -0.3779 0.2418 -0.1547 0.0990

  int32_t i;
  int16_t tmp16 = 0;
  int32_t tmp32 = 0;
  int32_t state32 = ((int32_t)(*filter_state) * (1 << 16)); // Q15

  for (i = 0; i < data_length; i++)
  {
    tmp32 = state32 + filter_coefficient * *data_in;
    tmp16 = (int16_t)(tmp32 >> 16); // Q(-1)
    *data_out++ = tmp16;
    state32 = (*data_in * (1 << 14)) - filter_coefficient * tmp16; // Q14
    state32 *= 2;                                                  // Q15.
    data_in += 2;
  }

  *filter_state = (int16_t)(state32 >> 16); // Q(-1)
}

// Splits `data_in` into `hp_data_out` and `lp_data_out` corresponding to
// an upper (high pass) part and a lower (low pass) part respectively.
//
// - data_in      [i]   : Input audio data to be split into two frequency bands.
// - data_length  [i]   : Length of `data_in`.
// - upper_state  [i/o] : State of the upper filter, given in Q(-1).
// - lower_state  [i/o] : State of the lower filter, given in Q(-1).
// - hp_data_out  [o]   : Output audio data of the upper half of the spectrum.
//                        The length is `data_length` / 2.
// - lp_data_out  [o]   : Output audio data of the lower half of the spectrum.
//                        The length is `data_length` / 2.
static void SplitFilter(const int16_t *data_in, int32_t data_length,
                        int16_t *upper_state, int16_t *lower_state,
                        int16_t *hp_data_out, int16_t *lp_data_out)
{
  int32_t i;
  int32_t half_length = data_length >> 1; // Downsampling by 2.
  int16_t tmp_out;

  // All-pass filtering upper branch.
  AllPassFilter(&data_in[0], half_length, kAllPassCoefsQ15[0], upper_state,
                hp_data_out);

  // All-pass filtering lower branch.
  AllPassFilter(&data_in[1], half_length, kAllPassCoefsQ15[1], lower_state,
                lp_data_out);

  // Make LP and HP signals.
  for (i = 0; i < half_length; i++)
  {
    tmp_out = *hp_data_out;
    *hp_data_out++ -= *lp_data_out;
    *lp_data_out++ += tmp_out;
  }
}

// Calculates the energy of `data_in` in dB, and also updates an overall
// `total_energy` if necessary.
//
// - data_in      [i]   : Input audio data for energy calculation.
// - data_length  [i]   : Length of input data.
// - offset       [i]   : Offset value added to `log_energy`.
// - total_energy [i/o] : An external energy updated with the energy of
//                        `data_in`.
//                        NOTE: `total_energy` is only updated if
//                        `total_energy` <= `kMinEnergy`.
// - log_energy   [o]   : 10 * log10("energy of `data_in`") given in Q4.
static void LogOfEnergy(const int16_t *data_in, int32_t data_length,
                        int16_t offset, int16_t *total_energy,
                        int16_t *log_energy)
{
  // `tot_rshifts` accumulates the number of right shifts performed on `energy`.
  int32_t tot_rshifts = 0;
  // The `energy` will be normalized to 15 bits. We use unsigned integer because
  // we eventually will mask out the fractional part.
  uint32_t energy = 0;

  // RTC_DCHECK(data_in);
  // RTC_DCHECK_GT(data_length, 0);
  // Note: the above is equal to the following
  // assert(data_in != NULL);
  // assert(data_length > 0);

  energy = (uint32_t)WebRtcSpl_Energy((int16_t *)data_in, data_length,
                                      &tot_rshifts);

  if (energy != 0)
  {
    // By construction, normalizing to 15 bits is equivalent with 17 leading
    // zeros of an unsigned 32 bit value.
    int32_t normalizing_rshifts = 17 - WebRtcSpl_NormU32(energy);
    // In a 15 bit representation the leading bit is 2^14. log2(2^14) in Q10 is
    // (14 << 10), which is what we initialize `log2_energy` with. For a more
    // detailed derivations, see below.
    int16_t log2_energy = kLogEnergyIntPart;

    tot_rshifts += normalizing_rshifts;
    // Normalize `energy` to 15 bits.
    // `tot_rshifts` is now the total number of right shifts performed on
    // `energy` after normalization. This means that `energy` is in
    // Q(-tot_rshifts).
    if (normalizing_rshifts < 0)
    {
      energy <<= -normalizing_rshifts;
    }
    else
    {
      energy >>= normalizing_rshifts;
    }

    // Calculate the energy of `data_in` in dB, in Q4.
    //
    // 10 * log10("true energy") in Q4 = 2^4 * 10 * log10("true energy") =
    // 160 * log10(`energy` * 2^`tot_rshifts`) =
    // 160 * log10(2) * log2(`energy` * 2^`tot_rshifts`) =
    // 160 * log10(2) * (log2(`energy`) + log2(2^`tot_rshifts`)) =
    // (160 * log10(2)) * (log2(`energy`) + `tot_rshifts`) =
    // `kLogConst` * (`log2_energy` + `tot_rshifts`)
    //
    // We know by construction that `energy` is normalized to 15 bits. Hence,
    // `energy` = 2^14 + frac_Q15, where frac_Q15 is a fractional part in Q15.
    // Further, we'd like `log2_energy` in Q10
    // log2(`energy`) in Q10 = 2^10 * log2(2^14 + frac_Q15) =
    // 2^10 * log2(2^14 * (1 + frac_Q15 * 2^-14)) =
    // 2^10 * (14 + log2(1 + frac_Q15 * 2^-14)) ~=
    // (14 << 10) + 2^10 * (frac_Q15 * 2^-14) =
    // (14 << 10) + (frac_Q15 * 2^-4) = (14 << 10) + (frac_Q15 >> 4)
    //
    // Note that frac_Q15 = (`energy` & 0x00003FFF)

    // Calculate and add the fractional part to `log2_energy`.
    log2_energy += (int16_t)((energy & 0x00003FFF) >> 4);

    // `kLogConst` is in Q9, `log2_energy` in Q10 and `tot_rshifts` in Q0.
    // Note that we in our derivation above have accounted for an output in Q4.
    *log_energy = (int16_t)(((kLogConst * log2_energy) >> 19) +
                            ((tot_rshifts * kLogConst) >> 9));

    if (*log_energy < 0)
    {
      *log_energy = 0;
    }
  }
  else
  {
    *log_energy = offset;
    return;
  }

  *log_energy += offset;

  // Update the approximate `total_energy` with the energy of `data_in`, if
  // `total_energy` has not exceeded `kMinEnergy`. `total_energy` is used as an
  // energy indicator in WebRtcVad_GmmProbability() in vad_core.c.
  if (*total_energy <= kMinEnergy)
  {
    if (tot_rshifts >= 0)
    {
      // We know by construction that the `energy` > `kMinEnergy` in Q0, so add
      // an arbitrary value such that `total_energy` exceeds `kMinEnergy`.
      *total_energy += kMinEnergy + 1;
    }
    else
    {
      // By construction `energy` is represented by 15 bits, hence any number of
      // right shifted `energy` will fit in an int16_t. In addition, adding the
      // value to `total_energy` is wrap around safe as long as
      // `kMinEnergy` < 8192.
      *total_energy += (int16_t)(energy >> -tot_rshifts); // Q0.
    }
  }
}

int16_t WebRtcVad_CalculateFeatures(VadInstT *self, const int16_t *data_in,
                                    int32_t data_length, int16_t *features)
{
  int16_t total_energy = 0;
  // We expect `data_length` to be 80, 160 or 240 samples, which corresponds to
  // 10, 20 or 30 ms in 8 kHz. Therefore, the intermediate downsampled data will
  // have at most 120 samples after the first split and at most 60 samples after
  // the second split.
  int16_t hp_120[120], lp_120[120];
  int16_t hp_60[60], lp_60[60];
  const int32_t half_data_length = data_length >> 1;
  int32_t length = half_data_length; // `data_length` / 2, corresponds to
                                     // bandwidth = 2000 Hz after downsampling.

  // Initialize variables for the first SplitFilter().
  int32_t frequency_band = 0;
  const int16_t *in_ptr = data_in; // [0 - 4000] Hz.
  int16_t *hp_out_ptr = hp_120;    // [2000 - 4000] Hz.
  int16_t *lp_out_ptr = lp_120;    // [0 - 2000] Hz.

  // RTC_DCHECK_LE(data_length, 240);
  // RTC_DCHECK_LT(4, kNumChannels - 1);  // Checking maximum `frequency_band`.
  // Note: the above is equal to the following
  // assert(data_length >= 0);
  // assert(data_length <= 240);
  // assert(4 < kNumChannels - 1);  // Checking maximum |frequency_band|.

  // Split at 2000 Hz and downsample.
  SplitFilter(in_ptr, data_length, &self->upper_state[frequency_band],
              &self->lower_state[frequency_band], hp_out_ptr, lp_out_ptr);

  // For the upper band (2000 Hz - 4000 Hz) split at 3000 Hz and downsample.
  frequency_band = 1;
  in_ptr = hp_120;    // [2000 - 4000] Hz.
  hp_out_ptr = hp_60; // [3000 - 4000] Hz.
  lp_out_ptr = lp_60; // [2000 - 3000] Hz.
  SplitFilter(in_ptr, length, &self->upper_state[frequency_band],
              &self->lower_state[frequency_band], hp_out_ptr, lp_out_ptr);

  // Energy in 3000 Hz - 4000 Hz.
  length >>= 1; // `data_length` / 4 <=> bandwidth = 1000 Hz.

  LogOfEnergy(hp_60, length, kOffsetVector[5], &total_energy, &features[5]);

  // Energy in 2000 Hz - 3000 Hz.
  LogOfEnergy(lp_60, length, kOffsetVector[4], &total_energy, &features[4]);

  // For the lower band (0 Hz - 2000 Hz) split at 1000 Hz and downsample.
  frequency_band = 2;
  in_ptr = lp_120;           // [0 - 2000] Hz.
  hp_out_ptr = hp_60;        // [1000 - 2000] Hz.
  lp_out_ptr = lp_60;        // [0 - 1000] Hz.
  length = half_data_length; // `data_length` / 2 <=> bandwidth = 2000 Hz.
  SplitFilter(in_ptr, length, &self->upper_state[frequency_band],
              &self->lower_state[frequency_band], hp_out_ptr, lp_out_ptr);

  // Energy in 1000 Hz - 2000 Hz.
  length >>= 1; // `data_length` / 4 <=> bandwidth = 1000 Hz.
  LogOfEnergy(hp_60, length, kOffsetVector[3], &total_energy, &features[3]);

  // For the lower band (0 Hz - 1000 Hz) split at 500 Hz and downsample.
  frequency_band = 3;
  in_ptr = lp_60;      // [0 - 1000] Hz.
  hp_out_ptr = hp_120; // [500 - 1000] Hz.
  lp_out_ptr = lp_120; // [0 - 500] Hz.
  SplitFilter(in_ptr, length, &self->upper_state[frequency_band],
              &self->lower_state[frequency_band], hp_out_ptr, lp_out_ptr);

  // Energy in 500 Hz - 1000 Hz.
  length >>= 1; // `data_length` / 8 <=> bandwidth = 500 Hz.
  LogOfEnergy(hp_120, length, kOffsetVector[2], &total_energy, &features[2]);

  // For the lower band (0 Hz - 500 Hz) split at 250 Hz and downsample.
  frequency_band = 4;
  in_ptr = lp_120;    // [0 - 500] Hz.
  hp_out_ptr = hp_60; // [250 - 500] Hz.
  lp_out_ptr = lp_60; // [0 - 250] Hz.
  SplitFilter(in_ptr, length, &self->upper_state[frequency_band],
              &self->lower_state[frequency_band], hp_out_ptr, lp_out_ptr);

  // Energy in 250 Hz - 500 Hz.
  length >>= 1; // `data_length` / 16 <=> bandwidth = 250 Hz.
  LogOfEnergy(hp_60, length, kOffsetVector[1], &total_energy, &features[1]);

  // Remove 0 Hz - 80 Hz, by high pass filtering the lower band.
  HighPassFilter(lp_60, length, self->hp_filter_state, hp_120);

  // Energy in 80 Hz - 250 Hz.
  LogOfEnergy(hp_120, length, kOffsetVector[0], &total_energy, &features[0]);

  return total_energy;
}
/*****************************************************************************/
// copied from vad_gmm.c

static const int32_t kCompVar = 22005;
static const int16_t kLog2Exp = 5909; // log2(exp(1)) in Q12.

// For a normal distribution, the probability of `input` is calculated and
// returned (in Q20). The formula for normal distributed probability is
//
// 1 / s * exp(-(x - m)^2 / (2 * s^2))
//
// where the parameters are given in the following Q domains:
// m = `mean` (Q7)
// s = `std` (Q7)
// x = `input` (Q4)
// in addition to the probability we output `delta` (in Q11) used when updating
// the noise/speech model.
int32_t WebRtcVad_GaussianProbability(int16_t input,
                                      int16_t mean,
                                      int16_t std,
                                      int16_t *delta)
{
  int16_t tmp16, inv_std, inv_std2, exp_value = 0;
  int32_t tmp32;

  // Calculate `inv_std` = 1 / s, in Q10.
  // 131072 = 1 in Q17, and (`std` >> 1) is for rounding instead of truncation.
  // Q-domain: Q17 / Q7 = Q10.
  tmp32 = (int32_t)131072 + (int32_t)(std >> 1);
  inv_std = (int16_t)WebRtcSpl_DivW32W16(tmp32, std);

  // Calculate `inv_std2` = 1 / s^2, in Q14.
  tmp16 = (inv_std >> 2); // Q10 -> Q8.
  // Q-domain: (Q8 * Q8) >> 2 = Q14.
  inv_std2 = (int16_t)((tmp16 * tmp16) >> 2);
  // TODO(bjornv): Investigate if changing to
  // inv_std2 = (int16_t)((inv_std * inv_std) >> 6);
  // gives better accuracy.

  tmp16 = (input << 3); // Q4 -> Q7
  tmp16 = tmp16 - mean; // Q7 - Q7 = Q7

  // To be used later, when updating noise/speech model.
  // `delta` = (x - m) / s^2, in Q11.
  // Q-domain: (Q14 * Q7) >> 10 = Q11.
  *delta = (int16_t)((inv_std2 * tmp16) >> 10);

  // Calculate the exponent `tmp32` = (x - m)^2 / (2 * s^2), in Q10. Replacing
  // division by two with one shift.
  // Q-domain: (Q11 * Q7) >> 8 = Q10.
  tmp32 = (*delta * tmp16) >> 9;

  // If the exponent is small enough to give a non-zero probability we calculate
  // `exp_value` ~= exp(-(x - m)^2 / (2 * s^2))
  //             ~= exp2(-log2(exp(1)) * `tmp32`).
  if (tmp32 < kCompVar)
  {
    // Calculate `tmp16` = log2(exp(1)) * `tmp32`, in Q10.
    // Q-domain: (Q12 * Q10) >> 12 = Q10.
    tmp16 = (int16_t)((kLog2Exp * tmp32) >> 12);
    tmp16 = -tmp16;
    exp_value = (0x0400 | (tmp16 & 0x03FF));
    tmp16 ^= 0xFFFF;
    tmp16 >>= 10;
    tmp16 += 1;
    // Get `exp_value` = exp(-`tmp32`) in Q10.
    exp_value >>= tmp16;
  }

  // Calculate and return (1 / s) * exp(-(x - m)^2 / (2 * s^2)), in Q20.
  // Q-domain: Q10 * Q10 = Q20.
  return inv_std * exp_value;
}
/*****************************************************************************/
// copied from vad_sp.c
//  Allpass filter coefficients, upper and lower, in Q13.
//  Upper: 0.64, Lower: 0.17.
static const int16_t kAllPassCoefsQ13[2] = {5243, 1392}; // Q13.
static const int16_t kSmoothingDown = 6553;              // 0.2 in Q15.
static const int16_t kSmoothingUp = 32439;               // 0.99 in Q15.

// TODO(bjornv): Move this function to vad_filterbank.c.
// Downsampling filter based on splitting filter and allpass functions.
void WebRtcVad_Downsampling(const int16_t *signal_in,
                            int16_t *signal_out,
                            int32_t *filter_state,
                            int32_t in_length)
{
  int16_t tmp16_1 = 0, tmp16_2 = 0;
  int32_t tmp32_1 = filter_state[0];
  int32_t tmp32_2 = filter_state[1];
  int32_t n = 0;
  // Downsampling by 2 gives half length.
  int32_t half_length = (in_length >> 1);

  // Filter coefficients in Q13, filter state in Q0.
  for (n = 0; n < half_length; n++)
  {
    // All-pass filtering upper branch.
    tmp16_1 = (int16_t)((tmp32_1 >> 1) +
                        ((kAllPassCoefsQ13[0] * *signal_in) >> 14));
    *signal_out = tmp16_1;
    tmp32_1 = (int32_t)(*signal_in++) - ((kAllPassCoefsQ13[0] * tmp16_1) >> 12);

    // All-pass filtering lower branch.
    tmp16_2 = (int16_t)((tmp32_2 >> 1) +
                        ((kAllPassCoefsQ13[1] * *signal_in) >> 14));
    *signal_out++ += tmp16_2;
    tmp32_2 = (int32_t)(*signal_in++) - ((kAllPassCoefsQ13[1] * tmp16_2) >> 12);
  }
  // Store the filter states.
  filter_state[0] = tmp32_1;
  filter_state[1] = tmp32_2;
}

// Inserts `feature_value` into `low_value_vector`, if it is one of the 16
// smallest values the last 100 frames. Then calculates and returns the median
// of the five smallest values.
int16_t WebRtcVad_FindMinimum(VadInstT *self,
                              int16_t feature_value,
                              int32_t channel)
{
  int32_t i = 0, j = 0;
  int32_t position = -1;
  // Offset to beginning of the 16 minimum values in memory.
  const int32_t offset = (channel << 4);
  int16_t current_median = 1600;
  int16_t alpha = 0;
  int32_t tmp32 = 0;
  // Pointer to memory for the 16 minimum values and the age of each value of
  // the `channel`.
  int16_t *age = &self->index_vector[offset];
  int16_t *smallest_values = &self->low_value_vector[offset];

  // RTC_DCHECK_LT(channel, kNumChannels);
  // Note: the above is equal to the following
  // assert(channel < kNumChannels);

  // Each value in `smallest_values` is getting 1 loop older. Update `age`, and
  // remove old values.
  for (i = 0; i < 16; i++)
  {
    if (age[i] != 100)
    {
      age[i]++;
    }
    else
    {
      // Too old value. Remove from memory and shift larger values downwards.
      for (j = i; j < 15; j++)
      {
        smallest_values[j] = smallest_values[j + 1];
        age[j] = age[j + 1];
      }
      age[15] = 101;
      smallest_values[15] = 10000;
    }
  }

  // Check if `feature_value` is smaller than any of the values in
  // `smallest_values`. If so, find the `position` where to insert the new value
  // (`feature_value`).
  if (feature_value < smallest_values[7])
  {
    if (feature_value < smallest_values[3])
    {
      if (feature_value < smallest_values[1])
      {
        if (feature_value < smallest_values[0])
        {
          position = 0;
        }
        else
        {
          position = 1;
        }
      }
      else if (feature_value < smallest_values[2])
      {
        position = 2;
      }
      else
      {
        position = 3;
      }
    }
    else if (feature_value < smallest_values[5])
    {
      if (feature_value < smallest_values[4])
      {
        position = 4;
      }
      else
      {
        position = 5;
      }
    }
    else if (feature_value < smallest_values[6])
    {
      position = 6;
    }
    else
    {
      position = 7;
    }
  }
  else if (feature_value < smallest_values[15])
  {
    if (feature_value < smallest_values[11])
    {
      if (feature_value < smallest_values[9])
      {
        if (feature_value < smallest_values[8])
        {
          position = 8;
        }
        else
        {
          position = 9;
        }
      }
      else if (feature_value < smallest_values[10])
      {
        position = 10;
      }
      else
      {
        position = 11;
      }
    }
    else if (feature_value < smallest_values[13])
    {
      if (feature_value < smallest_values[12])
      {
        position = 12;
      }
      else
      {
        position = 13;
      }
    }
    else if (feature_value < smallest_values[14])
    {
      position = 14;
    }
    else
    {
      position = 15;
    }
  }

  // If we have detected a new small value, insert it at the correct position
  // and shift larger values up.
  if (position > -1)
  {
    for (i = 15; i > position; i--)
    {
      smallest_values[i] = smallest_values[i - 1];
      age[i] = age[i - 1];
    }
    smallest_values[position] = feature_value;
    age[position] = 1;
  }

  // Get `current_median`.
  if (self->frame_counter > 2)
  {
    current_median = smallest_values[2];
  }
  else if (self->frame_counter > 0)
  {
    current_median = smallest_values[0];
  }

  // Smooth the median value.
  if (self->frame_counter > 0)
  {
    if (current_median < self->mean_value[channel])
    {
      alpha = kSmoothingDown; // 0.2 in Q15.
    }
    else
    {
      alpha = kSmoothingUp; // 0.99 in Q15.
    }
  }
  tmp32 = (alpha + 1) * self->mean_value[channel];
  tmp32 += (WEBRTC_SPL_WORD16_MAX - alpha) * current_median;
  tmp32 += 16384;
  self->mean_value[channel] = (int16_t)(tmp32 >> 15);

  return self->mean_value[channel];
}
/*****************************************************************************/
