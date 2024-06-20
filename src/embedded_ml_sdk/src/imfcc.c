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




#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include "kbutils.h"
#include "imfcc.h"
#include "imfcc_rom.h"

#include "fftr.h"
#include "fixlog.h"

#include "kb_typedefs.h"

#ifndef NULL
#define NULL ((void *)0)
#endif

/* Only one parameterization exists */
#define WINDOW_SIZE 400
#define WINDOW_LOG_SIZE 9
#define NUM_FILTERS 23
/* HPFbeta * (1<<13) */
#define HPF_BETA_13 164
/* sqrt(1.0 / NUM_CEPS) * (1<<11) */
#define SQRT_INV_N 427
/* sqrt(2.0 / NUM_CEPS) * (1<<11) */
#define SQRT_INV_2N 604
/* Pre-emphasis beta is 0.97 * 32767 */
#define PRE_EMPHASIS 31784
/* Left-shift of hanning window values */
#define WIN_HANNING_Q 14

void IMFCC_PreEmphasis(int16_t *data, int16_t length)
{
    /* Signal is shifted right by 1 to avoid overflow */

    int32_t prior = 0;
    int32_t i;
    int32_t sample;
    for (i = 0; i < length; i++)
    {
        sample = (int32_t)data[i];
        data[i] = (int16_t)(((sample << 15) - (prior * PRE_EMPHASIS)) >> 16);
        prior = sample;
    }

    // pre_emphasis_prior = prior;
    // return pre_emphasis_prior;
    // prior design need to be revisited
}

/* Returns max(abs(samples)) */
int32_t IMFCC_HannWindow(int16_t *buffer)
{
    int32_t i;
    int32_t max_value = 0;

    /* Left part of the window */
    for (i = 0; i < WINDOW_SIZE / 2; i++)
    {
        int32_t product = (int32_t)buffer[i] * (int32_t)kHannWindow[i];
        int16_t sample = (int16_t)(product >> HANN_WINDOW_Q);
        buffer[i] = sample;

        // printf("### HannWindow | %3d | %6" PRId16 " | %10f\n",i, buffer[i], Qint16_to_float(buffer[i],14));

        if (sample > max_value)
            max_value = sample;
        if (-sample > max_value)
            max_value = -sample;
    }

    /* Right part of the window */
    for (i = WINDOW_SIZE / 2; i < WINDOW_SIZE; i++)
    {
        int32_t product = (int32_t)buffer[i] * (int32_t)kHannWindow[WINDOW_SIZE - 1 - i];
        int16_t sample = (int16_t)(product >> HANN_WINDOW_Q);
        buffer[i] = sample;

        // printf("### HannWindow | %3d | %6" PRId16 " | %10f\n",i, buffer[i], Qint16_to_float(buffer[i],14));

        if (sample > max_value)
            max_value = sample;
        if (-sample > max_value)
            max_value = -sample;
    }

    return max_value;
}

void IMFCC_PowerTriFilter(const int16_t *samples,
                          int32_t shift, int32_t *output)
{
    /* TODO (jhofer): Could probably be done in 32 bit instead of 64 bit */
    int32_t i, j;
    /* Current index of the weight-bin */
    int32_t weight_index = 0;

    for (i = 0; i < NUM_FILTERS; i++)
    {
        uint64_t sum = 0;
        int32_t start_bin = kFirstMelBankBin[i];
        int32_t num_bins = kMelBankNumBins[i];
        uint32_t a1s;
        uint32_t a2;
        int32_t la1;
        int32_t la2;
        int32_t power;

        for (j = 0; j < num_bins; j++)
        {
            int32_t bin = start_bin + j;
            int64_t real = (int64_t)samples[2 * bin];
            int64_t imag = (int64_t)samples[2 * bin + 1];
            uint64_t power =
                (uint64_t)(real * real) +
                (uint64_t)(imag * imag);
            power <<= 2 * shift;
            power >>= 10;
            sum += power * (uint64_t)kMelBinWeights[weight_index];
            weight_index++;
        }

        /* log(sum) = log( a1 + a2 ) = log_add( log(a1), log(a2) ) */
        a1s = sum >> 32;
        a2 = sum & 0x00000000ffffffffLL;
        la1 = sphinx_fixlog(a1s) + 90852; /* ... + 2**12 log(2**32) */
        la2 = sphinx_fixlog(a2);
        power = sphinx_fe_log_add(la1, la2);
        /* floor to avoid overflow later */
        if (power < 49125)
            power = 49125;
        output[i] = power;

        // printf("### PowerTriFilter | %3d | %6d\n", i, output[i]);
    }
}

void IMFCC_DCT(int32_t *input, int32_t *output, int32_t num_cepstra)
{
    int32_t i, j;
    int32_t value;
    int32_t num_features = num_cepstra;

    value = input[0];
    for (j = 1; j < NUM_FILTERS; j++)
        value += input[j];
    value = ((value >> (COS_RADIX - 10)) * SQRT_INV_N) >> 10;
    output[0] = value;

    for (i = 1; i < num_features; ++i)
    {
        value = 0;
        for (j = 0; j < NUM_FILTERS; j++)
        {
            value += (input[j] >> (COS_RADIX - 10)) * (kDCTMatrix[i][j]);
        }
        value = ((value >> COS_RADIX) * SQRT_INV_2N) >> 10;
        output[i] = value;
        // printf("### DCT | %3d | %6d\n", i, output[i]);
    }
}

void IMFCC_Liftering(int32_t *MFCCs, int32_t num_cepstra)
{
    int32_t i;
    int32_t num_features = num_cepstra;

    for (i = 0; i < num_features; i++)
    {
        int32_t value = MFCCMUL(MFCCs[i], kLifters[i]);
        MFCCs[i] = value;
        // printf("### Lifter | %3d | %10d | %10f\n", i, MFCCs[i] , Qint32_to_float(MFCCs[i],13));
    }
}

void IMFCC_ProcessFrame(int16_t *samples,
                        int16_t sample_nrow,
                        int16_t window_size,
                        int32_t num_cepstra)
{

    int32_t i;
    const int32_t kMagicNumber = -190131; /* For power spectrum case */
    int32_t shift;
    int32_t max_value;

    int32_t tri_outputs[NUM_FILTERS];

    // using the features buffer as int32_t, values will be converted back to float before function completes
    int32_t *dct_outputs = (int32_t *)samples;

    IMFCC_PreEmphasis(samples, sample_nrow);

    max_value = IMFCC_HannWindow(samples);

    /* Shift samples left to fully utilize 16 bits */
    shift = 6;
    while (((max_value << (6 - shift)) < 16384) && shift > 0)
        shift--;
    for (i = 0; i < WINDOW_SIZE; i++)
    {
        samples[i] <<= 6 - shift;
    }

    /* Zero padding to FFT size */
    for (i = window_size; i < sample_nrow; i++)
    {
        samples[i] = 0;
    }

    shift += FFTR_512(samples);

    /* Created in samples array, as it is large enough */
    IMFCC_PowerTriFilter(samples, shift, tri_outputs);

    IMFCC_DCT(tri_outputs, dct_outputs, num_cepstra);

    IMFCC_Liftering(dct_outputs, num_cepstra);

    dct_outputs[0] += kMagicNumber;
}

void IMFE_ProcessFrame(int16_t *samples,
                       int16_t sample_nrow,
                       int16_t window_size)
{

    int32_t i;
    int32_t shift;
    int32_t max_value;
    int32_t *output = (int32_t *)samples;

    int32_t tri_outputs[NUM_FILTERS];

    IMFCC_PreEmphasis(samples, sample_nrow);

    max_value = IMFCC_HannWindow(samples);

    /* Shift samples left to fully utilize 16 bits */
    shift = 6;
    while (((max_value << (6 - shift)) < 16384) && shift > 0)
        shift--;
    for (i = 0; i < WINDOW_SIZE; i++)
    {
        samples[i] <<= 6 - shift;
    }

    /* Zero padding to FFT size */
    for (i = window_size; i < sample_nrow; i++)
    {
        samples[i] = 0;
    }

    shift += FFTR_512(samples);

    /* Created in samples array, as it is large enough */
    IMFCC_PowerTriFilter(samples, shift, tri_outputs);

    for (i = 0; i < NUM_FILTERS; i++)
    {
        output[i] = tri_outputs[i];
    }
}
