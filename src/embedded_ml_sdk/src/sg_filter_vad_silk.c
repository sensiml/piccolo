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




/***********************************************************************
Copyright (c) 2006-2011, Skype Limited. All rights reserved.
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
- Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright
notice, this list of conditions and the following disclaimer in the
documentation and/or other materials provided with the distribution.
- Neither the name of Internet Society, IETF or IETF Trust, nor the
names of specific contributors, may be used to endorse or promote
products derived from this software without specific prior written
permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
***********************************************************************/

/*
Note: The following code is from opus
   From https://opus-codec.org/downloads/

The following files are modified and copied here

From  opus-1.3.1/silk folder
  1.VAD.c
  2.Inlines.h - copied only a used in VAD
  3.sigm_Q15.c
  4.lin2log.c
  5.ana_filt_bank_1.c

From opus-1.3.1/silk, celt, include folders are copied into vad_silk.h

  6.vad.h (called define.h in opus)
  7.typedef.h
  8.tuning_parameters.h
  9.SigProc_FIX.h
  10.macros.h


*/

#include "kbalgorithms.h"

#include "vad_silk.h"

#define SILK_MOVING_AVG_SIZE (2 * 15) // 30ms*15*2 = 2*450ms of speech

static silk_encoder_state encState;
static int32_t remaining_audio_length = 0;
static int8_t silk_vad_flags[SILK_MOVING_AVG_SIZE];
static int32_t silk_vad_counter = 0;

void reset_sg_filter_vad_silk()
{
}

int32_t sg_filter_vad_silk_init(void)
{
    memset(&encState, 0, sizeof(encState));
    encState.frame_length = SILK_FRAME_LENGTH; // 10ms @16000 Hz
    encState.fs_kHz = SILK_AUDIO_SAMPLE_RATE;  // 16kH sampling rate
    silk_VAD_Init(&encState.sVAD);
    encState.init_flag = 1;
    remaining_audio_length = 0;
    silk_vad_counter = 0;
    return 0;
}
int32_t get_silk_sum(int32_t vad_flag, int8_t *vad_flags, int32_t buff_size)
{
    int32_t sum = 0;
    int32_t start_count;

    silk_vad_flags[silk_vad_counter++] = vad_flag;
    if (silk_vad_counter >= buff_size)
        silk_vad_counter = 0;

    start_count = silk_vad_counter;
    for (int32_t i = 0; i < buff_size; i++)
    {
        sum += silk_vad_flags[start_count++];
        if (start_count >= buff_size)
            start_count = 0;
    }
    // printf(" %d ", sum);
    return sum;
}
void clear_silk_vad(int32_t buff_size)
{
    int32_t counter = silk_vad_counter;
    // clear only half of the buffer
    for (int32_t i = 0; i < buff_size; i++)
    {
        silk_vad_flags[counter++] = 0;
        if (counter >= buff_size)
            counter = 0;
    }
    return;
}

/**
 * Return 0 if any of the data is outside the threshold range.
 * Return 1 if the segment isn't filtered out.
 */
int32_t sg_filter_vad_silk(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params)
{
#define SG_FILTER_VAD_SILK_NUM_PARAMS 2
#define SILK_THRESHOLD_PARAM_IDX 0
#define SILK_CIRC_BUFFER_PARAM_IDX 1

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
    int32_t threshold = (int32_t)params->data[SILK_THRESHOLD_PARAM_IDX];
    int32_t buff_size = (int32_t)params->data[SILK_CIRC_BUFFER_PARAM_IDX];

    // Note: buff_size should be greater than threshold, else the sum will never be threshold
    if (buff_size < (threshold + 2 * 1))
        buff_size = (threshold + 2 * 1);
    if (buff_size > SILK_MOVING_AVG_SIZE)
        buff_size = SILK_MOVING_AVG_SIZE;

    // initialize if not done
    if (encState.init_flag == 0)
    {
        sg_filter_vad_silk_init();
    }

    // copy the data into audio frame only if it fits the frame length
    for (i = remaining_audio_length; i < kb_model->sg_length;)
    {
        if ((kb_model->sg_length - i) >= SILK_FRAME_LENGTH)
            z = SILK_FRAME_LENGTH; // full frame
        else
            z = kb_model->sg_length - i; // partial frame
        for (j = remaining_audio_length; j < z; j++)
        {
            // since audio is 2 bytes per sample
            encState.indata[j] = rb_read(rb, base_index);
        }
        i += (SILK_FRAME_LENGTH - remaining_audio_length);
        if (z == SILK_FRAME_LENGTH)
        {
            remaining_audio_length = 0;
            vad_flag = silk_VAD_GetSA_Q8_c(&encState, encState.indata);
            if (encState.speech_activity_Q8 < SILK_FIX_CONST(SPEECH_ACTIVITY_DTX_THRES, 8))
            {
                vad_flag = 0;
            }
            else
            {
                vad_flag = 1;
            }

            sum = get_silk_sum(vad_flag, silk_vad_flags, buff_size);
            if (sum > threshold)
            {
                ret_val = 1;
                // clear vad flags - only half the buffer
                clear_silk_vad(buff_size / 2);
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
// copied from entcode.c
// modified

#if 1 //! defined(EC_CLZ)
/*This is a fallback for systems where we don't know how to access
   a BSR or CLZ instruction (see ecintrin.h).
  If you are optimizing Opus on a new platform and it has a native CLZ or
   BZR (e.g. cell, MIPS, x86, etc) then making it available to Opus will be
   an easy performance win.*/
static int32_t ec_ilog(int32_t _v)
{
    /*On a Pentium M, this branchless version tested as the fastest on
       1,000,000,000 random 32-bit integers, edging out a similar version with
       branches, and a 256-entry LUT version.*/
    int32_t ret;
    int32_t m;
    ret = !!_v;
    m = !!(_v & 0xFFFF0000) << 4;
    _v >>= m;
    ret |= m;
    m = !!(_v & 0xFF00) << 3;
    _v >>= m;
    ret |= m;
    m = !!(_v & 0xF0) << 2;
    _v >>= m;
    ret |= m;
    m = !!(_v & 0xC) << 1;
    _v >>= m;
    ret |= m;
    ret += !!(_v & 0x2);
    return ret;
}

#define EC_ILOG(_x) (ec_ilog(_x))
static int32_t silk_CLZ32(int32_t in32)
{
    return in32 ? 32 - EC_ILOG(in32) : 32;
}

#endif

/*****************************************************************************/
// copied from inlines.h

/* get number of leading zeros and fractional part (the bits right after the leading one */
static void silk_CLZ_FRAC(
    int32_t in,      /* I  input                               */
    int32_t *lz,     /* O  number of leading zeros             */
    int32_t *frac_Q7 /* O  the 7 bits right after the leading one */
)
{
    int32_t lzeros = silk_CLZ32(in);

    *lz = lzeros;
    *frac_Q7 = silk_ROR32(in, 24 - lzeros) & 0x7f;
}

/* Approximation of square root                                          */
/* Accuracy: < +/- 10%  for output values > 15                           */
/*           < +/- 2.5% for output values > 120                          */
static int32_t silk_SQRT_APPROX(int32_t x)
{
    int32_t y, lz, frac_Q7;

    if (x <= 0)
    {
        return 0;
    }

    silk_CLZ_FRAC(x, &lz, &frac_Q7);

    if (lz & 1)
    {
        y = 32768;
    }
    else
    {
        y = 46214; /* 46214 = sqrt(2) * 32768 */
    }

    /* get scaling right */
    y >>= silk_RSHIFT(lz, 1);

    /* increment using fractional part of input */
    y = silk_SMLAWB(y, y, silk_SMULBB(213, frac_Q7));

    return y;
}

/*****************************************************************************/
// copied from sigm_Q15.c

/* Approximate sigmoid function */

/* fprintf(1, '%d, ', round(1024 * ([1 ./ (1 + exp(-(1:5))), 1] - 1 ./ (1 + exp(-(0:5)))))); */
static const int32_t sigm_LUT_slope_Q10[6] = {
    237, 153, 73, 30, 12, 7};
/* fprintf(1, '%d, ', round(32767 * 1 ./ (1 + exp(-(0:5))))); */
static const int32_t sigm_LUT_pos_Q15[6] = {
    16384, 23955, 28861, 31213, 32178, 32548};
/* fprintf(1, '%d, ', round(32767 * 1 ./ (1 + exp((0:5))))); */
static const int32_t sigm_LUT_neg_Q15[6] = {
    16384, 8812, 3906, 1554, 589, 219};

int32_t silk_sigm_Q15(
    int32_t in_Q5 /* I                                                                */
)
{
    int32_t ind;

    if (in_Q5 < 0)
    {
        /* Negative input */
        in_Q5 = -in_Q5;
        if (in_Q5 >= 6 * 32)
        {
            return 0; /* Clip */
        }
        else
        {
            /* Linear interpolation of look up table */
            ind = silk_RSHIFT(in_Q5, 5);
            return (sigm_LUT_neg_Q15[ind] - silk_SMULBB(sigm_LUT_slope_Q10[ind], in_Q5 & 0x1F));
        }
    }
    else
    {
        /* Positive input */
        if (in_Q5 >= 6 * 32)
        {
            return 32767; /* clip */
        }
        else
        {
            /* Linear interpolation of look up table */
            ind = silk_RSHIFT(in_Q5, 5);
            return (sigm_LUT_pos_Q15[ind] + silk_SMULBB(sigm_LUT_slope_Q10[ind], in_Q5 & 0x1F));
        }
    }
}

/*****************************************************************************/
// copied from lin2log.c

/* Approximation of 128 * log2() (very close inverse of silk_log2lin()) */
/* Convert input to a log scale    */
int32_t silk_lin2log(
    const int32_t inLin /* I  input in linear scale                                         */
)
{
    int32_t lz, frac_Q7;

    silk_CLZ_FRAC(inLin, &lz, &frac_Q7);

    /* Piece-wise parabolic approximation */
    return silk_ADD_LSHIFT32(silk_SMLAWB(frac_Q7, silk_MUL(frac_Q7, 128 - frac_Q7), 179), 31 - lz, 7);
}
/*****************************************************************************/
// copied from ana_filt_bank_1.c

/* Coefficients for 2-band filter bank based on first-order allpass filters */
static int16_t A_fb1_20 = 5394 << 1;
static int16_t A_fb1_21 = -24290; /* (int16_t)(20623 << 1) */

/* Split signal into two decimated bands using first-order allpass filters */
void silk_ana_filt_bank_1(
    const int16_t *in, /* I    Input signal [N]                                            */
    int32_t *S,        /* I/O  State vector [2]                                            */
    int16_t *outL,     /* O    Low band [N/2]                                              */
    int16_t *outH,     /* O    High band [N/2]                                             */
    const int32_t N    /* I    Number of input samples                                     */
)
{
    int32_t k, N2 = silk_RSHIFT(N, 1);
    int32_t in32, X, Y, out_1, out_2;

    /* Internal variables and state are in Q10 format */
    for (k = 0; k < N2; k++)
    {
        /* Convert to Q10 */
        in32 = silk_LSHIFT((int32_t)in[2 * k], 10);

        /* All-pass section for even input sample */
        Y = silk_SUB32(in32, S[0]);
        X = silk_SMLAWB(Y, Y, A_fb1_21);
        out_1 = silk_ADD32(S[0], X);
        S[0] = silk_ADD32(in32, X);

        /* Convert to Q10 */
        in32 = silk_LSHIFT((int32_t)in[2 * k + 1], 10);

        /* All-pass section for odd input sample, and add to output of previous section */
        Y = silk_SUB32(in32, S[1]);
        X = silk_SMULWB(Y, A_fb1_20);
        out_2 = silk_ADD32(S[1], X);
        S[1] = silk_ADD32(in32, X);

        /* Add/subtract, convert back to int16 and store to output */
        outL[k] = (int16_t)silk_SAT16(silk_RSHIFT_ROUND(silk_ADD32(out_2, out_1), 11));
        outH[k] = (int16_t)silk_SAT16(silk_RSHIFT_ROUND(silk_SUB32(out_2, out_1), 11));
    }
}
/*****************************************************************************/

/* Silk VAD noise level estimation */
#if !defined(OPUS_X86_MAY_HAVE_SSE4_1)
static void silk_VAD_GetNoiseLevels(
    const int32_t pX[VAD_N_BANDS], /* I    subband energies                            */
    silk_VAD_state *psSilk_VAD     /* I/O  Pointer to Silk VAD state                   */
);
#endif

/**********************************/
/* Initialization of the Silk VAD */
/**********************************/
int32_t silk_VAD_Init(                           /* O    Return value, 0 if success                  */
                      silk_VAD_state *psSilk_VAD /* I/O  Pointer to Silk VAD state                   */
)
{
    int32_t b, ret = 0;

    /* reset state memory */
    silk_memset(psSilk_VAD, 0, sizeof(silk_VAD_state));

    /* init noise levels */
    /* Initialize array with approx pink noise levels (psd proportional to inverse of frequency) */
    for (b = 0; b < VAD_N_BANDS; b++)
    {
        psSilk_VAD->NoiseLevelBias[b] = silk_max_32(silk_DIV32_16(VAD_NOISE_LEVELS_BIAS, b + 1), 1);
    }

    /* Initialize state */
    for (b = 0; b < VAD_N_BANDS; b++)
    {
        psSilk_VAD->NL[b] = silk_MUL(100, psSilk_VAD->NoiseLevelBias[b]);
        psSilk_VAD->inv_NL[b] = silk_DIV32(silk_int32_MAX, psSilk_VAD->NL[b]);
    }
    psSilk_VAD->counter = 15;

    /* init smoothed energy-to-noise ratio*/
    for (b = 0; b < VAD_N_BANDS; b++)
    {
        psSilk_VAD->NrgRatioSmth_Q8[b] = 100 * 256; /* 100 * 256 --> 20 dB SNR */
    }

    return (ret);
}

/* Weighting factors for tilt measure */
static const int32_t tiltWeights[VAD_N_BANDS] = {30000, 6000, -12000, -12000};

/***************************************/
/* Get the speech activity level in Q8 */
/***************************************/
int32_t silk_VAD_GetSA_Q8_c(                            /* O    Return value, 0 if success                  */
                            silk_encoder_state *psEncC, /* I/O  Encoder state                               */
                            const int16_t pIn[]         /* I    PCM input                                   */
)
{
    int32_t SA_Q15, pSNR_dB_Q7, input_tilt;
    int32_t decimated_framelength1, decimated_framelength2;
    int32_t decimated_framelength;
    int32_t dec_subframe_length, dec_subframe_offset, SNR_Q7, i, b, s;
    int32_t sumSquared, smooth_coef_Q16;
    int16_t HPstateTmp;
    // VARDECL( int16_t, X );
    int32_t Xnrg[VAD_N_BANDS];
    int32_t NrgToNoiseRatio_Q8[VAD_N_BANDS];
    int32_t speech_nrg, x_tmp;
    int32_t X_offset[VAD_N_BANDS];
    int32_t ret = 0;
    silk_VAD_state *psSilk_VAD = &psEncC->sVAD;
    // SAVE_STACK;

    /* Safety checks */
    // silk_assert( VAD_N_BANDS == 4 );
    // silk_assert( MAX_FRAME_LENGTH >= psEncC->frame_length );
    // silk_assert( psEncC->frame_length <= 512 );
    // silk_assert( psEncC->frame_length == 8 * silk_RSHIFT( psEncC->frame_length, 3 ) );

    /***********************/
    /* Filter and Decimate */
    /***********************/
    decimated_framelength1 = silk_RSHIFT(psEncC->frame_length, 1);
    decimated_framelength2 = silk_RSHIFT(psEncC->frame_length, 2);
    decimated_framelength = silk_RSHIFT(psEncC->frame_length, 3);
    /* Decimate into 4 bands:
       0       L      3L       L              3L                             5L
               -      --       -              --                             --
               8       8       2               4                              4

       [0-1 kHz| temp. |1-2 kHz|    2-4 kHz    |            4-8 kHz           |

       They're arranged to allow the minimal ( frame_length / 4 ) extra
       scratch space during the downsampling process */
    X_offset[0] = 0;
    X_offset[1] = decimated_framelength + decimated_framelength2;
    X_offset[2] = X_offset[1] + decimated_framelength;
    X_offset[3] = X_offset[2] + decimated_framelength2;
    // ALLOC( X, X_offset[ 3 ] + decimated_framelength1, int16_t );
    int16_t X[2 * FRAME_LENGTH]; // this is defined

    /* 0-8 kHz to 0-4 kHz and 4-8 kHz */
    silk_ana_filt_bank_1(pIn, &psSilk_VAD->AnaState[0],
                         X, &X[X_offset[3]], psEncC->frame_length);

    /* 0-4 kHz to 0-2 kHz and 2-4 kHz */
    silk_ana_filt_bank_1(X, &psSilk_VAD->AnaState1[0],
                         X, &X[X_offset[2]], decimated_framelength1);

    /* 0-2 kHz to 0-1 kHz and 1-2 kHz */
    silk_ana_filt_bank_1(X, &psSilk_VAD->AnaState2[0],
                         X, &X[X_offset[1]], decimated_framelength2);

    /*********************************************/
    /* HP filter on lowest band (differentiator) */
    /*********************************************/
    X[decimated_framelength - 1] = silk_RSHIFT(X[decimated_framelength - 1], 1);
    HPstateTmp = X[decimated_framelength - 1];
    for (i = decimated_framelength - 1; i > 0; i--)
    {
        X[i - 1] = silk_RSHIFT(X[i - 1], 1);
        X[i] -= X[i - 1];
    }
    X[0] -= psSilk_VAD->HPstate;
    psSilk_VAD->HPstate = HPstateTmp;

    /*************************************/
    /* Calculate the energy in each band */
    /*************************************/
    for (b = 0; b < VAD_N_BANDS; b++)
    {
        /* Find the decimated framelength in the non-uniformly divided bands */
        decimated_framelength = silk_RSHIFT(psEncC->frame_length, silk_min_int(VAD_N_BANDS - b, VAD_N_BANDS - 1));

        /* Split length into subframe lengths */
        dec_subframe_length = silk_RSHIFT(decimated_framelength, VAD_INTERNAL_SUBFRAMES_LOG2);
        dec_subframe_offset = 0;

        /* Compute energy per sub-frame */
        /* initialize with summed energy of last subframe */
        Xnrg[b] = psSilk_VAD->XnrgSubfr[b];
        for (s = 0; s < VAD_INTERNAL_SUBFRAMES; s++)
        {
            sumSquared = 0;
            for (i = 0; i < dec_subframe_length; i++)
            {
                /* The energy will be less than dec_subframe_length * ( silk_int16_MIN / 8 ) ^ 2.            */
                /* Therefore we can accumulate with no risk of overflow (unless dec_subframe_length > 128)  */
                x_tmp = silk_RSHIFT(
                    X[X_offset[b] + i + dec_subframe_offset], 3);
                sumSquared = silk_SMLABB(sumSquared, x_tmp, x_tmp);

                /* Safety check */
                // silk_assert( sumSquared >= 0 );
            }

            /* Add/saturate summed energy of current subframe */
            if (s < VAD_INTERNAL_SUBFRAMES - 1)
            {
                Xnrg[b] = silk_ADD_POS_SAT32(Xnrg[b], sumSquared);
            }
            else
            {
                /* Look-ahead subframe */
                Xnrg[b] = silk_ADD_POS_SAT32(Xnrg[b], silk_RSHIFT(sumSquared, 1));
            }

            dec_subframe_offset += dec_subframe_length;
        }
        psSilk_VAD->XnrgSubfr[b] = sumSquared;
    }

    /********************/
    /* Noise estimation */
    /********************/
    silk_VAD_GetNoiseLevels(&Xnrg[0], psSilk_VAD);

    /***********************************************/
    /* Signal-plus-noise to noise ratio estimation */
    /***********************************************/
    sumSquared = 0;
    input_tilt = 0;
    for (b = 0; b < VAD_N_BANDS; b++)
    {
        speech_nrg = Xnrg[b] - psSilk_VAD->NL[b];
        if (speech_nrg > 0)
        {
            /* Divide, with sufficient resolution */
            if ((Xnrg[b] & 0xFF800000) == 0)
            {
                NrgToNoiseRatio_Q8[b] = silk_DIV32(silk_LSHIFT(Xnrg[b], 8), psSilk_VAD->NL[b] + 1);
            }
            else
            {
                NrgToNoiseRatio_Q8[b] = silk_DIV32(Xnrg[b], silk_RSHIFT(psSilk_VAD->NL[b], 8) + 1);
            }

            /* Convert to log domain */
            SNR_Q7 = silk_lin2log(NrgToNoiseRatio_Q8[b]) - 8 * 128;

            /* Sum-of-squares */
            sumSquared = silk_SMLABB(sumSquared, SNR_Q7, SNR_Q7); /* Q14 */

            /* Tilt measure */
            if (speech_nrg < ((int32_t)1 << 20))
            {
                /* Scale down SNR value for small subband speech energies */
                SNR_Q7 = silk_SMULWB(silk_LSHIFT(silk_SQRT_APPROX(speech_nrg), 6), SNR_Q7);
            }
            input_tilt = silk_SMLAWB(input_tilt, tiltWeights[b], SNR_Q7);
        }
        else
        {
            NrgToNoiseRatio_Q8[b] = 256;
        }
    }

    /* Mean-of-squares */
    sumSquared = silk_DIV32_16(sumSquared, VAD_N_BANDS); /* Q14 */

    /* Root-mean-square approximation, scale to dBs, and write to output pointer */
    pSNR_dB_Q7 = (int16_t)(3 * silk_SQRT_APPROX(sumSquared)); /* Q7 */

    /*********************************/
    /* Speech Probability Estimation */
    /*********************************/
    SA_Q15 = silk_sigm_Q15(silk_SMULWB(VAD_SNR_FACTOR_Q16, pSNR_dB_Q7) - VAD_NEGATIVE_OFFSET_Q5);

    /**************************/
    /* Frequency Tilt Measure */
    /**************************/
    psEncC->input_tilt_Q15 = silk_LSHIFT(silk_sigm_Q15(input_tilt) - 16384, 1);

    /**************************************************/
    /* Scale the sigmoid output based on power levels */
    /**************************************************/
    speech_nrg = 0;
    for (b = 0; b < VAD_N_BANDS; b++)
    {
        /* Accumulate signal-without-noise energies, higher frequency bands have more weight */
        speech_nrg += (b + 1) * silk_RSHIFT(Xnrg[b] - psSilk_VAD->NL[b], 4);
    }

    if (psEncC->frame_length == 20 * psEncC->fs_kHz)
    {
        speech_nrg = silk_RSHIFT32(speech_nrg, 1);
    }
    /* Power scaling */
    if (speech_nrg <= 0)
    {
        SA_Q15 = silk_RSHIFT(SA_Q15, 1);
    }
    else if (speech_nrg < 16384)
    {
        speech_nrg = silk_LSHIFT32(speech_nrg, 16);

        /* square-root */
        speech_nrg = silk_SQRT_APPROX(speech_nrg);
        SA_Q15 = silk_SMULWB(32768 + speech_nrg, SA_Q15);
    }

    /* Copy the resulting speech activity in Q8 */
    psEncC->speech_activity_Q8 = silk_min_int(silk_RSHIFT(SA_Q15, 7), silk_uint8_MAX);

    /***********************************/
    /* Energy Level and SNR estimation */
    /***********************************/
    /* Smoothing coefficient */
    smooth_coef_Q16 = silk_SMULWB(VAD_SNR_SMOOTH_COEF_Q18, silk_SMULWB((int32_t)SA_Q15, SA_Q15));

    if (psEncC->frame_length == 10 * psEncC->fs_kHz)
    {
        smooth_coef_Q16 >>= 1;
    }

    for (b = 0; b < VAD_N_BANDS; b++)
    {
        /* compute smoothed energy-to-noise ratio per band */
        psSilk_VAD->NrgRatioSmth_Q8[b] = silk_SMLAWB(psSilk_VAD->NrgRatioSmth_Q8[b],
                                                     NrgToNoiseRatio_Q8[b] - psSilk_VAD->NrgRatioSmth_Q8[b], smooth_coef_Q16);

        /* signal to noise ratio in dB per band */
        SNR_Q7 = 3 * (silk_lin2log(psSilk_VAD->NrgRatioSmth_Q8[b]) - 8 * 128);
        /* quality = sigmoid( 0.25 * ( SNR_dB - 16 ) ); */
        psEncC->input_quality_bands_Q15[b] = silk_sigm_Q15(silk_RSHIFT(SNR_Q7 - 16 * 128, 4));
    }

    // RESTORE_STACK;
    return (ret);
}

/**************************/
/* Noise level estimation */
/**************************/
// # if  !defined(OPUS_X86_MAY_HAVE_SSE4_1)
// static OPUS_INLINE
// #endif
void silk_VAD_GetNoiseLevels(
    const int32_t pX[VAD_N_BANDS], /* I    subband energies                            */
    silk_VAD_state *psSilk_VAD     /* I/O  Pointer to Silk VAD state                   */
)
{
    int32_t k;
    int32_t nl, nrg, inv_nrg;
    int32_t coef, min_coef;

    /* Initially faster smoothing */
    if (psSilk_VAD->counter < 1000)
    { /* 1000 = 20 sec */
        min_coef = silk_DIV32_16(silk_int16_MAX, silk_RSHIFT(psSilk_VAD->counter, 4) + 1);
        /* Increment frame counter */
        psSilk_VAD->counter++;
    }
    else
    {
        min_coef = 0;
    }

    for (k = 0; k < VAD_N_BANDS; k++)
    {
        /* Get old noise level estimate for current band */
        nl = psSilk_VAD->NL[k];
        // silk_assert( nl >= 0 );

        /* Add bias */
        nrg = silk_ADD_POS_SAT32(pX[k], psSilk_VAD->NoiseLevelBias[k]);
        // silk_assert( nrg > 0 );

        /* Invert energies */
        inv_nrg = silk_DIV32(silk_int32_MAX, nrg);
        // silk_assert( inv_nrg >= 0 );

        /* Less update when subband energy is high */
        if (nrg > silk_LSHIFT(nl, 3))
        {
            coef = VAD_NOISE_LEVEL_SMOOTH_COEF_Q16 >> 3;
        }
        else if (nrg < nl)
        {
            coef = VAD_NOISE_LEVEL_SMOOTH_COEF_Q16;
        }
        else
        {
            coef = silk_SMULWB(silk_SMULWW(inv_nrg, nl), VAD_NOISE_LEVEL_SMOOTH_COEF_Q16 << 1);
        }

        /* Initially faster smoothing */
        coef = silk_max_int(coef, min_coef);

        /* Smooth inverse energies */
        psSilk_VAD->inv_NL[k] = silk_SMLAWB(psSilk_VAD->inv_NL[k], inv_nrg - psSilk_VAD->inv_NL[k], coef);
        // silk_assert( psSilk_VAD->inv_NL[ k ] >= 0 );

        /* Compute noise level by inverting again */
        nl = silk_DIV32(silk_int32_MAX, psSilk_VAD->inv_NL[k]);
        // silk_assert( nl >= 0 );

        /* Limit noise levels (guarantee 7 bits of head room) */
        nl = silk_min(nl, 0x00FFFFFF);

        /* Store as part of state */
        psSilk_VAD->NL[k] = nl;
    }
}
