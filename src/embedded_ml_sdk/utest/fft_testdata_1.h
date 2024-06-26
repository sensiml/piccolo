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


//
// want this in ROM, since the FFT we're using processes data in-place 
// (ie: the results overwrite the input).
//
static const float fft_testdata_1[512] = \
{
    301.0,
    297.0,
    294.0,
    292.0,
    290.0,
    290.0,
    294.0,
    294.0,
    297.0,
    302.0,
    308.0,
    315.0,
    318.0,
    321.0,
    324.0,
    326.0,
    326.0,
    325.0,
    324.0,
    323.0,
    324.0,
    318.0,
    314.0,
    312.0,
    309.0,
    306.0,
    305.0,
    302.0,
    298.0,
    294.0,
    292.0,
    289.0,
    290.0,
    291.0,
    291.0,
    289.0,
    288.0,
    287.0,
    285.0,
    283.0,
    281.0,
    276.0,
    273.0,
    270.0,
    268.0,
    267.0,
    262.0,
    259.0,
    256.0,
    254.0,
    255.0,
    255.0,
    258.0,
    263.0,
    267.0,
    271.0,
    275.0,
    280.0,
    286.0,
    292.0,
    295.0,
    298.0,
    302.0,
    307.0,
    311.0,
    315.0,
    316.0,
    318.0,
    319.0,
    320.0,
    319.0,
    321.0,
    321.0,
    323.0,
    327.0,
    330.0,
    333.0,
    337.0,
    341.0,
    348.0,
    358.0,
    365.0,
    373.0,
    380.0,
    388.0,
    395.0,
    403.0,
    411.0,
    418.0,
    425.0,
    432.0,
    439.0,
    447.0,
    453.0,
    458.0,
    464.0,
    471.0,
    478.0,
    482.0,
    486.0,
    494.0,
    497.0,
    502.0,
    507.0,
    511.0,
    519.0,
    522.0,
    525.0,
    530.0,
    535.0,
    537.0,
    541.0,
    543.0,
    544.0,
    546.0,
    547.0,
    548.0,
    549.0,
    549.0,
    549.0,
    551.0,
    551.0,
    552.0,
    553.0,
    555.0,
    558.0,
    561.0,
    563.0,
    567.0,
    572.0,
    575.0,
    579.0,
    584.0,
    587.0,
    589.0,
    591.0,
    593.0,
    595.0,
    596.0,
    596.0,
    597.0,
    594.0,
    594.0,
    595.0,
    593.0,
    590.0,
    588.0,
    585.0,
    580.0,
    576.0,
    573.0,
    569.0,
    566.0,
    564.0,
    563.0,
    563.0,
    564.0,
    566.0,
    565.0,
    563.0,
    563.0,
    557.0,
    550.0,
    541.0,
    529.0,
    515.0,
    501.0,
    485.0,
    471.0,
    457.0,
    445.0,
    431.0,
    412.0,
    392.0,
    373.0,
    358.0,
    342.0,
    327.0,
    317.0,
    314.0,
    319.0,
    311.0,
    307.0,
    299.0,
    283.0,
    266.0,
    245.0,
    216.0,
    185.0,
    155.0,
    133.0,
    119.0,
    123.0,
    135.0,
    149.0,
    166.0,
    183.0,
    194.0,
    204.0,
    216.0,
    235.0,
    265.0,
    305.0,
    349.0,
    396.0,
    452.0,
    521.0,
    598.0,
    662.0,
    700.0,
    708.0,
    696.0,
    662.0,
    623.0,
    582.0,
    525.0,
    478.0,
    437.0,
    407.0,
    386.0,
    376.0,
    350.0,
    331.0,
    316.0,
    291.0,
    256.0,
    227.0,
    196.0,
    170.0,
    154.0,
    134.0,
    126.0,
    109.0,
    96.0,
    87.0,
    73.0,
    65.0,
    54.0,
    44.0,
    36.0,
    32.0,
    24.0,
    20.0,
    21.0,
    24.0,
    26.0,
    24.0,
    21.0,
    21.0,
    24.0,
    24.0,
    25.0,
    25.0,
    25.0,
    26.0,
    28.0,
    30.0,
    31.0,
    34.0,
    39.0,
    40.0,
    46.0,
    48.0,
    52.0,
    57.0,
    62.0,
    67.0,
    73.0,
    77.0,
    80.0,
    86.0,
    88.0,
    93.0,
    99.0,
    106.0,
    112.0,
    127.0,
    142.0,
    156.0,
    169.0,
    188.0,
    204.0,
    220.0,
    238.0,
    260.0,
    282.0,
    305.0,
    328.0,
    349.0,
    372.0,
    396.0,
    418.0,
    436.0,
    456.0,
    478.0,
    495.0,
    519.0,
    535.0,
    551.0,
    571.0,
    594.0,
    611.0,
    628.0,
    648.0,
    668.0,
    685.0,
    702.0,
    714.0,
    722.0,
    727.0,
    727.0,
    726.0,
    727.0,
    730.0,
    735.0,
    739.0,
    737.0,
    731.0,
    719.0,
    700.0,
    677.0,
    653.0,
    625.0,
    602.0,
    582.0,
    560.0,
    538.0,
    516.0,
    496.0,
    476.0,
    453.0,
    436.0,
    423.0,
    412.0,
    404.0,
    394.0,
    386.0,
    381.0,
    378.0,
    375.0,
    370.0,
    365.0,
    353.0,
    340.0,
    328.0,
    312.0,
    299.0,
    285.0,
    273.0,
    264.0,
    259.0,
    263.0,
    264.0,
    264.0,
    263.0,
    261.0,
    261.0,
    263.0,
    264.0,
    265.0,
    263.0,
    264.0,
    262.0,
    259.0,
    253.0,
    245.0,
    243.0,
    240.0,
    233.0,
    224.0,
    217.0,
    210.0,
    202.0,
    195.0,
    190.0,
    188.0,
    183.0,
    179.0,
    175.0,
    170.0,
    168.0,
    166.0,
    166.0,
    165.0,
    165.0,
    165.0,
    166.0,
    168.0,
    169.0,
    169.0,
    172.0,
    174.0,
    174.0,
    176.0,
    181.0,
    182.0,
    183.0,
    184.0,
    187.0,
    190.0,
    193.0,
    195.0,
    200.0,
    205.0,
    211.0,
    215.0,
    221.0,
    228.0,
    234.0,
    239.0,
    247.0,
    256.0,
    263.0,
    269.0,
    275.0,
    286.0,
    293.0,
    301.0,
    309.0,
    317.0,
    320.0,
    325.0,
    332.0,
    339.0,
    345.0,
    350.0,
    357.0,
    362.0,
    365.0,
    368.0,
    371.0,
    379.0,
    386.0,
    392.0,
    398.0,
    402.0,
    408.0,
    413.0,
    418.0,
    425.0,
    430.0,
    433.0,
    437.0,
    442.0,
    445.0,
    451.0,
    453.0,
    456.0,
    459.0,
    461.0,
    462.0,
    465.0,
    467.0,
    469.0,
    470.0,
    472.0,
    475.0,
    476.0,
    478.0,
    479.0,
    481.0,
    483.0,
    485.0,
    486.0,
    486.0,
    486.0,
    489.0,
    491.0,
    492.0,
    494.0,
    497.0,
    501.0,
    503.0,
    506.0,
    510.0,
    516.0,
    519.0,
    523.0,
    529.0,
    533.0,
    537.0,
    542.0,
    547.0,
    551.0,
    554.0,
    556.0,
    559.0,
    562.0,
    567.0,
    574.0,
    579.0,
    587.0,
    592.0,
    595.0,
    597.0,
    602.0,
    604.0,
    605.0,
    605.0,
    604.0,
    604.0,
    603.0,
    600.0,
    597.0,
    593.0,
    588.0,
    579.0,
    571.0,
    560.0,
    547.0,
    527.0,
    512.0
};
