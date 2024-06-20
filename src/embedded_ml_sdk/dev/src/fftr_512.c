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
 * \brief Rockhopper intereger 512-bin FFTR
 */

#include <stdint.h>

#include "fftr.h"
// #include "log.h"

#ifndef NULL
#define NULL ((void *)0)
#endif

#define N_WAVE 512
#define LOG2_N_WAVE 9 /* log2(N_WAVE) */

/* 3 / 4 of a full cycle of a sine wave,
 * Computed with:
 * awk 'BEGIN{for (i = 0; i < 512-128; i++)
 *      {printf("%d,", int32_t(sin(i*3.1415926536*2/512)*32767));
 *      if(i%8==7){printf("\n")}else{printf(" ")}}}'/
 */
static const int16_t kSine512[N_WAVE - N_WAVE / 4] = {
    0,
    402,
    804,
    1206,
    1607,
    2009,
    2410,
    2811,
    3211,
    3611,
    4011,
    4409,
    4807,
    5205,
    5601,
    5997,
    6392,
    6786,
    7179,
    7571,
    7961,
    8351,
    8739,
    9126,
    9511,
    9895,
    10278,
    10659,
    11038,
    11416,
    11792,
    12166,
    12539,
    12909,
    13278,
    13645,
    14009,
    14372,
    14732,
    15090,
    15446,
    15799,
    16150,
    16499,
    16845,
    17189,
    17530,
    17868,
    18204,
    18537,
    18867,
    19194,
    19519,
    19840,
    20159,
    20474,
    20787,
    21096,
    21402,
    21705,
    22004,
    22301,
    22594,
    22883,
    23169,
    23452,
    23731,
    24006,
    24278,
    24546,
    24811,
    25072,
    25329,
    25582,
    25831,
    26077,
    26318,
    26556,
    26789,
    27019,
    27244,
    27466,
    27683,
    27896,
    28105,
    28309,
    28510,
    28706,
    28897,
    29085,
    29268,
    29446,
    29621,
    29790,
    29955,
    30116,
    30272,
    30424,
    30571,
    30713,
    30851,
    30984,
    31113,
    31236,
    31356,
    31470,
    31580,
    31684,
    31785,
    31880,
    31970,
    32056,
    32137,
    32213,
    32284,
    32350,
    32412,
    32468,
    32520,
    32567,
    32609,
    32646,
    32678,
    32705,
    32727,
    32744,
    32757,
    32764,
    32767,
    32764,
    32757,
    32744,
    32727,
    32705,
    32678,
    32646,
    32609,
    32567,
    32520,
    32468,
    32412,
    32350,
    32284,
    32213,
    32137,
    32056,
    31970,
    31880,
    31785,
    31684,
    31580,
    31470,
    31356,
    31236,
    31113,
    30984,
    30851,
    30713,
    30571,
    30424,
    30272,
    30116,
    29955,
    29790,
    29621,
    29446,
    29268,
    29085,
    28897,
    28706,
    28510,
    28309,
    28105,
    27896,
    27683,
    27466,
    27244,
    27019,
    26789,
    26556,
    26318,
    26077,
    25831,
    25582,
    25329,
    25072,
    24811,
    24546,
    24278,
    24006,
    23731,
    23452,
    23169,
    22883,
    22594,
    22301,
    22004,
    21705,
    21402,
    21096,
    20787,
    20474,
    20159,
    19840,
    19519,
    19194,
    18867,
    18537,
    18204,
    17868,
    17530,
    17189,
    16845,
    16499,
    16150,
    15799,
    15446,
    15090,
    14732,
    14372,
    14009,
    13645,
    13278,
    12909,
    12539,
    12166,
    11792,
    11416,
    11038,
    10659,
    10278,
    9895,
    9511,
    9126,
    8739,
    8351,
    7961,
    7571,
    7179,
    6786,
    6392,
    5997,
    5601,
    5205,
    4807,
    4409,
    4011,
    3611,
    3211,
    2811,
    2410,
    2009,
    1607,
    1206,
    804,
    402,
    0,
    -402,
    -804,
    -1206,
    -1607,
    -2009,
    -2410,
    -2811,
    -3211,
    -3611,
    -4011,
    -4409,
    -4807,
    -5205,
    -5601,
    -5997,
    -6392,
    -6786,
    -7179,
    -7571,
    -7961,
    -8351,
    -8739,
    -9126,
    -9511,
    -9895,
    -10278,
    -10659,
    -11038,
    -11416,
    -11792,
    -12166,
    -12539,
    -12909,
    -13278,
    -13645,
    -14009,
    -14372,
    -14732,
    -15090,
    -15446,
    -15799,
    -16150,
    -16499,
    -16845,
    -17189,
    -17530,
    -17868,
    -18204,
    -18537,
    -18867,
    -19194,
    -19519,
    -19840,
    -20159,
    -20474,
    -20787,
    -21096,
    -21402,
    -21705,
    -22004,
    -22301,
    -22594,
    -22883,
    -23169,
    -23452,
    -23731,
    -24006,
    -24278,
    -24546,
    -24811,
    -25072,
    -25329,
    -25582,
    -25831,
    -26077,
    -26318,
    -26556,
    -26789,
    -27019,
    -27244,
    -27466,
    -27683,
    -27896,
    -28105,
    -28309,
    -28510,
    -28706,
    -28897,
    -29085,
    -29268,
    -29446,
    -29621,
    -29790,
    -29955,
    -30116,
    -30272,
    -30424,
    -30571,
    -30713,
    -30851,
    -30984,
    -31113,
    -31236,
    -31356,
    -31470,
    -31580,
    -31684,
    -31785,
    -31880,
    -31970,
    -32056,
    -32137,
    -32213,
    -32284,
    -32350,
    -32412,
    -32468,
    -32520,
    -32567,
    -32609,
    -32646,
    -32678,
    -32705,
    -32727,
    -32744,
    -32757,
    -32764,
};

/* Bit reverse table for a single Byte.
 * Computed with:
 * awk 'BEGIN{for (i=0;i<256;i++) {o = 0; for (j=0;j<8;j++)
 *           {if(and(lshift(1,j), i)){o+= lshift(1, 7-j)}};
 *           printf("%d,", o);if(i%16==15){printf("\n")}else{printf(" ")}}}'
 */
static const uint8_t kBitReverseTable256[] = {
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
    1,
    129,
    65,
    193,
    33,
    161,
    97,
    225,
    17,
    145,
    81,
    209,
    49,
    177,
    113,
    241,
    9,
    137,
    73,
    201,
    41,
    169,
    105,
    233,
    25,
    153,
    89,
    217,
    57,
    185,
    121,
    249,
    5,
    133,
    69,
    197,
    37,
    165,
    101,
    229,
    21,
    149,
    85,
    213,
    53,
    181,
    117,
    245,
    13,
    141,
    77,
    205,
    45,
    173,
    109,
    237,
    29,
    157,
    93,
    221,
    61,
    189,
    125,
    253,
    3,
    131,
    67,
    195,
    35,
    163,
    99,
    227,
    19,
    147,
    83,
    211,
    51,
    179,
    115,
    243,
    11,
    139,
    75,
    203,
    43,
    171,
    107,
    235,
    27,
    155,
    91,
    219,
    59,
    187,
    123,
    251,
    7,
    135,
    71,
    199,
    39,
    167,
    103,
    231,
    23,
    151,
    87,
    215,
    55,
    183,
    119,
    247,
    15,
    143,
    79,
    207,
    47,
    175,
    111,
    239,
    31,
    159,
    95,
    223,
    63,
    191,
    127,
    255,
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
/* Complex 256-bin FFT. real/complex values are interleaved in samples */
static int32_t FFT_256(int16_t *samples)
{
    const int32_t kNumSamples = 256;
    int32_t sample_index;
    int32_t sub_fft_length;
    int32_t sine_table_log_step;
    int32_t total_right_shift = 0;

    /* Bit-reversal of elements in sample array */
    for (sample_index = 1; sample_index < kNumSamples; sample_index++)
    {
        int32_t reverse_index = (int32_t)kBitReverseTable256[sample_index];
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
            int16_t weight_real = kSine512[phase_index + N_WAVE / 4];
            int16_t weight_imag = -kSine512[phase_index];

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

int32_t FFTR_512(int16_t *samples)
{
    const int32_t kComplexFFTLength = 256;
    int32_t k;
    int32_t total_right_shift;

    total_right_shift = FFT_256(samples);
    total_right_shift++; /* Always do a right-shift */

    /* Final butterfly pass, ignoring bin 0 and bin 256 (which does not exist) */
    for (k = 1; k < kComplexFFTLength / 2; k++)
    {
        /* Assumes kLogNumSamples == LOG2_N_WAVE */
        int16_t weight_real = kSine512[k + N_WAVE / 4 + N_WAVE / 4];
        int16_t weight_imag = -kSine512[k + N_WAVE / 4];

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

int32_t FFTR_512_GetRomSize(void)
{
    return (int32_t)(sizeof(kSine512) + sizeof(kBitReverseTable256));
}
