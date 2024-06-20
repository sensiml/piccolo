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

#include <stdint.h>

int16_t tr_segment_pre_emphasis_filter_gt[][10] = {
	//1114_howling_4.txt
	{
		-776,
		-84,
		-68,
		-12,
		96,
		207,
		245,
		167,
		11,
		-145,
	},
	//13789_growling_35.txt
	{
		-1476,
		-238,
		-233,
		-457,
		-37,
		-331,
		-177,
		132,
		-253,
		135,
	},
	//24965_barking_37.txt
	{
		237,
		-38,
		-98,
		-134,
		-134,
		-164,
		-170,
		-158,
		-99,
		-77,
	},
	//61025_eating_0.txt
	{
		344,
		93,
		633,
		-54,
		-930,
		268,
		251,
		17,
		328,
		102,
	},
	//332294_drinking_1.txt
	{
		297,
		94,
		18,
		-64,
		-180,
		-319,
		-349,
		-277,
		-137,
		-38,
	},
};
