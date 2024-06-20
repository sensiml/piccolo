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

#ifndef __SENSOR_CONFIG_H__
#define __SENSOR_CONFIG_H__

#include <ArduinoJson.h>

//
// Most commonly used configurations to consider:
// - USE_BLE
// - SERIAL_BAUD_RATE
// - ODR_IMU_MAX / ODR_IMU


#define USE_BLE 0 //set to 1 to use BLE and 0 to use serial com (tty) port

/**
 * Serial Port Settings
 */

//by default: it seems that DCL uses 115200 and open gateway uses 115200 * 4 (460800)
//when used with open gateway, change the value to 115200 * 4 (460800)
//when used with DCL, change the value to 115200 * 4 (most suggested) or 115200 * 8
#define SERIAL_BAUD_RATE 115200 * 4


// this is used for debugging when BLE is used
#define SERIAL_BAUD_RATE_DEFAULT 115200


//odr of acc and gyro could be different, but we prefer to be the same for most cases
//supported ODRs (output data rate) of the IMU inside the BHI260 chip:
//12, 25, 50, 100, 200, 400, 800, 1600

//when using BLE: suggest to set up to 100
//when using serial: suggest to set up to 400, this depends on the performance of the PC being used as well
#define ODR_IMU 200



#define USE_SECOND_SERIAL_PORT_FOR_OUTPUT 0
#define CFG_IMITATE_NANO33BLE 0

#define CFG_LED_ON_DURATION 50
#define CFG_LED_OFF_DURATION 3000


#define ENABLE_ACCEL 1
#define ENABLE_GYRO  1
#define ENABLE_MAG   0
#define ENABLE_TEMP  0
#define ENABLE_HUMID 0
#define ENABLE_BARO  0  //ambient pressure sensor
#define ENABLE_GAS   0

#define ENABLE_AUDIO 0


#define ODR_ACC ODR_IMU
#define ODR_GYR ODR_IMU
#define ODR_MAG 25
#define ODR_TEMP 1
#define ODR_HUMID 1
#define ODR_BARO  1
#define ODR_GAS  1

const int32_t WRITE_BUFFER_SIZE = 256;  //about 164B

typedef unsigned long time_ms_t;

/**
 * BLE Settings
 */


#if USE_BLE
#define MAX_NUMBER_OF_COLUMNS 10
#define MAX_SAMPLES_PER_PACKET 1
#else
#define MAX_NUMBER_OF_COLUMNS 20
#define MAX_SAMPLES_PER_PACKET 6
#endif  // USE_BLE

#define DELAY_BRDCAST_JSON_DESC_SENSOR_CONFIG 1000



#if ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG || ENABLE_TEMP || ENABLE_HUMID || ENABLE_BARO || ENABLE_GAS
int32_t setup_sensors(JsonDocument& config_message, int32_t column_start);
int16_t* get_sensor_data_buffer();
int32_t update_sensor_data_col(int32_t startIndex);
#endif  //#if ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG

#endif  //__SENSOR_CONFIG_H__
