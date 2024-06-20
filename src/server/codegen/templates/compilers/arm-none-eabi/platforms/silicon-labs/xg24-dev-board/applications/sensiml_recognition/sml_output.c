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

#include "sml_output.h"
#include "kb_output.h"
#include "kb.h"

#define SERIAL_OUT_CHARS_MAX 2056

#ifdef __GNUC__
#pragma GCC diagnostic ignored "-Wunused-function"
#endif

// Test to see if code is being used
static char serial_out_buf[SERIAL_OUT_CHARS_MAX];
#if SML_PROFILER
float recent_fv_times[MAX_VECTOR_SIZE];
uint32_t recent_fv_cycles[MAX_VECTOR_SIZE];
#endif

void sml_output_results(uint16_t model, uint16_t classification)
{
    int32_t written = 0;
    memset(serial_out_buf, 0, SERIAL_OUT_CHARS_MAX);

    kb_sprint_model_result(model, serial_out_buf, true, true, true);

    printf("%s\n", serial_out_buf);
#if SML_PROFILER
    memset(serial_out_buf, 0, SERIAL_OUT_CHARS_MAX);
    kb_print_model_cycles(model, serial_out_buf, recent_fv_cycles);
    printf("%s\n", serial_out_buf);
    memset(serial_out_buf, 0, SERIAL_OUT_CHARS_MAX);
    kb_print_model_times(model, serial_out_buf, recent_fv_times);
    printf("%s\n", serial_out_buf);
#endif
}
