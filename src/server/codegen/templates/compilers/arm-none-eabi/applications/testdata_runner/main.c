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

#include "kb.h"
#include "kb_defines.h"
#include "testdata.h"
#include "kb_output.h"

static char str_buffer[2048];
#if SML_PROFILER
float recent_fv_times[MAX_VECTOR_SIZE];
uint32_t recent_fv_cycles[MAX_VECTOR_SIZE];
#endif

void sml_output_results(int32_t model_index, int32_t model_result)
{
    bool feature_vectors = true;
    int32_t size = 0;
    kb_sprint_model_result(model_index, str_buffer, false, false, false);
    printf("%s\n", str_buffer);
#if SML_PROFILER
    memset(str_buffer, 0, 2048);
    kb_print_model_cycles(model_index, str_buffer, recent_fv_cycles);
    printf("%s\n", str_buffer);
    memset(str_buffer, 0, 2048);
    kb_print_model_times(model_index, str_buffer, recent_fv_times);
    printf("%s\n", str_buffer);
#endif
};

int32_t main(void)
{
    kb_model_init();
    int32_t ret = 0;
    int32_t index = 0;
    int32_t num_sensors = 0;
    int16_t *data;

    while (1)
    {

        for (index = 0; index < TD_NUMROWS; index++)
        {
            data = (int16_t *)&testdata[index];
            // FILL_RUN_MODEL_CUSTOM
            // FILL_RUN_MODEL_MOTION
            // FILL_RUN_MODEL_AUDIO
        }
    }
}
