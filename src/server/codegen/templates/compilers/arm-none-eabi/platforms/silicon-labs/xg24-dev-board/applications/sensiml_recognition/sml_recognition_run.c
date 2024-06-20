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
#include "sml_output.h"
#include "sml_recognition_run.h"

// FILL_USE_TEST_DATA

#ifdef SML_USE_TEST_DATA
#include "testdata.h"
int32_t td_index = 0;
#endif // SML_USE_TEST_DATA

int32_t sml_recognition_run(signed short *data_batch, int32_t batch_sz, uint8_t num_sensors, uint32_t sensor_id)
{
	int32_t ret;

	int32_t batch_index = 0;
	signed short *data;
	for (batch_index = 0; batch_index < batch_sz; batch_index++)
	{
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
		data = &data_batch[batch_index * num_sensors];
// FILL_RUN_MODEL_MOTION
// FILL_RUN_MODEL_AUDIO
// FILL_RUN_MODEL_CUSTOM
#endif // SML_USE_TEST_DATA
	}
	return ret;
}
