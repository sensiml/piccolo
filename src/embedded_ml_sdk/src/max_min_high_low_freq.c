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




#include "kbutils.h"

/*
 * max_min_high_low_freq - compute the maximum and minimum of the high or low frequency
 *							 component of a waveform.
 *
 * Inputs
 *		nframes - number of rows in the array
 *       col - which column to analyze
 * 		offset - offset into the column to start
 *		sf	- smoothing factor (how many data points on either side of a sample to use to
 *				compute the mean.)
 *		max = pointer to FLOAT to receive the maximum value.
 *		min = pointer to FLOAT to receive the minimum value.
 *		lowhigh  - 1 = use high-freq values, 0 = use low freq values.
 */
int32_t max_min_high_low_freq(ringb *pringb, int32_t base_index, int32_t nframes, int32_t col, int32_t offset, int32_t sf, int32_t lowhigh, FLOAT *max, FLOAT *min)
{
	int32_t i;
	ringb *rb = pringb + col;
	int32_t start_index = (base_index + offset) & rb->mask;
	FLOAT dsum;
	FLOAT davg;
	FLOAT dmin = KB_FLT_MAX;
	FLOAT dmax = KB_FLT_MIN;
	FLOAT dval;
	FLOAT dval0 = (FLOAT)rb->buff[start_index];

	// Compute the running mean for the first sample
	for (i = -sf / 2, dsum = 0.0; i < sf / 2; i++)
	{
		start_index = (base_index + offset + i) & rb->mask;
		if (i < 0)
		{
			dsum += dval0; // pad with first value on left side.
		}
		else
		{
			dsum += (FLOAT)rb->buff[start_index];
		}
	}
	davg = dsum / sf;

	// Subtract the mean from the first sample
	dval = dval0 - davg;

	// Compare to max/min
	if (dval < dmin)
		dmin = dval;
	if (dval > dmax)
		dmax = dval;

	start_index = (base_index + offset) & rb->mask;
	// Compute the running mean for the each sample
	for (i = 1; i < nframes; i++)
	{
		int32_t decndx = i - sf / 2;
		int32_t addndx = i + sf / 2;
		int32_t dec = decndx < 0 ? dval0 : rb->buff[(base_index + decndx + offset) & rb->mask];
		int32_t add = addndx >= nframes ? rb->buff[(base_index + nframes + offset - 1) & rb->mask] : rb->buff[(base_index + addndx + offset) & rb->mask];

		dsum = dsum - dec + add;
		davg = dsum / sf;

		start_index = (start_index + 1) & rb->mask;
		switch (lowhigh)
		{
		case MOD_HF: // Subtract the mean to get the high freq components.
			dval = rb->buff[start_index] - davg;
			break;

		case MOD_LF:
			dval = davg; // Return the mean for the low freq components.
			break;

		case MOD_RAW:
			dval = rb->buff[start_index];
			break;
		}
		if (dval < dmin)
			dmin = dval;
		if (dval > dmax)
			dmax = dval;
	}
	*max = dmax;
	*min = dmin;

	return 1;
}
