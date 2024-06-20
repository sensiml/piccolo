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

#ifndef _VAD_SILK_H_
#define _VAD_SILK_H_

#include <stdint.h>

//Note: 
//Replaced   
//   opus_int16 with int16_t,
//   opus_uint16 with uint16_t,
//   opus_int32 with int32_t,
//   opus_uint32 with uint32_t,
//   opus_int with int32_t,
//   opus_int64 with int64_t,
//   opus_uint64 with uint64_t,

//Removed OPUS_INLINE, OPUS_EXPORT 
//Removed silk_assert
#define silk_assert  
#define SILK_AUDIO_SAMPLE_RATE   (16000)
#define SILK_FRAME_LENGTH        (3*10*16)   //in samples - should be 30ms

//Note: this is required for all 
#define MAX_FRAME_LENGTH  1000 //???
#define FRAME_LENGTH (SILK_FRAME_LENGTH) 


/*****************************************************************************/
//copied from typedef.h
//modified 

#ifndef SILK_TYPEDEF_H
#define SILK_TYPEDEF_H

//#define silk_int64_MAX   ((int64_t)0x7FFFFFFFFFFFFFFFLL)   /*  2^63 - 1 */
//#define silk_int64_MIN   ((int64_t)0x8000000000000000LL)   /* -2^63 */
#define silk_int32_MAX   0x7FFFFFFF                           /*  2^31 - 1 =  2147483647 */
#define silk_int32_MIN   ((int32_t)0x80000000)             /* -2^31     = -2147483648 */
#define silk_int16_MAX   0x7FFF                               /*  2^15 - 1 =  32767 */
#define silk_int16_MIN   ((int16_t)0x8000)                 /* -2^15     = -32768 */
#define silk_int8_MAX    0x7F                                 /*  2^7 - 1  =  127 */
#define silk_int8_MIN    ((opus_int8)0x80)                    /* -2^7      = -128 */
#define silk_uint8_MAX   0xFF                                 /*  2^8 - 1 = 255 */

#endif /* SILK_TYPEDEF_H */

/*****************************************************************************/
//copied from tuning_parameters.h
//modified

/* VAD threshold */
#define SPEECH_ACTIVITY_DTX_THRES                       0.05f


/*****************************************************************************/
//copied from define.h, structs.h
//modified 

#ifndef VAD_H
#define VAD_H


/***************************/
/* Voice activity detector */
/***************************/
#define VAD_N_BANDS                             4

#define VAD_INTERNAL_SUBFRAMES_LOG2             2
#define VAD_INTERNAL_SUBFRAMES                  ( 1 << VAD_INTERNAL_SUBFRAMES_LOG2 )

#define VAD_NOISE_LEVEL_SMOOTH_COEF_Q16         1024    /* Must be <  4096 */
#define VAD_NOISE_LEVELS_BIAS                   50

/* Sigmoid settings */
#define VAD_NEGATIVE_OFFSET_Q5                  128     /* sigmoid is 0 at -128 */
#define VAD_SNR_FACTOR_Q16                      45000

/* smoothing for SNR measurement */
#define VAD_SNR_SMOOTH_COEF_Q18                 4096

/********************************/
/* VAD state                    */
/********************************/
typedef struct {
    int32_t                  AnaState[ 2 ];                  /* Analysis filterbank state: 0-8 kHz                                   */
    int32_t                  AnaState1[ 2 ];                 /* Analysis filterbank state: 0-4 kHz                                   */
    int32_t                  AnaState2[ 2 ];                 /* Analysis filterbank state: 0-2 kHz                                   */
    int32_t                  XnrgSubfr[ VAD_N_BANDS ];       /* Subframe energies                                                    */
    int32_t                  NrgRatioSmth_Q8[ VAD_N_BANDS ]; /* Smoothed energy level in each band                                   */
    int16_t                  HPstate;                        /* State of differentiator in the lowest band                           */
    int32_t                  NL[ VAD_N_BANDS ];              /* Noise energy level in each band                                      */
    int32_t                  inv_NL[ VAD_N_BANDS ];          /* Inverse noise energy level in each band                              */
    int32_t                  NoiseLevelBias[ VAD_N_BANDS ];  /* Noise level estimator bias/offset                                    */
    int32_t                  counter;                        /* Frame counter used in the initial phase                              */
} silk_VAD_state;

typedef struct {
    silk_VAD_state               sVAD;                              /* Voice activity detector state                                    */
    int32_t                     speech_activity_Q8;                /* Speech activity                                                  */
    int32_t                     fs_kHz;                            /* Internal sampling frequency (kHz)                                */
    int32_t                     frame_length;                      /* Frame length (samples)                                           */
    int32_t                     input_quality_bands_Q15[ VAD_N_BANDS ];
    int32_t                     input_tilt_Q15;
    //added new for sensiml
    int32_t                     init_flag;
    int16_t                     indata[SILK_FRAME_LENGTH];
} silk_encoder_state;
/************/
/* Silk VAD */
/************/
/* Initialize the Silk VAD */
int32_t silk_VAD_Init(                                         /* O    Return value, 0 if success                  */
    silk_VAD_state              *psSilk_VAD                     /* I/O  Pointer to Silk VAD state                   */
);

/* Get speech activity level in Q8 */
int32_t silk_VAD_GetSA_Q8_c(                                   /* O    Return value, 0 if success                  */
    silk_encoder_state          *psEncC,                        /* I/O  Encoder state                               */
    const int16_t            pIn[]                           /* I    PCM input                                   */
);

#endif /* VAD_H */

/*****************************************************************************/
//copied from SigProc_FIX.h
//modified 

#ifndef SILK_SIGPROC_FIX_H
#define SILK_SIGPROC_FIX_H

#ifdef  __cplusplus
extern "C"
{
#endif

/********************************************************************/
/*                                MACROS                            */
/********************************************************************/

/* Rotate a32 right by 'rot' bits. Negative rot values result in rotating
   left. Output is 32bit int.
   Note: contemporary compilers recognize the C expression below and
   compile it into a 'ror' instruction if available. No need for ASM! */
static int32_t silk_ROR32( int32_t a32, int32_t rot )
{
    uint32_t x = (uint32_t) a32;
    uint32_t r = (uint32_t) rot;
    uint32_t m = (uint32_t) -rot;
    if( rot == 0 ) {
        return a32;
    } else if( rot < 0 ) {
        return (int32_t) ((x << m) | (x >> (32 - m)));
    } else {
        return (int32_t) ((x << (32 - r)) | (x >> r));
    }
}

/* Allocate int16_t aligned to 4-byte memory address */
#if EMBEDDED_ARM
#define silk_DWORD_ALIGN __attribute__((aligned(4)))
#else
#define silk_DWORD_ALIGN
#endif


/* Useful Macros that can be adjusted to other platforms */
//#define silk_memcpy(dest, src, size)        memcpy((dest), (src), (size))
#define silk_memset(dest, src, size)        memset((dest), (src), (size))
//#define silk_memmove(dest, src, size)       memmove((dest), (src), (size))

/* Fixed point macros */

/* (a32 * b32) output have to be 32bit int */
#define silk_MUL(a32, b32)                  ((a32) * (b32))

/* (a32 * b32) output have to be 32bit uint */
#define silk_MUL_uint(a32, b32)             silk_MUL(a32, b32)

/* a32 + (b32 * c32) output have to be 32bit int */
#define silk_MLA(a32, b32, c32)             silk_ADD32((a32),((b32) * (c32)))

/* a32 + (b32 * c32) output have to be 32bit uint */
#define silk_MLA_uint(a32, b32, c32)        silk_MLA(a32, b32, c32)

/* ((a32 >> 16)  * (b32 >> 16)) output have to be 32bit int */
#define silk_SMULTT(a32, b32)               (((a32) >> 16) * ((b32) >> 16))

/* a32 + ((a32 >> 16)  * (b32 >> 16)) output have to be 32bit int */
#define silk_SMLATT(a32, b32, c32)          silk_ADD32((a32),((b32) >> 16) * ((c32) >> 16))

#define silk_SMLALBB(a64, b16, c16)         silk_ADD64((a64),(int64_t)((int32_t)(b16) * (int32_t)(c16)))

/* (a32 * b32) */
#define silk_SMULL(a32, b32)                ((int64_t)(a32) * /*(int64_t)*/(b32))

/* Adds two signed 32-bit values in a way that can overflow, while not relying on undefined behaviour
   (just standard two's complement implementation-specific behaviour) */
#define silk_ADD32_ovflw(a, b)              ((int32_t)((uint32_t)(a) + (uint32_t)(b)))
/* Subtractss two signed 32-bit values in a way that can overflow, while not relying on undefined behaviour
   (just standard two's complement implementation-specific behaviour) */
#define silk_SUB32_ovflw(a, b)              ((int32_t)((uint32_t)(a) - (uint32_t)(b)))

/* Multiply-accumulate macros that allow overflow in the addition (ie, no asserts in debug mode) */
#define silk_MLA_ovflw(a32, b32, c32)       silk_ADD32_ovflw((a32), (uint32_t)(b32) * (uint32_t)(c32))
#define silk_SMLABB_ovflw(a32, b32, c32)    (silk_ADD32_ovflw((a32) , ((int32_t)((int16_t)(b32))) * (int32_t)((int16_t)(c32))))

#define silk_DIV32_16(a32, b16)             ((int32_t)((a32) / (b16)))
#define silk_DIV32(a32, b32)                ((int32_t)((a32) / (b32)))

/* These macros enables checking for overflow in silk_API_Debug.h*/
#define silk_ADD16(a, b)                    ((a) + (b))
#define silk_ADD32(a, b)                    ((a) + (b))
#define silk_ADD64(a, b)                    ((a) + (b))

#define silk_SUB16(a, b)                    ((a) - (b))
#define silk_SUB32(a, b)                    ((a) - (b))
#define silk_SUB64(a, b)                    ((a) - (b))

#define silk_SAT8(a)                        ((a) > silk_int8_MAX ? silk_int8_MAX  :       \
                                            ((a) < silk_int8_MIN ? silk_int8_MIN  : (a)))
#define silk_SAT16(a)                       ((a) > silk_int16_MAX ? silk_int16_MAX :      \
                                            ((a) < silk_int16_MIN ? silk_int16_MIN : (a)))
#define silk_SAT32(a)                       ((a) > silk_int32_MAX ? silk_int32_MAX :      \
                                            ((a) < silk_int32_MIN ? silk_int32_MIN : (a)))

#define silk_CHECK_FIT8(a)                  (a)
#define silk_CHECK_FIT16(a)                 (a)
#define silk_CHECK_FIT32(a)                 (a)

#define silk_ADD_SAT16(a, b)                (int16_t)silk_SAT16( silk_ADD32( (int32_t)(a), (b) ) )
#define silk_ADD_SAT64(a, b)                ((((a) + (b)) & 0x8000000000000000LL) == 0 ?                            \
                                            ((((a) & (b)) & 0x8000000000000000LL) != 0 ? silk_int64_MIN : (a)+(b)) : \
                                            ((((a) | (b)) & 0x8000000000000000LL) == 0 ? silk_int64_MAX : (a)+(b)) )

#define silk_SUB_SAT16(a, b)                (int16_t)silk_SAT16( silk_SUB32( (int32_t)(a), (b) ) )
#define silk_SUB_SAT64(a, b)                ((((a)-(b)) & 0x8000000000000000LL) == 0 ?                                               \
                                            (( (a) & ((b)^0x8000000000000000LL) & 0x8000000000000000LL) ? silk_int64_MIN : (a)-(b)) : \
                                            ((((a)^0x8000000000000000LL) & (b)  & 0x8000000000000000LL) ? silk_int64_MAX : (a)-(b)) )

/* Saturation for positive input values */
#define silk_POS_SAT32(a)                   ((a) > silk_int32_MAX ? silk_int32_MAX : (a))

/* Add with saturation for positive input values */
#define silk_ADD_POS_SAT8(a, b)             ((((a)+(b)) & 0x80)                 ? silk_int8_MAX  : ((a)+(b)))
#define silk_ADD_POS_SAT16(a, b)            ((((a)+(b)) & 0x8000)               ? silk_int16_MAX : ((a)+(b)))
#define silk_ADD_POS_SAT32(a, b)            ((((uint32_t)(a)+(uint32_t)(b)) & 0x80000000) ? silk_int32_MAX : ((a)+(b)))

#define silk_LSHIFT8(a, shift)              ((opus_int8)((opus_uint8)(a)<<(shift)))         /* shift >= 0, shift < 8  */
#define silk_LSHIFT16(a, shift)             ((int16_t)((uint16_t)(a)<<(shift)))       /* shift >= 0, shift < 16 */
#define silk_LSHIFT32(a, shift)             ((int32_t)((uint32_t)(a)<<(shift)))       /* shift >= 0, shift < 32 */
#define silk_LSHIFT64(a, shift)             ((int64_t)((uint64_t)(a)<<(shift)))       /* shift >= 0, shift < 64 */
#define silk_LSHIFT(a, shift)               silk_LSHIFT32(a, shift)                         /* shift >= 0, shift < 32 */

#define silk_RSHIFT8(a, shift)              ((a)>>(shift))                                  /* shift >= 0, shift < 8  */
#define silk_RSHIFT16(a, shift)             ((a)>>(shift))                                  /* shift >= 0, shift < 16 */
#define silk_RSHIFT32(a, shift)             ((a)>>(shift))                                  /* shift >= 0, shift < 32 */
#define silk_RSHIFT64(a, shift)             ((a)>>(shift))                                  /* shift >= 0, shift < 64 */
#define silk_RSHIFT(a, shift)               silk_RSHIFT32(a, shift)                         /* shift >= 0, shift < 32 */

/* saturates before shifting */
#define silk_LSHIFT_SAT32(a, shift)         (silk_LSHIFT32( silk_LIMIT( (a), silk_RSHIFT32( silk_int32_MIN, (shift) ), \
                                                    silk_RSHIFT32( silk_int32_MAX, (shift) ) ), (shift) ))

#define silk_LSHIFT_ovflw(a, shift)         ((int32_t)((uint32_t)(a) << (shift)))     /* shift >= 0, allowed to overflow */
#define silk_LSHIFT_uint(a, shift)          ((a) << (shift))                                /* shift >= 0 */
#define silk_RSHIFT_uint(a, shift)          ((a) >> (shift))                                /* shift >= 0 */

#define silk_ADD_LSHIFT(a, b, shift)        ((a) + silk_LSHIFT((b), (shift)))               /* shift >= 0 */
#define silk_ADD_LSHIFT32(a, b, shift)      silk_ADD32((a), silk_LSHIFT32((b), (shift)))    /* shift >= 0 */
#define silk_ADD_LSHIFT_uint(a, b, shift)   ((a) + silk_LSHIFT_uint((b), (shift)))          /* shift >= 0 */
#define silk_ADD_RSHIFT(a, b, shift)        ((a) + silk_RSHIFT((b), (shift)))               /* shift >= 0 */
#define silk_ADD_RSHIFT32(a, b, shift)      silk_ADD32((a), silk_RSHIFT32((b), (shift)))    /* shift >= 0 */
#define silk_ADD_RSHIFT_uint(a, b, shift)   ((a) + silk_RSHIFT_uint((b), (shift)))          /* shift >= 0 */
#define silk_SUB_LSHIFT32(a, b, shift)      silk_SUB32((a), silk_LSHIFT32((b), (shift)))    /* shift >= 0 */
#define silk_SUB_RSHIFT32(a, b, shift)      silk_SUB32((a), silk_RSHIFT32((b), (shift)))    /* shift >= 0 */

/* Requires that shift > 0 */
#define silk_RSHIFT_ROUND(a, shift)         ((shift) == 1 ? ((a) >> 1) + ((a) & 1) : (((a) >> ((shift) - 1)) + 1) >> 1)
#define silk_RSHIFT_ROUND64(a, shift)       ((shift) == 1 ? ((a) >> 1) + ((a) & 1) : (((a) >> ((shift) - 1)) + 1) >> 1)

/* Number of rightshift required to fit the multiplication */
#define silk_NSHIFT_MUL_32_32(a, b)         ( -(31- (32-silk_CLZ32(silk_abs(a)) + (32-silk_CLZ32(silk_abs(b))))) )
//#define silk_NSHIFT_MUL_16_16(a, b)         ( -(15- (16-silk_CLZ16(silk_abs(a)) + (16-silk_CLZ16(silk_abs(b))))) )


#define silk_min(a, b)                      (((a) < (b)) ? (a) : (b))
#define silk_max(a, b)                      (((a) > (b)) ? (a) : (b))

/* Macro to convert floating-point constants to fixed-point */
#define SILK_FIX_CONST( C, Q )              ((int32_t)((C) * ((int64_t)1 << (Q)) + 0.5))

/* silk_min() versions with typecast in the function call */
static int32_t silk_min_int(int32_t a, int32_t b)
{
    return (((a) < (b)) ? (a) : (b));
}
/*
static int16_t silk_min_16(int16_t a, int16_t b)
{
    return (((a) < (b)) ? (a) : (b));
}
static int32_t silk_min_32(int32_t a, int32_t b)
{
    return (((a) < (b)) ? (a) : (b));
}
static int64_t silk_min_64(int64_t a, int64_t b)
{
    return (((a) < (b)) ? (a) : (b));
}
*/
/* silk_min() versions with typecast in the function call */
static int32_t silk_max_int(int32_t a, int32_t b)
{
    return (((a) > (b)) ? (a) : (b));
}
/*
static int16_t silk_max_16(int16_t a, int16_t b)
{
    return (((a) > (b)) ? (a) : (b));
}
*/
static int32_t silk_max_32(int32_t a, int32_t b)
{
    return (((a) > (b)) ? (a) : (b));
}
/*
static int64_t silk_max_64(int64_t a, int64_t b)
{
    return (((a) > (b)) ? (a) : (b));
}
*/
#define silk_LIMIT( a, limit1, limit2)      ((limit1) > (limit2) ? ((a) > (limit1) ? (limit1) : ((a) < (limit2) ? (limit2) : (a))) \
                                                                 : ((a) > (limit2) ? (limit2) : ((a) < (limit1) ? (limit1) : (a))))

#define silk_LIMIT_int                      silk_LIMIT
#define silk_LIMIT_16                       silk_LIMIT
#define silk_LIMIT_32                       silk_LIMIT

#define silk_abs(a)                         (((a) >  0)  ? (a) : -(a))            /* Be careful, silk_abs returns wrong when input equals to silk_intXX_MIN */
#define silk_abs_int(a)                     (((a) ^ ((a) >> (8 * sizeof(a) - 1))) - ((a) >> (8 * sizeof(a) - 1)))
#define silk_abs_int32(a)                   (((a) ^ ((a) >> 31)) - ((a) >> 31))
#define silk_abs_int64(a)                   (((a) >  0)  ? (a) : -(a))

#define silk_sign(a)                        ((a) > 0 ? 1 : ( (a) < 0 ? -1 : 0 ))

/* PSEUDO-RANDOM GENERATOR                                                          */
/* Make sure to store the result as the seed for the next call (also in between     */
/* frames), otherwise result won't be random at all. When only using some of the    */
/* bits, take the most significant bits by right-shifting.                          */
#define RAND_MULTIPLIER                     196314165
#define RAND_INCREMENT                      907633515
#define silk_RAND(seed)                     (silk_MLA_ovflw((RAND_INCREMENT), (seed), (RAND_MULTIPLIER)))

/*  Add some multiplication functions that can be easily mapped to ARM. */

/*    silk_SMMUL: Signed top word multiply.
          ARMv6        2 instruction cycles.
          ARMv3M+      3 instruction cycles. use SMULL and ignore LSB registers.(except xM)*/
/*#define silk_SMMUL(a32, b32)                (int32_t)silk_RSHIFT(silk_SMLAL(silk_SMULWB((a32), (b32)), (a32), silk_RSHIFT_ROUND((b32), 16)), 16)*/
/* the following seems faster on x86 */
#define silk_SMMUL(a32, b32)                (int32_t)silk_RSHIFT64(silk_SMULL((a32), (b32)), 32)

#if !defined(OPUS_X86_MAY_HAVE_SSE4_1)
#define silk_burg_modified(res_nrg, res_nrg_Q, A_Q16, x, minInvGain_Q30, subfr_length, nb_subfr, D, arch) \
    ((void)(arch), silk_burg_modified_c(res_nrg, res_nrg_Q, A_Q16, x, minInvGain_Q30, subfr_length, nb_subfr, D, arch))

#define silk_inner_prod16_aligned_64(inVec1, inVec2, len, arch) \
    ((void)(arch),silk_inner_prod16_aligned_64_c(inVec1, inVec2, len))
#endif


#ifdef  __cplusplus
}
#endif

#endif /* SILK_SIGPROC_FIX_H */

/*****************************************************************************/
//copied from macros.h
//modified 

#ifndef SILK_MACROS_H
#define SILK_MACROS_H


/* This is an header file for general platform. */

/* (a32 * (int32_t)((int16_t)(b32))) >> 16 output have to be 32bit int */
#if OPUS_FAST_INT64
#define silk_SMULWB(a32, b32)            ((int32_t)(((a32) * (int64_t)((int16_t)(b32))) >> 16))
#else
#define silk_SMULWB(a32, b32)            ((((a32) >> 16) * (int32_t)((int16_t)(b32))) + ((((a32) & 0x0000FFFF) * (int32_t)((int16_t)(b32))) >> 16))
#endif

/* a32 + (b32 * (int32_t)((int16_t)(c32))) >> 16 output have to be 32bit int */
#if OPUS_FAST_INT64
#define silk_SMLAWB(a32, b32, c32)       ((int32_t)((a32) + (((b32) * (int64_t)((int16_t)(c32))) >> 16)))
#else
#define silk_SMLAWB(a32, b32, c32)       ((a32) + ((((b32) >> 16) * (int32_t)((int16_t)(c32))) + ((((b32) & 0x0000FFFF) * (int32_t)((int16_t)(c32))) >> 16)))
#endif

/* (a32 * (b32 >> 16)) >> 16 */
#if OPUS_FAST_INT64
#define silk_SMULWT(a32, b32)            ((int32_t)(((a32) * (int64_t)((b32) >> 16)) >> 16))
#else
#define silk_SMULWT(a32, b32)            (((a32) >> 16) * ((b32) >> 16) + ((((a32) & 0x0000FFFF) * ((b32) >> 16)) >> 16))
#endif

/* a32 + (b32 * (c32 >> 16)) >> 16 */
#if OPUS_FAST_INT64
#define silk_SMLAWT(a32, b32, c32)       ((int32_t)((a32) + (((b32) * ((int64_t)(c32) >> 16)) >> 16)))
#else
#define silk_SMLAWT(a32, b32, c32)       ((a32) + (((b32) >> 16) * ((c32) >> 16)) + ((((b32) & 0x0000FFFF) * ((c32) >> 16)) >> 16))
#endif

/* (int32_t)((int16_t)(a3))) * (int32_t)((int16_t)(b32)) output have to be 32bit int */
#define silk_SMULBB(a32, b32)            ((int32_t)((int16_t)(a32)) * (int32_t)((int16_t)(b32)))

/* a32 + (int32_t)((int16_t)(b32)) * (int32_t)((int16_t)(c32)) output have to be 32bit int */
#define silk_SMLABB(a32, b32, c32)       ((a32) + ((int32_t)((int16_t)(b32))) * (int32_t)((int16_t)(c32)))

/* (int32_t)((int16_t)(a32)) * (b32 >> 16) */
#define silk_SMULBT(a32, b32)            ((int32_t)((int16_t)(a32)) * ((b32) >> 16))

/* a32 + (int32_t)((int16_t)(b32)) * (c32 >> 16) */
#define silk_SMLABT(a32, b32, c32)       ((a32) + ((int32_t)((int16_t)(b32))) * ((c32) >> 16))

/* a64 + (b32 * c32) */
#define silk_SMLAL(a64, b32, c32)        (silk_ADD64((a64), ((int64_t)(b32) * (int64_t)(c32))))

/* (a32 * b32) >> 16 */
#if OPUS_FAST_INT64
#define silk_SMULWW(a32, b32)            ((int32_t)(((int64_t)(a32) * (b32)) >> 16))
#else
#define silk_SMULWW(a32, b32)            silk_MLA(silk_SMULWB((a32), (b32)), (a32), silk_RSHIFT_ROUND((b32), 16))
#endif

/* a32 + ((b32 * c32) >> 16) */
#if OPUS_FAST_INT64
#define silk_SMLAWW(a32, b32, c32)       ((int32_t)((a32) + (((int64_t)(b32) * (c32)) >> 16)))
#else
#define silk_SMLAWW(a32, b32, c32)       silk_MLA(silk_SMLAWB((a32), (b32), (c32)), (b32), silk_RSHIFT_ROUND((c32), 16))
#endif

/* add/subtract with output saturated */
#define silk_ADD_SAT32(a, b)             ((((uint32_t)(a) + (uint32_t)(b)) & 0x80000000) == 0 ?                              \
                                        ((((a) & (b)) & 0x80000000) != 0 ? silk_int32_MIN : (a)+(b)) :   \
                                        ((((a) | (b)) & 0x80000000) == 0 ? silk_int32_MAX : (a)+(b)) )

#define silk_SUB_SAT32(a, b)             ((((uint32_t)(a)-(uint32_t)(b)) & 0x80000000) == 0 ?                                        \
                                        (( (a) & ((b)^0x80000000) & 0x80000000) ? silk_int32_MIN : (a)-(b)) :    \
                                        ((((a)^0x80000000) & (b)  & 0x80000000) ? silk_int32_MAX : (a)-(b)) )


#if 0 
#ifndef OVERRIDE_silk_CLZ32

static int32_t silk_CLZ32(int32_t in32)
{
    //return in32 ? 32 - EC_ILOG(in32) : 32;
    
    //Note: EC_ILOG is not found anywhere. replacing it with actual function
    //Count leading zeros.
    int j = 0x7FFFFFFF;
    int i;
    for (i = 0; i < 32; i++)
    {
        if (in32 & j)
            break;
        j = j >> 1;
    }
    return in32 ? 32 - i : 32;

}
#endif
#endif


#endif /* SILK_MACROS_H */


/*****************************************************************************/

#endif //_VAD_SILK_H_