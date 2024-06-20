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

#ifndef __SENSIML_RECOGNITION_RUN_H__
#define __SENSIML_RECOGNITION_RUN_H__



int32_t sml_recognition_run(signed short *data_batch, int32_t batch_sz, uint8_t num_sensors, uint32_t sensor_id);
int32_t sml_recognition_run_single(signed short *data, uint32_t sensor_id);

#endif //__SENSIML_RECOGNITION_RUN_H__
