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




#include "kbutils.h"

FLOAT stats_percentile_presorted(const int16_t *input_data, int32_t nframes, FLOAT pct)
{
	int32_t idx;
	int32_t nteger;
	FLOAT result;

	if (pct <= 0.0)
		return (FLOAT)input_data[0];
	if (pct >= 1.0)
		return (FLOAT)input_data[nframes - 1];

	// Compute percentile
	FLOAT index = pct * (nframes - 1);

	FLOAT finteger;
	FLOAT frac = (FLOAT)MODF(index, &finteger);

	if (finteger <= (FLOAT)(nframes - 1))
		nteger = (int32_t)finteger;
	else
		return input_data[nframes - 1];

	if (frac == 0.0)
	{
		idx = (int32_t)index;
		result = input_data[idx];
	}
	else
	{
		result = ((FLOAT)1.0 - frac) * input_data[nteger] + frac * input_data[nteger + 1];
	}

	return result;
}
