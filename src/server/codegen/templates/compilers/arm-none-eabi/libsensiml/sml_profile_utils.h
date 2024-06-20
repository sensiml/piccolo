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

#define SML_PROFILE_MHZ 1024000
#define SML_PROFILE_CLK (80 * SML_PROFILE_MHZ)

volatile uint32_t *DWT_CYCCNT  ;
volatile uint32_t *DWT_CONTROL ;
volatile uint32_t *SCB_DEMCR   ;

void sml_profile_reset_timer()
{
    DWT_CYCCNT   = (int32_t *)0xE0001004; //address of the register
    DWT_CONTROL  = (int32_t *)0xE0001000; //address of the register
    SCB_DEMCR    = (int32_t *)0xE000EDFC; //address of the register
    *SCB_DEMCR   = *SCB_DEMCR | 0x01000000;
    *DWT_CYCCNT  = 0; // reset the counter
    *DWT_CONTROL = 0;
}

void sml_profile_start_timer()
{
    *DWT_CONTROL = *DWT_CONTROL | 1 ; // enable the counter
}

void sml_profile_stop_timer()
{
    *DWT_CONTROL = *DWT_CONTROL | 0 ; // disable the counter
}

uint32_t sml_profile_get_cycle_count()
{
    return *DWT_CYCCNT;
}

float sml_profile_get_total_time()
{
    return (float)(*DWT_CYCCNT * 1.0f)/(SML_PROFILE_CLK * 1.0f);
}

float sml_profile_get_avg_iteration_time(uint32_t iterations)
{
    return (sml_profile_get_total_time())/(iterations * 1.0f);
}

#endif // __SML_PROFILE_UTILS_H__