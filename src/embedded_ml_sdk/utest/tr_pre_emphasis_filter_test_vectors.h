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

// 5 columns of 10 rows
int16_t tr_segment_pre_emphasis_filter_tv[50] = {
    //1114_howling_4.txt
    -1551,
    -1672,
    -1756,
    -1726,
    -1482,
    -1022,
    -501,
    -150,
    -122,
    -408,

    //13789_growling_35.txt

    -2951,
    -3338,
    -3702,
    -4503,
    -4440,
    -4968,
    -5172,
    -4752,
    -5115,
    -4690,

    //24965_barking_37.txt

    475,
    385,
    178,
    -94,
    -359,
    -675,
    -994,
    -1280,
    -1439,
    -1548,

    //61025_eating_0.txt

    689,
    855,
    2097,
    1928,
    11,
    548,
    1035,
    1039,
    1665,
    1820,

    //332294_drinking_1.txt

    595,
    766,
    779,
    628,
    250,
    -395,
    -1080,
    -1600,
    -1825,
    -1845,

};
