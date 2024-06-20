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




#include "kbalgorithms.h"

/*!
 * \brief Transform the sensor data into magnitude and add it to input_data
 *
 * \param rawdata Raw sensor data array pointer.
 * \param cols_to_use array of columns to use from rawdata
 * \param num_cols number of columns to use
 * \param input_data Pointer to the new framedata array
 */
int32_t tr_sensor_magnitude(int16_t *rawdata, int16_data_t *cols_to_use, int16_t *input_data)
{
    int32_t icol;
    int32_t col;

    int32_t norm = 0;

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        col = cols_to_use->data[icol];
        norm += rawdata[col] * rawdata[col];
    }

    norm = SQRT(norm);

    if (cols_to_use->size > 0)
    {
        input_data[0] = (uint16_t)(norm / cols_to_use->size);
    }
    else
    {
        input_data[0] = (uint16_t)(norm);
    }

    return 1;
}
