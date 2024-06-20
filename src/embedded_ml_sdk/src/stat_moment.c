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

//      This routine computes the nth moment of a given data set.
//      There are pretty much two optimizations:  First, we use a case
//      statement instead of using the POW library function.
//      Second, we do the calculations using int32 or int64 instead
//      of float.
//      As customay, we supply three entry points:
//      i_stat_moment()         returns an integer.
//      f_stat_moment()         returns a float.
//      stat_moment()           compatible with the old calling style
//
//      Note:  The i_stat_moment() will generally produce different results
//      than the other routines, because it uses a fixed-point value for the
//      average (and the interior summations).  This is generally a small error.
//
//      Note:  There will be an integer overflow in cases where more than
//      128 million 12-bit data points are fed into this routine.
//      We know that this won't happen in the current version,
//      but be careful in the future. . .

FLOAT f_stat_moment(ringb *rb, int32_t base_index, int32_t len, int32_t moment)
//
//      The floating-point version, cleaned up somewhat by not
//      using the POW library routine in every case.
//
{
	int32_t i;
	FLOAT avg;
	FLOAT temp;
	FLOAT sum;
	int32_t start_index;

	if (len <= 0)
		return 0.0;

	if (moment == 1)
		return 0.0;
	avg = mean(rb, base_index, len);
	sum = 0.0f;
	start_index = base_index;

	switch (moment)
	{
	case 2:
		for (i = 0; i < len; i++)
		{
			temp = (FLOAT)MOD_READ_RINGBUF(rb, start_index++) - avg;
			sum += temp * temp; // temp**2
		}
		break;
	case 3:
		for (i = 0; i < len; i++)
		{
			temp = (FLOAT)MOD_READ_RINGBUF(rb, start_index++) - avg;
			sum += temp * temp * temp; // temp**3
		}
		break;
	default:
		for (i = 0; i < len; i++)
		{
			sum +=
				(float)POW((float)MOD_READ_RINGBUF(rb, start_index++) -
							   avg,
						   (float)moment);
		}
		break;
	}
	return sum / len;
}

int32_t i_stat_moment(ringb *rb, int32_t base_index, int32_t len, int32_t moment)
//
//      The integer version.
//
//      Note that, for moments other than 2 or 3, it just returns 0.
//      Typical higher-order moment results won't fit in 32 bits.
//
{
	int32_t i;
	int32_t avg;
	int32_t temp;
	int64_t sum;
	int32_t start_index;

	if (len <= 0)
		return 0;
	if (moment == 1)
		return 0;

	sum = 0;
	avg = (int32_t)mean(rb, base_index, len);
	start_index = base_index;

	switch (moment)
	{
	default:
	case 1:
		return 0;
		break;
	case 2:
		for (i = 0; i < len; i++)
		{
			temp = MOD_READ_RINGBUF(rb, start_index++) - avg;
			sum += (temp * temp); // temp**2
		}
		break;
	case 3:
		for (i = 0; i < len; i++)
		{
			temp = MOD_READ_RINGBUF(rb, start_index++) - avg;
			sum += ((int64_t)(temp * temp)) * temp; // temp**3
		}
		break;
	}
	return (int32_t)(sum / len);
}

FLOAT stat_moment(ringb *rb, int32_t base_index, int32_t len, int32_t moment)
//
//      The generic version, used for compatibility.
//      Calls f_stat_moment(), at this time.
//
{
	return f_stat_moment(rb, base_index, len, moment);
}

//
