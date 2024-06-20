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

/// This function is used to initalize the blank state of feature generators. See test_fg_stats_maximum.cpp for an example
//  of how it can be used

#define MAX_COLS 6
#define RB_SIZE 512 // since
#define MAX_FEATURE_VECTOR 128

static int16_t columns[MAX_COLS] = {0, 1, 2, 3, 4, 5};
static int16_data_t cols_to_use={.data=columns,
                                .size=MAX_COLS}; //
static int ret;                                        // return value from data frame
