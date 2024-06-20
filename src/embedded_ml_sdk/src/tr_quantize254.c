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

// quantize - convert feature vectors to the range 0-255

/* Uses the following algorithm to quantize the feature vectors

def q254(x) :
	x = x + 1.0     # Add 1.0 to the input value to ensure values between 0 and 2
	qx = x*127.0
	qx = qx.astype(np.int64)

	return (qx)
*/

int32_t quantize_254(FLOAT *pFV, int32_t ncomps)
{
	int32_t icomp;
	FLOAT range = 127.0;

	for (icomp = 0; icomp < ncomps; icomp++)
	{
		pFV[icomp] = (FLOAT)((int32_t)((pFV[icomp] + 1.0f) * range));
	}
	return ncomps;
}
