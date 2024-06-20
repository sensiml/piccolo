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

int32_t ratio_diff_impl(ringb *rb, int32_t base_index, int32_t nlen, int32_t half_winsize, int32_t flag_h_l, float *out)
{
	int32_t i, window_size;
	int32_t start_index = base_index + nlen * flag_h_l;
	float sum_mem = 0, sumtemp = 0;

	float max = -KB_FLT_MAX, min = KB_FLT_MAX;

	window_size = 2 * half_winsize + 1;

	sum_mem = 0;
	for (i = 0; i < window_size; i++)
	{
		sum_mem += MOD_READ_RINGBUF(rb, start_index++);
	}
	start_index = base_index + nlen * flag_h_l + half_winsize;
	for (i = half_winsize; i < nlen - half_winsize; i++)
	{
		sumtemp = sum_mem;
		sumtemp = sumtemp / (window_size);
		sumtemp = rb->buff[start_index] - sumtemp;
		sum_mem = sum_mem - MOD_READ_RINGBUF(rb, (start_index - half_winsize)) +
				  MOD_READ_RINGBUF(rb, (start_index + half_winsize + 1));
		start_index++;
		if (sumtemp > max)
			max = sumtemp;
		if (sumtemp < min)
			min = sumtemp;
	}

	*out = max - min;
	return 1;
}
