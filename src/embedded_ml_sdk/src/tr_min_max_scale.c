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




#include "kbalgorithms.h"

/**
 * Transcoded from min_max_scale from tr_scale.py
 */
int32_t min_max_scale(float *pFeatures, feature_vector_t *feature_vector, int32_t nfeats, int32_t start, int32_t total_features, FLOAT minbound, FLOAT maxbound, struct minmax *m)
{
	int32_t index;
	int32_t i;
	FLOAT value;
	float *pdata_float;
	uint8_t *pdata_uint8;

	pdata_uint8 = (uint8_t *)feature_vector->data;
	pdata_float = (float *)feature_vector->data;

	for (i = 0; i < nfeats; i++)
	{
		index = (start + m[i].index) % total_features;
		// printf("%d: %f\n", index, pFeatures[index]);
		value = maxbound * (pFeatures[index] - m[i].min) / (m[i].max - m[i].min + 1.0e-10);
		if (value > maxbound)
			value = maxbound;
		if (value < minbound)
			value = minbound;
		if (feature_vector->typeID == 1)
		{
			pdata_uint8[i] = (uint8_t)value;
		}
		else
		{
			pdata_float[i] = (float)value;
		}
	}
	return nfeats;
}