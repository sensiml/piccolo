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

// THIS NEEDS TO BE REWRITTEN NOT CURRENTLY IMPLEMENTED
int32_t cagh(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
	return 0;
}
/*{
	int32_t row, icol, i;
	FLOAT G[3] = { 0 };	// Gravity vector
	//FLOAT S[3][3];		// Correlation matrix
	//FLOAT V_[3];		// N-1 means
	#ifdef DSW_BUILD
	OS_ERR_TYPE err;
	FLOAT *Vnorm = (FLOAT *)balloc(num_rows * sizeof(FLOAT), &err);
	FLOAT *Hnorm = (FLOAT *)balloc(num_rows * sizeof(FLOAT), &err);
	#else
	FLOAT *Vnorm = (FLOAT *)malloc(num_rows * sizeof(FLOAT));
	FLOAT *Hnorm = (FLOAT *)malloc(num_rows * sizeof(FLOAT));
	#endif
	FLOAT Vnorm_, Hnorm_, sigmaV, sigmaH, cov;

	FLOAT Gnorm;
	//FLOAT v;
	FLOAT a[3];
	FLOAT h[3];

	// At least 3 columns are required for this f/g, assuming the 3 columns are Ax, Ay, Az.
	if (cols_to_use->size< 3) return 0;

	// Compute the G-vector over the entire set of acceleration vectors
	for (icol = 0; icol < 3; icol++)
	{
		int32_t col = cols_to_use->data[icol];

		for (row = 0; row < num_rows; row++)
		{
			G[icol] += (FLOAT)get_axis__data(pringb + col, row);
		}
	}

	// Compute the mean (div by num_rows) and the norm
	for (icol = 0; icol < 3; icol++)
	{
		G[icol] /= (FLOAT)num_rows;
	}

	// Compute the length of G
	Gnorm = (FLOAT)SQRT(G[0] * G[0] + G[1] * G[1] + G[2] * G[2]);

	// Prepare to compute the H/V norm means
	Hnorm_ = 0.0;
	Vnorm_ = 0.0;

	// Compute A.G
	for (row = 0; row < num_rows; row++)
	{
		for (icol = 0; icol < 3; icol++)
			a[icol] = (FLOAT)get_axis_data(pringb + cols_to_use->data[icol], row);

		Vnorm[row] = a[0] * G[0] + a[1] * G[1] + a[2] * G[2];	// Dot product
																// Take orthogonal complement of v to estimate heading direction
		Vnorm_ += Vnorm[row];

		for (i = 0; i < 3; i++)
			h[i] = a[i] - Vnorm[row] * G[i] / Gnorm;

		// Compute the norm of orthogonal complement
		Hnorm[row] = (FLOAT)SQRT(h[0] * h[0] + h[1] * h[1] + h[2] * h[2]);

		Hnorm_ += Hnorm[row];
	}
	Vnorm_ /= num_rows;
	Hnorm_ /= num_rows;

	// Compute the sample covariance between Vnorm[0] and Hnorm[1]

	cov = 0;
	for (i = 0; i < num_rows; i++)
	{
		cov += (Hnorm[i] - Hnorm_)*(Vnorm[i] - Vnorm_);
	}
	cov /= num_rows - 1;

	// Compute the sigma for Vnorm and Hnorm
	// Start with summing the squares of the differences
	// between the samples and the sample means.
	for (i = 0, sigmaV = 0, sigmaH = 0; i < num_rows; i++)
	{
		sigmaV += (Vnorm[i] - Vnorm_)*(Vnorm[i] - Vnorm_);
		sigmaH += (Hnorm[i] - Hnorm_)*(Hnorm[i] - Hnorm_);
	}

	// Finally divide sums by n-1 and take square root
	sigmaV = SQRT(sigmaV/(num_rows - 1));
	sigmaH = SQRT(sigmaH/(num_rows - 1));

	*pFV = cov / (sigmaH * sigmaV);
	return 1;
}
*/