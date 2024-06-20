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

int32_t util_model_check_positive_crossing(int32_t first, int32_t second, int32_t positive_threshold, int32_t negative_threshold)
{

    int32_t ncrossings = 0;

    // Positive Threshold Value Crossing

    // Postive Crossing
    if ((first < positive_threshold) && (second > positive_threshold))
    {
        ncrossings++;
    }

    // Negative Threshold Value Crossing

    // Postive Crossing
    if ((first < negative_threshold) && (second > negative_threshold))
    {
        ncrossings++;
    }

    return ncrossings;
}

int32_t util_model_check_negative_crossing(int32_t first, int32_t second, int32_t positive_threshold, int32_t negative_threshold)
{

    int32_t ncrossings = 0;

    // Positive Threshold Value Crossing
    // Negative Crossing
    if ((first > positive_threshold) && (second < positive_threshold))
    {
        ncrossings++;
    }

    // Negative Threshold Value Crossing
    // Negative Crossing
    if ((first > negative_threshold) && (second < negative_threshold))
    {
        ncrossings++;
    }

    return ncrossings;
}

int32_t utils_model_crossing_rate(ringb *rb, int32_t base_index, int32_t num_rows, int32_t positive_threshold, int32_t negative_threshold, crossingType cross_type)
{
    int32_t ncrossings = 0;
    int32_t first;  // must be 32-bit int32_t for bit mask operations
    int32_t second; // must be 32-bit int32_t for bit mask operations
    int32_t i;
    int32_t start_index = base_index & rb->mask;

    first = rb->buff[start_index++];

    for (i = 1; i < num_rows; i++)
    {
        second = MOD_READ_RINGBUF(rb, start_index++);

        switch (cross_type)
        {
        case NUMBER_OF_CROSSINGS_OVER_THRESHOLD_REGIONS:
            ncrossings += util_model_check_positive_crossing(first, second, positive_threshold, negative_threshold);
            ncrossings += util_model_check_negative_crossing(first, second, positive_threshold, negative_threshold);
            break;
        case NUMBER_OF_POSITIVE_CROSSINGS_OVER_THRESHOLD_REGIONS:
            ncrossings += util_model_check_positive_crossing(first, second, positive_threshold, negative_threshold);
            break;
        case NUMBER_OF_NEGATIVE_CROSSINGS_OVER_THRESHOLD_REGIONS:
            ncrossings += util_model_check_negative_crossing(first, second, positive_threshold, negative_threshold);
            break;
        default:
            break;
        }

        first = second;
    }

    printf("Number Crossing %d\n", ncrossings);

    return ncrossings;
}
