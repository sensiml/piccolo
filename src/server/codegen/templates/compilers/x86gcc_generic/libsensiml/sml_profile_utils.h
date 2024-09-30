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

#ifndef __SML_PROFILE_UTILS_H__
#define __SML_PROFILE_UTILS_H__
#define _POSIX_C_SOURCE 200809L

#include <inttypes.h>
#include <math.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#ifdef __cplusplus // Only compile this when c++


static struct timespec ts_end;
static struct timespec ts_begin;
static long total_time_ms;
static long total_ns;

void sml_profile_reset_timer()
{
    memset(&ts_begin, 0, sizeof(timespec));
    memset(&ts_end, 0, sizeof(timespec));
}

void sml_profile_start_timer()
{
    clock_gettime(CLOCK_REALTIME, &ts_begin);
}

void sml_profile_stop_timer()
{
    clock_gettime(CLOCK_REALTIME, &ts_end);
}

uint32_t sml_profile_get_cycle_count()
{
    total_ns = ts_end.tv_nsec - ts_begin.tv_nsec;
    return(int32_t)total_ns;

}

float sml_profile_get_total_time()
{
    total_time_ms = round(total_ns / 1.0e6);
    return (float)total_time_ms * 1.0f;
}

float sml_profile_get_avg_iteration_time(uint32_t iterations)
{
    return (sml_profile_get_total_time())/(iterations * 1.0f);
}

#endif

#endif // __SML_PROFILE_UTILS_H__