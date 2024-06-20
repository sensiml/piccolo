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




#include "rb.h"
#include "kbutils.h"
/*!
 * \brief Save raw sensor data into RAW_DATA_BUFFER in s16 format.
 *
 * \param rawdata Raw sensor data array pointer.
 * \param count Count of data values to save into the RAW_DATA_BUFFER array.
 */
void saveSensorData(ringb *pringb, int16_t *rawdata, int32_t count)
{
    int32_t i;

    for (i = 0; i < count; i++)
    {
        rb_add(pringb + i, *rawdata++);
    }

    return;
}

/*!
 * \brief Save raw sensor data into RAW_DATA_BUFFER in s16 format.
 *
 * \param rawdata Mixed size sensor data array.
 * \param row startcol in rows to the frame to update.
 * \param count Count of data values to save into the RAW_DATA_BUFFER array.
 */
void saveSenseDataOffset(ringb *pringb, int16_t *rawdata, int32_t startcol, int32_t count)
{
    int32_t icol;

    for (icol = startcol; icol < (count + startcol); icol++)
    {
        rb_add(pringb + icol, *rawdata++);
    }
    return;
}
