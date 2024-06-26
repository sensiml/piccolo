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

int16_t fg_mfcc_tv[2000] = {
	//1112_howling_0_preemph.txt
	
		561, 39, 60, 60, 46, 
		35, 41, 57, 61, 44, 
		17, 0, 3, 14, 15, 
		2, -18, -28, -23, -9, 
		4, 17, 31, 48, 55, 
		43, 15, -12, -22, -11, 
		10, 26, 34, 38, 42, 
		44, 34, 16, -1, -8, 
		-3, 1, -7, -25, -39, 
		-40, -26, -11, -5, -8, 
		-13, -10, 2, 21, 39, 
		50, 51, 40, 22, 8, 
		8, 18, 26, 17, -8, 
		-35, -41, -20, 12, 31, 
		26, 7, -6, -3, 10, 
		18, 13, 1, -6, -7, 
		-6, -7, -10, -5, 12, 
		34, 43, 35, 15, -5, 
		-8, 2, 18, 33, 39, 
		38, 30, 17, 4, -1, 
		5, 18, 25, 17, -6, 
		-33, -48, -44, -29, -15, 
		-10, -12, -14, -10, -3, 
		-1, -7, -20, -31, -33, 
		-24, -10, 1, 7, 9, 
		11, 16, 21, 20, 9, 
		-8, -21, -22, -11, 6, 
		18, 19, 11, 0, -6, 
		-5, 0, 2, -1, -9, 
		-20, -28, -29, -22, -8, 
		4, 10, 5, -3, -7, 
		0, 15, 25, 18, -4, 
		-33, -50, -46, -26, -6, 
		0, -8, -20, -24, -13, 
		2, 11, 6, -8, -21, 
		-24, -16, -7, -5, -12, 
		-20, -22, -14, -4, -2, 
		-13, -31, -45, -47, -36, 
		-21, -12, -11, -11, -4, 
		15, 41, 57, 53, 30, 
		1, -17, -14, 4, 21, 
		23, 9, -11, -20, -13, 
		0, 9, 6, -6, -16, 
		-17, -9, 1, 5, 3, 
		-3, -9, -12, -14, -12, 
		-4, 8, 22, 32, 35, 
		31, 24, 14, 5, -1, 
		-2, 2, 5, 1, -12, 
		-29, -37, -27, -6, 14, 
		18, 3, -19, -32, -31, 
		-24, -19, -20, -20, -14, 
		-1, 12, 13, 3, -12, 
		-25, -31, -32, -25, -11, 
		8, 29, 43, 45, 39, 
		34, 36, 46, 54, 51, 
		38, 19, 3, -6, -8, 
		-4, 2, 9, 12, 10, 
		3, -5, -7, -2, 5, 
		11, 11, 10, 7, 1, 
		-9, -23, -33, -34, -23, 
		-9, -1, -4, -10, -6, 
		11, 33, 42, 29, 3, 
		-21, -23, -6, 16, 24, 
		14, -8, -22, -24, -14, 
		-5, -3, -7, -10, -8, 
		-2, -1, -5, -12, -15, 
		-11, -2, 7, 12, 13, 
		12, 13, 14, 15, 20, 
		28, 38, 40, 31, 12, 
		-6, -9, 5, 24, 31, 
		18, -9, -34, -43, -34, 
		-17, 0, 11, 18, 22, 
		22, 14, 0, -11, -15, 
		-13, -13, -18, -28, -33, 
		-22, 4, 33, 56, 62, 
		51, 32, 12, -4, -13, 
		-19, -23, -25, -21, -11, 
		3, 13, 13, 5, -6, 
		-11, -7, 2, 5, 2, 
		-4, -3, 4, 15, 18, 
	
    //125524_drinking_1_preemph.txt
	
		3, 6, 30, 73, 118, 
		70, -176, -512, -586, -86, 
		814, 1361, 860, -484, -1598, 
		-1522, -346, 881, 1283, 851, 
		34, -566, -537, -356, -418, 
		-116, 376, 404, 338, 158, 
		-76, -88, -43, 20, -41, 
		-226, -176, -58, 32, 222, 
		130, -101, -38, 55, -66, 
		-85, 83, 156, 92, -33, 
		-117, -124, -39, 155, 199, 
		22, -116, -154, -83, 68, 
		118, 89, 20, -77, -77, 
		10, 56, -13, -93, -112, 
		-112, -12, 121, 121, 50, 
		-25, -65, -8, 74, 86, 
		7, -125, -122, 44, 133, 
		69, -31, -77, -55, 5, 
		65, 98, 30, -100, -105, 
		17, 85, 17, -54, -15, 
		28, -6, -10, 32, 12, 
		-36, -46, -31, -8, 11, 
		24, 26, -38, -66, 4, 
		8, -33, -11, 17, 1, 
		-12, 1, 11, 8, -9, 
		-9, 14, 50, 56, 8, 
		-28, -26, -13, -9, 13, 
		3, -7, 19, 33, 51, 
		2, -55, -36, -14, -7, 
		4, 31, 5, -24, 1, 
		3, 0, 3, -6, -16, 
		-13, 2, -13, -11, 22, 
		13, -13, -7, 27, 48, 
		43, 24, -8, -21, -15, 
		3, 31, 12, -29, -12, 
		27, 19, -9, -23, -18, 
		-5, -12, -14, -4, -4, 
		-11, -18, -17, -8, 4, 
		16, 16, 15, -1, -5, 
		3, 11, 4, 5, 28, 
		27, 23, 16, -6, -35, 
		-12, 14, 10, 1, -15, 
		-8, 15, 42, 31, -14, 
		-17, 16, 16, -4, -14, 
		-11, -2, -12, -13, -21, 
		-36, -9, 8, -28, -29, 
		-2, 4, -11, -41, -30, 
		32, 64, 23, -4, 6, 
		-7, -10, 20, 29, 1, 
		-7, 23, 33, -1, -7, 
		26, 9, -14, 10, 25, 
		5, -20, -14, -15, -22, 
		-11, -18, -17, 1, 3, 
		-14, -12, 13, -9, -28, 
		10, 20, 22, 20, 2, 
		10, -5, -28, -10, 4, 
		16, 18, 3, -6, -5, 
		-3, 7, 21, 5, -14, 
		-13, 10, 22, -17, -16, 
		2, -9, 0, 6, 3, 
		-6, 2, 22, 9, -24, 
		-19, 8, 10, 23, 12, 
		-36, -36, -8, 8, 20, 
		27, 12, -1, -13, -21, 
		1, 7, 8, 19, 15, 
		15, 18, 3, -17, -15, 
		7, 10, -12, -24, 6, 
		2, -19, 14, 5, -1, 
		-5, -34, 9, 20, 8, 
		13, -10, 2, 9, -8, 
		-4, 17, 6, -13, 3, 
		-1, 9, 40, 17, -9, 
		-2, 5, 7, -2, 4, 
		-14, -19, 24, 18, -18, 
		-15, 6, 2, -16, -2, 
		6, -2, 12, 10, 10, 
		8, -11, 5, 19, -3, 
		-9, 10, 15, 2, -11, 
		5, 6, -27, -4, 18, 
		-15, -14, 11, 18, -8,
	
	//130030_barking_16_preemph.txt
	
		-1357, 7, 50, 69, 101, 
		95, 117, 92, 72, 90, 
		90, 106, 108, 159, 146, 
		125, 170, 140, 137, 140, 
		122, 124, 149, 146, 137, 
		154, 123, 85, 43, -17, 
		-73, -130, -185, -205, -210, 
		-230, -271, -268, -293, -321, 
		-305, -329, -319, -290, -252, 
		-176, -116, -49, 18, 39, 
		72, 92, 107, 128, 133, 
		195, 248, 286, 324, 360, 
		353, 317, 321, 294, 211, 
		192, 198, 129, 82, 73, 
		19, -61, -112, -174, -258, 
		-300, -289, -278, -286, -254, 
		-205, -144, -157, -108, -57, 
		-85, -69, -64, -67, -45, 
		14, 15, 45, 33, 1, 
		-9, -6, 48, 105, 171, 
		204, 227, 239, 300, 302, 
		271, 273, 186, 81, 24, 
		-57, -99, -96, -107, -87, 
		-99, -108, -114, -168, -198, 
		-234, -256, -291, -332, -349, 
		-347, -317, -252, -127, -66, 
		-3, 38, 28, 65, 64, 
		164, 278, 336, 433, 455, 
		418, 363, 348, 312, 291, 
		285, 217, 137, 88, 37, 
		-39, -45, -96, -213, -303, 
		-394, -409, -409, -390, -297, 
		-289, -261, -230, -196, -149, 
		-85, -55, -4, -3, -59, 
		31, 50, 130, 223, 251, 
		293, 232, 189, 186, 203, 
		259, 325, 333, 356, 319, 
		234, 176, 105, 42, -55, 
		-151, -255, -301, -325, -313, 
		-272, -228, -251, -278, -334, 
		-422, -402, -366, -269, -134, 
		-42, 2, 30, 35, -2, 
		11, 89, 103, 142, 277, 
		319, 405, 499, 553, 590, 
		535, 491, 406, 255, 154, 
		102, 33, -14, -47, -133, 
		-272, -395, -489, -578, -609, 
		-585, -530, -479, -390, -278, 
		-216, -127, -114, -97, -26, 
		-57, -58, 35, 85, 158, 
		310, 407, 447, 454, 417, 
		342, 321, 345, 393, 434, 
		460, 478, 394, 354, 268, 
		180, 45, -172, -305, -483, 
		-602, -613, -566, -562, -554, 
		-534, -572, -618, -525, -448, 
		-381, -153, -27, 35, 156, 
		234, 238, 360, 406, 393, 
		424, 337, 282, 231, 315, 
		399, 481, 638, 605, 494, 
		401, 257, 142, 153, 139, 
		95, 23, -181, -426, -629, 
		-849, -907, -970, -958, -845, 
		-810, -669, -482, -217, -33, 
		140, 278, 253, 188, 211, 
		286, 385, 624, 718, 700, 
		618, 414, 310, 272, 318, 
		413, 436, 362, 257, 176, 
		108, 134, 63, -56, -201, 
		-493, -748, -866, -916, -880, 
		-719, -610, -521, -427, -404, 
		-296, -179, -81, 28, 72, 
		186, 311, 400, 620, 749, 
		797, 752, 584, 426, 263, 
		228, 295, 354, 374, 332, 
		218, 49, -16, -27, -78, 
		-42, -129, -247, -319, -474, 
		-557, -580, -635, -752, -822, 
		-934, -968, -828, -691, -374, 
		-101, 86, 299, 368, 359, 
	
	//13789_growling_82_preemph.txt
	
		1785, 122, -36, 64, -67, 
		-178, -18, -240, -159, -162, 
		-276, -106, -216, -168, -86, 
		-197, 23, 32, -1, 221, 
		167, 236, 374, 318, 381, 
		462, 405, 437, 399, 331, 
		348, 218, 248, 123, 48, 
		102, -144, -54, -124, -293, 
		-194, -344, -374, -360, -429, 
		-457, -476, -417, -440, -440, 
		-357, -319, -313, -161, -96, 
		-187, -14, -39, -59, 129, 
		-28, 53, 54, -67, 108, 
		-40, 17, 69, -91, 36, 
		-54, -108, -31, -111, -153, 
		-104, -139, -138, -46, -101, 
		-45, -20, 4, 95, 15, 
		140, 86, 60, 241, 51, 
		172, 198, 93, 241, 111, 
		187, 246, 122, 186, 118, 
		82, 132, 4, 12, 42, 
		-77, -17, -72, -81, 1, 
		-119, -40, -41, -82, 33, 
		-27, -4, 68, 44, 84, 
		135, 166, 191, 212, 182, 
		239, 259, 222, 251, 224, 
		231, 173, 164, 199, 122, 
		159, 109, 30, 62, -39, 
		-44, -90, -109, -129, -191, 
		-186, -250, -221, -226, -229, 
		-263, -291, -230, -277, -252, 
		-274, -265, -259, -292, -187, 
		-226, -152, -110, -196, -127, 
		-116, -73, -86, -99, -41, 
		-85, -23, -13, -73, 10, 
		-26, -23, -11, -2, 29, 
		-56, 10, -14, -40, 18, 
		-52, -12, -26, -2, 43, 
		-17, 82, 73, 18, 108, 
		112, 60, 157, 97, 96, 
		181, 41, 123, 87, 70, 
		157, 17, 133, 107, 16, 
		157, 45, 112, 62, -15, 
		137, -67, 33, 86, -129, 
		82, -26, -49, 124, -41, 
		141, 102, 62, 256, 51, 
		212, 268, 94, 370, 197, 
		156, 390, 110, 282, 250, 
		74, 327, 45, 94, 158, 
		-166, 71, -91, -244, -6, 
		-289, -195, -181, -366, -82, 
		-351, -266, -159, -495, -79, 
		-362, -424, -77, -545, -187, 
		-171, -439, -47, -272, -173, 
		-59, -274, 20, -176, -168, 
		156, -238, -32, 113, -265, 
		76, 32, -170, 136, -114, 
		-33, 81, -171, 106, -124, 
		-58, 148, -186, 109, 44, 
		-109, 172, 31, 39, 119, 
		-22, 114, 73, 10, 167, 
		10, 72, 171, -18, 201, 
		135, -18, 249, 29, 74, 
		203, -68, 168, 27, -39, 
		241, -106, 103, 186, -108, 
		246, 20, -66, 193, -180, 
		72, 59, -236, 209, -78, 
		-55, 265, -111, 218, 191, 
		-8, 355, 57, 226, 337, 
		-16, 393, 195, 153, 525, 
		58, 325, 410, 18, 356, 
		61, -21, 108, -263, 7, 
		-232, -336, -6, -476, -140, 
		-136, -486, -38, -348, -351, 
		-111, -415, -268, -285, -368, 
		-166, -374, -241, -98, -340, 
		-40, -105, -255, 9, -176, 
		-156, -56, -213, -70, -156, 
		-108, 4, -166, 34, -66, 
		-80, 45, -130, -19, -90, 
	
	//216613_eating_1_preemph.txt
	
		381, -1170, 201, 1338, -2694, 
		1475, 2030, -2145, 258, 53, 
		389, -577, 10, 1847, -951, 
		-1605, 689, 1950, -928, -1287, 
		518, -232, 194, -502, -164, 
		628, -217, 101, 270, 544, 
		-13, -725, -214, 936, -40, 
		-1032, 1022, -344, -470, 1375, 
		-1212, -38, 691, -1375, 647, 
		155, -743, 869, -60, -450, 
		500, -180, -92, 711, -567, 
		-30, 671, -486, 42, 139, 
		-389, -37, 109, 71, 193, 
		-166, -623, 587, 119, -547, 
		357, -67, -126, 128, -22, 
		10, 287, 53, -79, 163, 
		-287, -69, 100, -192, 101, 
		-51, 62, 57, -216, 181, 
		14, -239, 160, 89, -119, 
		150, 1, -180, 208, -35, 
		-94, 69, -54, 118, -33, 
		-44, -39, -73, 43, -81, 
		0, 59, 103, -110, -14, 
		75, -142, 134, 30, -42, 
		224, -36, -97, 58, -29, 
		-121, 64, -167, -117, 185, 
		-71, 89, 73, -72, 131, 
		-31, -171, 32, 64, 11, 
		70, -40, 14, 42, -69, 
		40, -76, -38, 66, -41, 
		-19, 97, 19, -84, 68, 
		-116, -96, 161, -96, 71, 
		22, -190, 264, 133, -227, 
		-85, 187, 55, -195, 172, 
		-36, -127, 30, -44, 149, 
		-140, -97, 103, -78, -35, 
		101, 89, -24, 34, -25, 
		31, -2, -162, 21, 79, 
		77, -9, -28, 70, -52, 
		22, -43, -33, 14, -47, 
		51, -24, -70, 7, 85, 
		-26, 52, 101, -109, -70, 
		190, 156, -325, -92, 109, 
		-84, 185, -70, -202, 281, 
		71, -288, 116, -61, -123, 
		192, 106, 2, -121, -68, 
		212, 197, -135, -221, 60, 
		36, -4, -16, -241, 43, 
		138, 46, 118, -60, -142, 
		147, 70, -238, -92, 75, 
		16, 20, 46, 125, 15, 
		-54, 48, -80, -112, 50, 
		53, -56, 7, 58, 20, 
		-1, -28, -98, 44, 122, 
		-108, -51, 47, -69, 44, 
		-12, -28, 46, -78, 57, 
		102, -119, 8, 141, -55, 
		-75, 23, 33, -36, -56, 
		123, 12, -158, -14, 83, 
		-47, -72, 103, -71, -113, 
		202, 196, -19, -270, -117, 
		282, -429, 66, 346, -300, 
		516, -394, -248, 416, -395, 
		534, -139, -411, 935, -579, 
		-216, 743, -720, -4, 297, 
		-264, -5, -48, 120, 114, 
		-73, -107, -14, -58, -18, 
		244, -38, -19, 143, -78, 
		-79, -40, -75, 234, 78, 
		-173, -10, -29, 104, 2, 
		-272, 80, 87, -127, 136, 
		-85, -130, 206, 44, -25, 
		-31, -123, 76, 87, -42, 
		26, -18, -125, 94, -2, 
		-154, 112, 29, -100, 79, 
		29, -33, 42, -66, -18, 
		58, -79, 24, 98, -49, 
		-4, -4, -83, 20, -74, 
		-49, 29, -60, 53, -2, 
		18, 70, -81, -1, -15, 

};
