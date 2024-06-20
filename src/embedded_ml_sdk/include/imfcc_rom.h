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




/**
 * \file imfcc_rom.h
 * \brief Pre-calculated tables for Rockhopper mini frontend
 */
#ifndef __IMFCC_ROM_H__
#define __IMFCC_ROM_H__

#include <stdint.h>

#define WINDOW_SIZE_ROM 400
#define NUM_CEPS_ROM 23

#define HANN_WINDOW_Q 14

#ifdef __cplusplus
extern "C"
{
#endif

    /* Only left size, mirror for right */
    static const int16_t kHannWindow[WINDOW_SIZE_ROM / 2] = {
        0, 4, 14, 28, 46, 67, 91, 119, 149, 182,
        217, 255, 296, 339, 384, 432, 482, 534, 588, 644,
        702, 763, 825, 889, 955, 1022, 1092, 1163, 1236, 1311,
        1387, 1465, 1545, 1626, 1708, 1792, 1878, 1965, 2053, 2143,
        2234, 2327, 2421, 2516, 2612, 2709, 2808, 2908, 3008, 3110,
        3213, 3318, 3423, 3529, 3636, 3744, 3852, 3962, 4073, 4184,
        4296, 4409, 4523, 4637, 4752, 4868, 4984, 5101, 5218, 5336,
        5455, 5574, 5694, 5813, 5934, 6055, 6176, 6297, 6419, 6541,
        6663, 6785, 6908, 7031, 7154, 7277, 7400, 7523, 7647, 7770,
        7893, 8016, 8140, 8263, 8386, 8508, 8631, 8753, 8876, 8998,
        9119, 9241, 9362, 9483, 9603, 9723, 9843, 9962, 10081, 10199,
        10317, 10434, 10550, 10666, 10782, 10896, 11011, 11124, 11237, 11349,
        11460, 11571, 11680, 11789, 11897, 12004, 12111, 12216, 12321, 12424,
        12527, 12629, 12729, 12829, 12928, 13025, 13122, 13217, 13311, 13405,
        13497, 13587, 13677, 13766, 13853, 13939, 14023, 14107, 14189, 14270,
        14350, 14428, 14505, 14580, 14654, 14727, 14798, 14868, 14937, 15004,
        15069, 15133, 15196, 15257, 15317, 15375, 15431, 15486, 15540, 15592,
        15642, 15691, 15738, 15784, 15827, 15870, 15910, 15949, 15987, 16023,
        16057, 16089, 16120, 16149, 16176, 16202, 16226, 16248, 16269, 16288,
        16305, 16321, 16334, 16347, 16357, 16366, 16372, 16378, 16381, 16383,
        /*16383, 16381, 16378, 16372, 16366, 16357, 16347, 16334, 16321, 16305,
        16288, 16269, 16248, 16226, 16202, 16176, 16149, 16120, 16089, 16057,
        16023, 15987, 15949, 15910, 15870, 15827, 15784, 15738, 15691, 15642,
        15592, 15540, 15486, 15431, 15375, 15317, 15257, 15196, 15133, 15069,
        15004, 14937, 14868, 14798, 14727, 14654, 14580, 14505, 14428, 14350,
        14270, 14189, 14107, 14023, 13939, 13853, 13766, 13677, 13587, 13497,
        13405, 13311, 13217, 13122, 13025, 12928, 12829, 12729, 12629, 12527,
        12424, 12321, 12216, 12111, 12004, 11897, 11789, 11680, 11571, 11460,
        11349, 11237, 11124, 11011, 10896, 10782, 10666, 10550, 10434, 10317,
        10199, 10081, 9962, 9843, 9723, 9603, 9483, 9362, 9241, 9119,
        8998, 8876, 8753, 8631, 8508, 8386, 8263, 8140, 8016, 7893,
        7770, 7647, 7523, 7400, 7277, 7154, 7031, 6908, 6785, 6663,
        6541, 6419, 6297, 6176, 6055, 5934, 5813, 5694, 5574, 5455,
        5336, 5218, 5101, 4984, 4868, 4752, 4637, 4523, 4409, 4296,
        4184, 4073, 3962, 3852, 3744, 3636, 3529, 3423, 3318, 3213,
        3110, 3008, 2908, 2808, 2709, 2612, 2516, 2421, 2327, 2234,
        2143, 2053, 1965, 1878, 1792, 1708, 1626, 1545, 1465, 1387,
        1311, 1236, 1163, 1092, 1022, 955, 889, 825, 763, 702,
        644, 588, 534, 482, 432, 384, 339, 296, 255, 217,
        182, 149, 119, 91, 67, 46, 28, 14, 4, 0,*/
    };

    static const uint16_t kLifters[NUM_CEPS_ROM] = {
        4096, 10508, 16790, 22813, 28455, 33601, 38147, 42000, 45080, 47327,
        48693, 49152, 48693, 47327, 45080, 42000, 38147, 33601, 28455, 22813,
        16790, 10508, 4096};

    /* First non-zero bin of each mel filter bank */
    static const uint8_t kFirstMelBankBin[NUM_CEPS_ROM] = {
        1,
        4,
        6,
        10,
        13,
        17,
        21,
        26,
        31,
        37,
        43,
        50,
        58,
        67,
        77,
        87,
        99,
        113,
        127,
        144,
        162,
        182,
        204,
    };

    /* Number of non-zero bins of each feature mel feature bank */
    static const uint8_t kMelBankNumBins[NUM_CEPS_ROM] = {
        5, 6, 7, 7, 8, 9, 10, 11, 12, 13, 15, 17, 19,
        20, 22, 26, 28, 31, 35, 38, 42, 47, 52};

    /* List of all bin weights, ordered from bin 0 to 22 */
    static const uint16_t kMelBinWeights[] = {
        /* Bank 0 */
        612, 2263, 3847, 2822, 1355,
        /* Bank 1 */
        1274, 2741, 4037, 2671, 1352, 75,
        /* Bank 2 */
        59, 1425, 2744, 4021, 2934, 1735, 571,
        /* Bank 3 */
        1162, 2361, 3525, 3537, 2438, 1369, 328,
        /* Bank 4 */
        559, 1658, 2727, 3768, 3409, 2421, 1456, 514,
        /* Bank 5 */
        687, 1675, 2640, 3582, 3691, 2792, 1913, 1054, 213,
        /* Bank 6 */
        405, 1304, 2183, 3042, 3883, 3485, 2678, 1888, 1113, 352,
        /* Bank 7 */
        611, 1418, 2208, 2983, 3744, 3703, 2971, 2252, 1546, 853,
        172,
        /* Bank 8 */
        393, 1125, 1844, 2550, 3243, 3924, 3598, 2939, 2291, 1654,
        1027, 409,
        /* Bank 9 */
        498, 1157, 1805, 2442, 3069, 3687, 3898, 3299, 2709, 2128,
        1556, 991, 435,
        /* Bank 10 */
        198, 797, 1387, 1968, 2540, 3105, 3661, 3982, 3441, 2907,
        2380, 1861, 1348, 841, 341,
        /* Bank 11 */
        114, 655, 1189, 1716, 2235, 2748, 3255, 3755, 3943, 3456,
        2974, 2498, 2028, 1563, 1104, 650, 201,
        /* Bank 12 */
        153, 640, 1122, 1598, 2068, 2533, 2992, 3446, 3895, 3853,
        3415, 2981, 2551, 2127, 1707, 1291, 879, 472, 69,
        /* Bank 13 */
        243, 681, 1115, 1545, 1969, 2389, 2805, 3217, 3624, 4027,
        3766, 3372, 2981, 2593, 2210, 1830, 1454, 1082, 713, 347,
        /* Bank 14 */
        330, 724, 1115, 1503, 1886, 2266, 2642, 3014, 3383, 3749,
        4081, 3722, 3366, 3013, 2664, 2318, 1974, 1634, 1296, 962,
        630, 301,
        /* Bank 15 */
        15, 374, 730, 1083, 1432, 1778, 2122, 2462, 2800, 3134,
        3466, 3795, 4071, 3747, 3426, 3108, 2792, 2478, 2168, 1859,
        1553, 1249, 948, 649, 352, 57,
        /* Bank 16 */
        25, 349, 670, 988, 1304, 1618, 1928, 2237, 2543, 2847,
        3148, 3447, 3744, 4039, 3861, 3571, 3283, 2996, 2712, 2430,
        2150, 1872, 1596, 1322, 1050, 780, 511, 244,
        /* Bank 17 */
        235, 525, 813, 1100, 1384, 1666, 1946, 2224, 2500, 2774,
        3046, 3316, 3585, 3852, 4075, 3812, 3551, 3291, 3033, 2777,
        2522, 2269, 2017, 1768, 1519, 1273, 1027, 784, 542, 301,
        62,
        /* Bank 18 */
        21, 284, 545, 805, 1063, 1319, 1574, 1827, 2079, 2328,
        2577, 2823, 3069, 3312, 3554, 3795, 4034, 3920, 3683, 3448,
        3215, 2983, 2752, 2522, 2294, 2067, 1842, 1617, 1394, 1173,
        952, 733, 515, 298, 82,
        /* Bank 19 */
        176, 413, 648, 881, 1113, 1344, 1574, 1802, 2029, 2254,
        2479, 2702, 2923, 3144, 3363, 3581, 3798, 4014, 3964, 3750,
        3538, 3327, 3117, 2908, 2701, 2494, 2288, 2084, 1880, 1678,
        1477, 1276, 1077, 878, 681, 485, 289, 95,
        /* Bank 20 */
        132, 346, 558, 769, 979, 1188, 1395, 1602, 1808, 2012,
        2216, 2418, 2619, 2820, 3019, 3218, 3415, 3611, 3807, 4001,
        3997, 3805, 3613, 3423, 3233, 3044, 2856, 2669, 2483, 2298,
        2113, 1930, 1747, 1565, 1384, 1204, 1024, 846, 668, 491,
        315, 139,
        /* Bank 21 */
        99, 291, 483, 673, 863, 1052, 1240, 1427, 1613, 1798,
        1983, 2166, 2349, 2531, 2712, 2892, 3072, 3250, 3428, 3605,
        3781, 3957, 4061, 3887, 3714, 3541, 3370, 3199, 3029, 2859,
        2691, 2523, 2355, 2189, 2023, 1858, 1694, 1530, 1367, 1204,
        1043, 881, 721, 561, 402, 244, 86,
        /* Bank 22 */
        35, 209, 382, 555, 726, 897, 1067, 1237, 1405, 1573,
        1741, 1907, 2073, 2238, 2402, 2566, 2729, 2892, 3053, 3215,
        3375, 3535, 3694, 3852, 4010, 4025, 3868, 3712, 3557, 3402,
        3248, 3094, 2941, 2789, 2637, 2486, 2335, 2185, 2035, 1887,
        1738, 1590, 1443, 1296, 1150, 1005, 860, 715, 571, 427,
        284, 142};

    static const int16_t kDCTMatrix[NUM_CEPS_ROM][NUM_CEPS_ROM] = {
        {/* DCT vector 0 */
         2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048,
         2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048, 2048,
         2048, 2048, 2048},
        {/* DCT vector 1 */
         2043, 2005, 1930, 1818, 1673, 1497, 1292, 1064, 816, 553,
         279, 0, -279, -553, -816, -1064, -1292, -1497, -1673, -1818,
         -1930, -2005, -2043},
        {/* DCT vector 2 */
         2029, 1878, 1589, 1181, 686, 140, -417, -942, -1398, -1750,
         -1972, -2048, -1972, -1750, -1398, -942, -417, 140, 686, 1181,
         1589, 1878, 2029},
        {/* DCT vector 3 */
         2005, 1673, 1064, 279, -553, -1292, -1818, -2043, -1930, -1497,
         -816, 0, 816, 1497, 1930, 2043, 1818, 1292, 553, -279,
         -1064, -1673, -2005},
        {/* DCT vector 4 */
         1972, 1398, 417, -686, -1589, -2029, -1878, -1181, -140, 942,
         1750, 2048, 1750, 942, -140, -1181, -1878, -2029, -1589, -686,
         417, 1398, 1972},
        {/* DCT vector 5 */
         1930, 1064, -279, -1497, -2043, -1673, -553, 816, 1818, 2005,
         1292, 0, -1292, -2005, -1818, -816, 553, 1673, 2043, 1497,
         279, -1064, -1930},
        {/* DCT vector 6 */
         1878, 686, -942, -1972, -1750, -417, 1181, 2029, 1589, 140,
         -1398, -2048, -1398, 140, 1589, 2029, 1181, -417, -1750, -1972,
         -942, 686, 1878},
        {/* DCT vector 7 */
         1818, 279, -1497, -2005, -816, 1064, 2043, 1292, -553, -1930,
         -1673, 0, 1673, 1930, 553, -1292, -2043, -1064, 816, 2005,
         1497, -279, -1818},
        {/* DCT vector 8 */
         1750, -140, -1878, -1589, 417, 1972, 1398, -686, -2029, -1181,
         942, 2048, 942, -1181, -2029, -686, 1398, 1972, 417, -1589,
         -1878, -140, 1750},
        {/* DCT vector 9 */
         1673, -553, -2043, -816, 1497, 1818, -279, -2005, -1064, 1292,
         1930, 0, -1930, -1292, 1064, 2005, 279, -1818, -1497, 816,
         2043, 553, -1673},
        {/* DCT vector 10 */
         1589, -942, -1972, 140, 2029, 686, -1750, -1398, 1181, 1878,
         -417, -2048, -417, 1878, 1181, -1398, -1750, 686, 2029, 140,
         -1972, -942, 1589},
        {/* DCT vector 11 */
         1497, -1292, -1673, 1064, 1818, -816, -1930, 553, 2005, -279,
         -2043, 0, 2043, 279, -2005, -553, 1930, 816, -1818, -1064,
         1673, 1292, -1497},
        {/* DCT vector 12 */
         1398, -1589, -1181, 1750, 942, -1878, -686, 1972, 417, -2029,
         -140, 2048, -140, -2029, 417, 1972, -686, -1878, 942, 1750,
         -1181, -1589, 1398},
        {/* DCT vector 13 */
         1292, -1818, -553, 2043, -279, -1930, 1064, 1497, -1673, -816,
         2005, 0, -2005, 816, 1673, -1497, -1064, 1930, 279, -2043,
         553, 1818, -1292},
        {/* DCT vector 14 */
         1181, -1972, 140, 1878, -1398, -942, 2029, -417, -1750, 1589,
         686, -2048, 686, 1589, -1750, -417, 2029, -942, -1398, 1878,
         140, -1972, 1181},
        {/* DCT vector 15 */
         1064, -2043, 816, 1292, -2005, 553, 1497, -1930, 279, 1673,
         -1818, 0, 1818, -1673, -279, 1930, -1497, -553, 2005, -1292,
         -816, 2043, -1064},
        {/* DCT vector 16 */
         942, -2029, 1398, 417, -1878, 1750, -140, -1589, 1972, -686,
         -1181, 2048, -1181, -686, 1972, -1589, -140, 1750, -1878, 417,
         1398, -2029, 942},
        {/* DCT vector 17 */
         816, -1930, 1818, -553, -1064, 2005, -1673, 279, 1292, -2043,
         1497, 0, -1497, 2043, -1292, -279, 1673, -2005, 1064, 553,
         -1818, 1930, -816},
        {/* DCT vector 18 */
         686, -1750, 2029, -1398, 140, 1181, -1972, 1878, -942, -417,
         1589, -2048, 1589, -417, -942, 1878, -1972, 1181, 140, -1398,
         2029, -1750, 686},
        {/* DCT vector 19 */
         553, -1497, 2005, -1930, 1292, -279, -816, 1673, -2043, 1818,
         -1064, 0, 1064, -1818, 2043, -1673, 816, 279, -1292, 1930,
         -2005, 1497, -553},
        {/* DCT vector 20 */
         417, -1181, 1750, -2029, 1972, -1589, 942, -140, -686, 1398,
         -1878, 2048, -1878, 1398, -686, -140, 942, -1589, 1972, -2029,
         1750, -1181, 417},
        {/* DCT vector 21 */
         279, -816, 1292, -1673, 1930, -2043, 2005, -1818, 1497, -1064,
         553, 0, -553, 1064, -1497, 1818, -2005, 2043, -1930, 1673,
         -1292, 816, -279},
        {/* DCT vector 22 */
         140, -417, 686, -942, 1181, -1398, 1589, -1750, 1878, -1972,
         2029, -2048, 2029, -1972, 1878, -1750, 1589, -1398, 1181, -942,
         686, -417, 140}};

#ifdef __cplusplus
}
#endif

#endif //__IMFCC_ROM_H__