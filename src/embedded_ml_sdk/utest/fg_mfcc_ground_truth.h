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

float fg_mfcc_gt[][23] = {
	//1112_howling_0_preemph.txt
	{
		260172, 118928, -99339, -12176, 83725, 
		-117333, 18225, 48121, -81114, -12502, 
		48740, -17604, 10283, -4264, -2444, 
		14150, 1778, -7203, 4967, -8450, 
		-1074, 6341, -725, 
	},
	//125524_drinking_1_lifter.txt
	{
		287741, -24098, -92448, 43387, -65414, 
		-34881, -77496, -22744, -59949, 15355, 
		28816, 2400, 21303, 55680, -617, 
		22220, 25313, 4774, -2925, 774, 
		3890, -3169, -2768, 
	},
	//130030_barking_16_lifter.txt
	{
		335554, 81413, -30732, -138432, -39168, 
		-109639, -246540, -37786, -76777, -71938, 
		25416, 8172, -16453, 78223, 102387, 
		12878, -60397, -35743, -1161, 11033, 
		-3821, -2615, 2635, 
	},
	//13789_growling_82_lifter.txt
	{
		328941, 45133, 170863, -7458, 21848, 
		-29541, -21980, 26875, -128670, 47003, 
		-34547, 104568, -32110, 21733, -53599, 
		11156, -7507, 2387, -33443, 4166, 
		6816, 4635, 864, 
	},
	//216613_eating_1_lifter.txt
	{
		324712, -138203, -63336, -73079, -66213, 
		28186, -8978, 40318, 39257, 129594, 
		-14337, 25176, -17428, 8700, -7363, 
		27111, -7879, -5513, 1945, -8851, 
		4713, 2242, -1470, 
	},
};
