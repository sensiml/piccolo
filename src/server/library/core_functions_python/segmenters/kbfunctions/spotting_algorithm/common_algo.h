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




// Featrue exteration for burlington
// author: zhiqiang.liang@intel.com

#ifndef _COMMON_ALGO_
#define _COMMON_ALGO_

#ifdef __cplusplus
#if __cplusplus
extern "C"{
#endif
#endif /* __cplusplus */ 

#ifndef DIM_FEATURE
#define DIM_FEATURE 60
#endif

#define FRAME_NORM_LEN 20
    //#define DIM_FEAT_FINA 4
#define EIGVEC_PICKED 60
#define G 1000
#define QUANTIZATION_MAX 127


#define PI 3.1415926
#define TRUE 1
#define FALSE 0
#define true 1
#define false 0
#define YES 1
#define NO 0
#define BASE_DOWNSAMPLE 20
#define CLASSAMOUNT 8
#define CLASSTRINGLENGTH 11

#define abs(a) ((a)>0?(a):(-(a))) 
#define max(a,b) ((a)>(b)?(a):(b))
#define min(a,b) ((a)>(b)?(b):(a))
#define sign(d) ((d)<0?-1:((d)>(0)))

#define ROUND(x) ((int)(x + 0.4999999999999999))

typedef unsigned char uchar;
typedef unsigned short ushort;
typedef unsigned int uint;
typedef signed char schar;
typedef signed short sshort;
typedef signed int sint;

typedef unsigned char u8;
typedef unsigned short u16;
typedef unsigned int u32;
typedef signed char s8;
typedef signed short s16;
typedef signed int s32;

typedef unsigned long long u64;
typedef signed long long s64;

#define bool unsigned char
    //------------------------------------------------------------------#definition from PSH code:
#define MEM_NORMAL	0	/* use normal memory to allocate */
#define MEM_INIT	1	/* reuse init section to allocate,*/
#define NULL 0
#define ACT_MAX_REPORT 64


#ifndef likely
#define likely(x) ((x)>0?1:0)
#endif
#ifndef unlikly
#define unlikely(x) ((x)<=0?0:1)
#endif

#define ZMALLOC(size, flag)	malloc(size)
#define FREE(ptr)	free(ptr)
//------------------------------------------------------------------
typedef struct _OneAccSample
{
    float x;
    float y;
    float z;

    //float gx;
    //float gy;
    //float gz;

}AccSample;

typedef struct _ParamClassifier
{
    uint TrainMode;
    uint TrainAmo;
    uint TestAmo;
    uint FeatDim;
    uint ClassAmo;
    char * ClassStringBase;
    char * TrainedLabel;
    char ** ClassString;
}ParamNN;


typedef struct _PathClassifier
{

    char * pFeatVecPath;
    char * pTrainedNeuron;
    char * pMappedLabel;
    char * pFeat_OnLineTrain;
    char * ClassStringBase;
}PathNN;

typedef struct _RecResult
{
    uint PredictAmo;
    uint Unknowns;
    uint Uncertains;
    uint Corrects;
    uint Errors;

}RecResult;

#ifdef __cplusplus
#if __cplusplus
}
#endif
#endif /* __cplusplus */



#endif