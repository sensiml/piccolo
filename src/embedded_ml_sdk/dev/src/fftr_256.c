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
 * \file fftr.cpp
 * \brief Rockhopper intereger 256-bin FFTR
 */

#include <stdint.h>

#include "fftr.h"
// #include "log.h"

#ifndef NULL
#define NULL ((void *)0)
#endif

#define N_WAVE 256
#define LOG2_N_WAVE 8 /* log2(N_WAVE) */

/* 3 / 4 of a full cycle of a sine wave,
 * Computed with:
 * awk 'BEGIN{for (i = 0; i < 256-64; i++)
 *      {printf("%d,", int32_t(sin(i*3.1415926536*2/256)*32767));
 *      if(i%8==7){printf("\n")}else{printf(" ")}}}'/
 */
static const int16_t kSine256[N_WAVE - N_WAVE / 4] = {
    0,
    804,
    1607,
    2410,
    3211,
    4011,
    4807,
    5601,
    6392,
    7179,
    7961,
    8739,
    9511,
    10278,
    11038,
    11792,
    12539,
    13278,
    14009,
    14732,
    15446,
    16150,
    16845,
    17530,
    18204,
    18867,
    19519,
    20159,
    20787,
    21402,
    22004,
    22594,
    23169,
    23731,
    24278,
    24811,
    25329,
    25831,
    26318,
    26789,
    27244,
    27683,
    28105,
    28510,
    28897,
    29268,
    29621,
    29955,
    30272,
    30571,
    30851,
    31113,
    31356,
    31580,
    31785,
    31970,
    32137,
    32284,
    32412,
    32520,
    32609,
    32678,
    32727,
    32757,
    32767,
    32757,
    32727,
    32678,
    32609,
    32520,
    32412,
    32284,
    32137,
    31970,
    31785,
    31580,
    31356,
    31113,
    30851,
    30571,
    30272,
    29955,
    29621,
    29268,
    28897,
    28510,
    28105,
    27683,
    27244,
    26789,
    26318,
    25831,
    25329,
    24811,
    24278,
    23731,
    23169,
    22594,
    22004,
    21402,
    20787,
    20159,
    19519,
    18867,
    18204,
    17530,
    16845,
    16150,
    15446,
    14732,
    14009,
    13278,
    12539,
    11792,
    11038,
    10278,
    9511,
    8739,
    7961,
    7179,
    6392,
    5601,
    4807,
    4011,
    3211,
    2410,
    1607,
    804,
    0,
    -804,
    -1607,
    -2410,
    -3211,
    -4011,
    -4807,
    -5601,
    -6392,
    -7179,
    -7961,
    -8739,
    -9511,
    -10278,
    -11038,
    -11792,
    -12539,
    -13278,
    -14009,
    -14732,
    -15446,
    -16150,
    -16845,
    -17530,
    -18204,
    -18867,
    -19519,
    -20159,
    -20787,
    -21402,
    -22004,
    -22594,
    -23169,
    -23731,
    -24278,
    -24811,
    -25329,
    -25831,
    -26318,
    -26789,
    -27244,
    -27683,
    -28105,
    -28510,
    -28897,
    -29268,
    -29621,
    -29955,
    -30272,
    -30571,
    -30851,
    -31113,
    -31356,
    -31580,
    -31785,
    -31970,
    -32137,
    -32284,
    -32412,
    -32520,
    -32609,
    -32678,
    -32727,
    -32757,
};

/* Bit reverse table for a single Byte.
 * Computed with:
 * awk 'BEGIN{for (i=0;i<128;i++) {o = 0; for (j=0;j<8;j++)
 *           {if(and(lshift(1,j), i)){o+= lshift(1, 7-j)}};
 *           printf("%d,", o);if(i%16==15){printf("\n")}else{printf(" ")}}}'
 */
static const uint8_t kBitReverseTable128[] = {
    0,
    128,
    64,
    192,
    32,
    160,
    96,
    224,
    16,
    144,
    80,
    208,
    48,
    176,
    112,
    240,
    8,
    136,
    72,
    200,
    40,
    168,
    104,
    232,
    24,
    152,
    88,
    216,
    56,
    184,
    120,
    248,
    4,
    132,
    68,
    196,
    36,
    164,
    100,
    228,
    20,
    148,
    84,
    212,
    52,
    180,
    116,
    244,
    12,
    140,
    76,
    204,
    44,
    172,
    108,
    236,
    28,
    156,
    92,
    220,
    60,
    188,
    124,
    252,
    2,
    130,
    66,
    194,
    34,
    162,
    98,
    226,
    18,
    146,
    82,
    210,
    50,
    178,
    114,
    242,
    10,
    138,
    74,
    202,
    42,
    170,
    106,
    234,
    26,
    154,
    90,
    218,
    58,
    186,
    122,
    250,
    6,
    134,
    70,
    198,
    38,
    166,
    102,
    230,
    22,
    150,
    86,
    214,
    54,
    182,
    118,
    246,
    14,
    142,
    78,
    206,
    46,
    174,
    110,
    238,
    30,
    158,
    94,
    222,
    62,
    190,
    126,
    254,

};

/** Multiplication of 0.15 and 15.0 integers */
static inline int16_t FIX_MULTIPLY(int16_t a, int16_t b)
{
    return (int16_t)((((int32_t)a * (int32_t)b) + 1) >> 15);
}

#ifdef _OPT
int32_t fft_16x16_primitive(int32_t *srcA, int32_t SrcB, int32_t *srcC);
void fft_16x16_primitive_init();
int32_t fft_shift(int32_t srcA);
#endif
/* Complex 128-bin FFT. real/complex values are interleaved in samples */
static int32_t FFT_128(int16_t *samples)
{
    const int32_t kNumSamples = 128;
    int32_t sample_index;
    int32_t sub_fft_length;
    int32_t sine_table_log_step;
    int32_t total_right_shift = 0;

    /* Bit-reversal of elements in sample array */
    for (sample_index = 1; sample_index < kNumSamples; sample_index++)
    {
        int32_t reverse_index = (int32_t)kBitReverseTable128[sample_index];
        int32_t *complex_samples = (int32_t *)samples;
        int32_t temp_value;

        if (reverse_index <= sample_index)
            continue;

        temp_value = complex_samples[sample_index];
        complex_samples[sample_index] = complex_samples[reverse_index];
        complex_samples[reverse_index] = temp_value;
    }

    sub_fft_length = 1;
    /* sine_table_log_step is LOG2_N_WAVE - sub_fft_log_length */
    sine_table_log_step = LOG2_N_WAVE - 1;
    while (sub_fft_length < kNumSamples)
    {
        total_right_shift += 1; /* Always do a right-shift */

        int32_t sample_step = sub_fft_length << 1;
        int32_t start_pos;
        for (start_pos = 0; start_pos < sub_fft_length; start_pos++)
        {
            int32_t i;
            /* phase_index maps from 0..pi to 0..N_WAVE */
            int32_t phase_index = start_pos << sine_table_log_step;
            int16_t weight_real = kSine256[phase_index + N_WAVE / 4];
            int16_t weight_imag = -kSine256[phase_index];

#ifdef _OPT
            fft_16x16_primitive_init();
            int32_t weight_ = (((int32_t)weight_imag) << 16) | (weight_real & 0xFFFF);
#endif

            for (i = start_pos; i < kNumSamples; i += sample_step)
            {
                int32_t s_index = i + sub_fft_length;

#if _OPT
                int32_t *s_p = (int32_t *)samples;
                fft_16x16_primitive(&s_p[s_index], weight_, &s_p[i]);
#else
                int16_t q_real = samples[2 * i] >> 1;
                int16_t q_imag = samples[2 * i + 1] >> 1;
                int16_t s_real = samples[2 * s_index] >> 1;
                int16_t s_imag = samples[2 * s_index + 1] >> 1;

                int16_t t_real = FIX_MULTIPLY(weight_real, s_real) -
                                 FIX_MULTIPLY(weight_imag, s_imag);
                int16_t t_imag = FIX_MULTIPLY(weight_real, s_imag) +
                                 FIX_MULTIPLY(weight_imag, s_real);
                samples[2 * s_index] = q_real - t_real;
                samples[2 * s_index + 1] = q_imag - t_imag;
                samples[2 * i] = q_real + t_real;
                samples[2 * i + 1] = q_imag + t_imag;
#endif // _OPT
            }
        }
        sine_table_log_step--;
        sub_fft_length <<= 1;
    }

    return total_right_shift;
}

int32_t FFTR_256(int16_t *samples)
{
    const int32_t kComplexFFTLength = 128;
    int32_t k;
    int32_t total_right_shift;

    total_right_shift = FFT_128(samples);
    total_right_shift++; /* Always do a right-shift */

    /* Final butterfly pass, ignoring bin 0 and bin 128 (which does not exist) */
    for (k = 1; k < kComplexFFTLength / 2; k++)
    {
        /* Assumes kLogNumSamples == LOG2_N_WAVE */
        int16_t weight_real = kSine256[k + N_WAVE / 4 + N_WAVE / 4];
        int16_t weight_imag = -kSine256[k + N_WAVE / 4];

        int16_t q_real = samples[2 * k] >> 1;
        int16_t q_imag = samples[2 * k + 1] >> 1;
        int16_t s_real = samples[2 * (kComplexFFTLength - k)] >> 1;
        int16_t s_imag = -samples[2 * (kComplexFFTLength - k) + 1] >> 1;

        int16_t f1_real = q_real + s_real;
        int16_t f1_imag = q_imag + s_imag;
        int16_t f2_real = q_real - s_real;
        int16_t f2_imag = q_imag - s_imag;
        int16_t t_real = FIX_MULTIPLY(weight_real, f2_real) -
                         FIX_MULTIPLY(weight_imag, f2_imag);
        int16_t t_imag = FIX_MULTIPLY(weight_real, f2_imag) +
                         FIX_MULTIPLY(weight_imag, f2_real);

        samples[2 * k] = f1_real + t_real;
        samples[2 * k + 1] = f1_imag + t_imag;
        samples[2 * (kComplexFFTLength - k)] = f1_real - t_real;
        samples[2 * (kComplexFFTLength - k) + 1] = t_imag - f1_imag;
    }

    return total_right_shift;
}

int32_t FFTR_256_GetRomSize(void)
{
    return (int32_t)(sizeof(kSine256) + sizeof(kBitReverseTable128));
}
