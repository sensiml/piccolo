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

// normalize - scale all vectors to the range -1.0 to 1.0

int32_t normalize(FLOAT *pFV, int32_t numComps)
{
	int32_t icomp;
	FLOAT max = KB_FLT_MIN;

	// Determine the maximum of absolute value of each component
	for (icomp = 0; icomp < numComps; icomp++)
	{
		FLOAT fval = fabsf(pFV[icomp]);
		if (max < fval)
			max = fval;
	}

	// Scale each component
	for (icomp = 0; icomp < numComps; icomp++)
	{
		pFV[icomp] = pFV[icomp] / max;
	}
	return numComps;
}
