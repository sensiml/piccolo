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
#include "kb_output.h"

// FILL_USE_TEST_DATA
#ifdef SML_USE_TEST_DATA
#include "testdata.h"
int32_t td_index = 0;
#endif // SML_USE_TEST_DATA

static char str_buffer[2048];

void sml_output_results(int32_t model_index, int32_t model_result)
{
  int32_t size = 0;
  kb_sprint_model_result(model_index, str_buffer, false, false, false);
  printf("%s\n", str_buffer);
};

uint16_t sml_recognition_run(int16_t *data, int32_t num_sensors)
{
  int32_t ret;
#ifdef SML_USE_TEST_DATA
  ret = kb_run_model((int16_t *)&testdata[td_index++], TD_NUMCOLS, 0);
  if (td_index >= TD_NUMROWS)
  {
    td_index = 0;
  }
  if (ret >= 0)
  {
    sml_output_results(0, ret);
    kb_reset_model(0);
  }
#else
// FILL_RUN_MODEL_CUSTOM
#endif
  return ret;
}
