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
 * Author(s) : Giuseppe Raffa, Noura Farra
 * Group : IXR/Intel Labs
 * modified to linux kernel coding style by Alek Du (PSI, MCG)
 * code cleanup and maintained by Han Ke (PSI, MCG)
*/

#ifndef GESTURE_SPOTTING_H
#define GESTURE_SPOTTING_H
#include "mathcontext.h"

#ifdef _WIN32
#define DLL_EXPORT __declspec(dllexport)
#else
#define DLL_EXPORT
#endif

#define TEMPLATE_MATHING_NUM_DIM	2 /* two dimensions: 0:duration 1:max power */
#define SAMPLE_SIZE_ITEMS		3 /* ax ay az gx gy gz */
#define USE_BACKTRACKING

struct mov_detect_struct_init
{
	s16 avgnotmovetomove;	/* accel threshold notmove to move (avg) */
	s16 stdnotmovetomove;	/* accel threshold notmove to move (std) */
	s16 avgmovetonotmove;	/* accel threshold move to notmove (avg) */
	s16 stdmovetonotmove;	/* accel threshold move to notmove (std) */
	u16 window;		/* smooting window */
	u8 ntimesmovingtonotmoving;	/* #times filtered signal should be below */
					/* thresholds to go to "not move" state */
	u8 ntimesnotmovingtomoving;	/* #times filtered signal should be above */
					/* thresholds to go to "move" state */
};

struct template_entry
{
	u8 ndim;	/* 0: duration 1:max power */
	s16 min;	/* for each dimension min and max values */
	s16 max;
	s16 min_valid;
	s16 max_valid;
};

struct gesture_struct
{
	s16 *sample;	/* buffer to the data in Ax,Ay,Az,Gx,Gy,Gz format */
	u8 is_valid;	/* TRUE if the sample buffer is valid and gesture complete */
	u16 size_samples;	/* size of the sample in #samples, each sample is 6 s16 */
};

struct gs_data
{
	u16 size;
	s16 sample[(300 * 3 * 2) / 2];
};

#ifdef __cplusplus
extern "C"
{
#endif
u8 gesture_spot_init(s16 one_g,
		struct template_entry t[],
		u8 num_dim_template,
		int use_default_template_entry,
		struct mov_detect_struct_init *m_forward,
		struct mov_detect_struct_init *m_backward,
		int use_default_mov_detect,
		int use_template_matching_filtering,
		void *sample_buf, int sample_buf_size);

int gesture_spot_processsample(void* data,u16 len_bytes,struct gesture_struct *g);/* data is a s16* */
DLL_EXPORT int GestureSpotting_TopInterface(s16 ax, s16 ay, s16 az, s16 * pRetDataBuf, s16 * nLenInBytes);
int spotting_init_top(short *pbuf, int buf_size);
#ifdef __cplusplus
}
#endif

#endif
