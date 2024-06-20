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




#include "rb.h"
#include "kbutils.h"

#define MIN(x, y) (x < y ? x : y)

/*
 * calc_area - compute various areas of a waveform
 *
 * Inputs
 *       col - which column to analyze
 *		nrows - number of rows in the array
 *       sample_rate - samples/sec.
 *		smoothing factor (how many data points on either side of a sample to use to compute the mean.)
 *		mode - conversion to perform on raw data values before the operation is performed
 *			 0 = raw data
 *			 1 = Low frequency
 *			 2 = high frequency
 *		op - operation to perform on converted data
 *
 * Output : FLOAT resultant value.
 *
 * The moving average for the signal is computed by starting with the average of
 * the first sample, over 'smoothing_factor' samples on either side of the sample.
 * The samples to the left of the first sample are assumed to be identical to the
 * first sample. Likewise, for samples to the right of the last sample.
 * Once this is done the average for each successive sample is computed as follows:
 * Sum = Sum - 1st sample in the last sum + sample following the last summed value
 * Avg = Sum/(smoothing factor + 1)
 * This is repeated for each sample.
 * This method avoids creating temporary arrays to hold the intermediate averages.
 */
FLOAT calc_area(ringb *pringb, int32_t col, int32_t nrows, FLOAT sample_rate, int32_t smoothing_factor, int32_t mode, int32_t op)
{
	int32_t irow;
	FLOAT dsum = 0.0, asum = 0.0;
	FLOAT darea = 0.0;
	FLOAT davg = 0.0;
	FLOAT dval = 0.0;		// Data value
	int32_t base_index = 0; // REPLACE THIS WITH AN INPUT WHEN THIS FUNCTION IS READY
	ringb *rb;
	int32_t start_index;

	// Process the samples
	for (irow = 0; irow < nrows; irow++)
	{
		int32_t icnt;

		asum = 0.0;
		rb = pringb + col;
		start_index = (base_index + irow) & rb->mask;
		for (icnt = 0; icnt < smoothing_factor; icnt++)
		{
			if (icnt + irow < nrows)
				asum += (FLOAT)rb->buff[start_index];
			start_index = (start_index + 1) & rb->mask;
		}
		davg = asum / MIN(smoothing_factor, nrows - irow);
		start_index = (base_index + irow) & rb->mask;
		dval = (FLOAT)rb->buff[start_index];

		if (mode == MOD_HF) // Use high-frequency components
		{
			dval -= davg; // Subtract the mean to get the high freq components.
		}
		else
		{
			dval = davg; // Use the mean for the low freq components.
		}

		// Perform the operation on the remaining 'modified' samples
		if (op == OP_ABS_SUM)
			dsum += dval / sample_rate;
		else if (op == OP_SUM_ABS)
			dsum += (dval < 0 ? -dval : dval) / sample_rate;
	}
	darea = dsum;
	if (op == OP_ABS_SUM)
	{
		if (dsum < 0.0)
			darea = -dsum;
	}
	return darea;
}
