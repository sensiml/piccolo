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

static int32_t MA_Symmetric_mm(ringb *pringb, int32_t base_index, int32_t nFrameLen,
							   int32_t nWinSize, int32_t nColToUse, int32_t nSampleRate,
							   int32_t isAC, int32_t nFlagUseSampleRate,
							   int32_t nABSBeforSum, int32_t nABSAfterSum, int32_t nFGName,
							   FLOAT *pFV)
//
//      The version of Moving Average Symmetric which does minimum/maximum code.
//      Anything having to do with sum code is ignored.
//
{
	ringb *rb = pringb + nColToUse; // pointer to ring buffer

	int32_t latest_dc_sum = 0;		// sum of the sample values for the set of window size
	int32_t sum_dc_sum = 0;			// sum of all DC mean values;
	int32_t max_dc_sum, min_dc_sum; // latest max and min of sum for DC mean

	int32_t latest_ac_sum = 0;
	int32_t sum_ac_sum = 0;			// sum of all AC mean values;
	int32_t max_ac_sum, min_ac_sum; // latest max and min of sum of AC mean

	int32_t half_win_size_offset = nWinSize >> 1; // divided by 2

	float max = -FLOAT_MAX, min = FLOAT_MAX; // max and min of mean values

	int32_t i; // loop index variable

	// Calculate sum of sample values of the first window
	for (i = 0; i < nWinSize; i++)
	{
		latest_dc_sum += rb_read(rb, i + base_index);
	}

	// update statistical variables for the window
	max_dc_sum = min_dc_sum = latest_dc_sum;
	sum_dc_sum += nABSBeforSum == 1 ? fabs(latest_dc_sum) : latest_dc_sum;

	if (isAC != 0)
	{
		// Chris pointed out that it should be the mid sample of the window
		latest_ac_sum =
			(rb_read(rb, half_win_size_offset + base_index) * nWinSize) -
			latest_dc_sum;

		max_ac_sum = min_ac_sum = latest_ac_sum;
		sum_ac_sum +=
			nABSBeforSum == 1 ? fabs(latest_ac_sum) : latest_ac_sum;
	}
	// Bug fix to JSD-7213 by adding +1 to this loop
	for (i = 1; i < nFrameLen - nWinSize + 1; i++)
	{

		latest_dc_sum =
			latest_dc_sum - rb_read(rb, i - 1 + base_index) + rb_read(rb, i + nWinSize - 1 + base_index);
		sum_dc_sum +=
			nABSBeforSum == 1 ? fabs(latest_dc_sum) : latest_dc_sum;

		if (max_dc_sum < latest_dc_sum)
		{
			max_dc_sum = latest_dc_sum;
		}
		else if (min_dc_sum > latest_dc_sum)
		{
			min_dc_sum = latest_dc_sum;
		}

		if (isAC != 0)
		{
			// Chris pointed out that it should be the mid sample of the window
			latest_ac_sum =
				(rb_read(rb, i + half_win_size_offset + base_index) *
				 nWinSize) -
				latest_dc_sum;

			if (max_ac_sum < latest_ac_sum)
			{
				max_ac_sum = latest_ac_sum;
			}
			else if (min_ac_sum > latest_ac_sum)
			{
				min_ac_sum = latest_ac_sum;
			}
		}
	}

	if (isAC != 0)
	{
		max = (max_ac_sum * 1.0) / nWinSize; // AC
		min = (min_ac_sum * 1.0) / nWinSize;
	}
	else
	{
		max = (max_dc_sum * 1.0) / nWinSize; // DC
		min = (min_dc_sum * 1.0) / nWinSize;
	}

	switch (nFGName)
	{
	case global_p2p_high_frequency_name:
		*pFV = max - min;
		break;
	case global_p2p_low_frequency_name:
		*pFV = max - min;
		break;
	case max_p2p_half_high_frequency_name:
		*pFV = max - min;
		break;
	case absolute_area_high_frequency_name:
	case absolute_area_low_frequency_name:
	case total_area_low_frequency_name:
	case total_area_high_frequency_name:
	default:
		pFV[0] = 1234.5678; // error flag value
		break;
	}

	return 1;
}

static int32_t MA_Symmetric_sum(ringb *pringb, int32_t base_index, int32_t nFrameLen,
								int32_t nWinSize, int32_t nColToUse, int32_t nSampleRate,
								int32_t isAC, int32_t nFlagUseSampleRate,
								int32_t nABSBeforSum, int32_t nABSAfterSum,
								int32_t nFGName, FLOAT *pFV)
//
//      The version of Moving Average Symmetric which does summation code.
//      Anything having to do with minimum/maximum code is ignored.
//
{
	ringb *rb = pringb + nColToUse; // pointer to ring buffer

	int32_t latest_dc_sum = 0; // sum of the sample values for the set of window size
	int32_t sum_dc_sum = 0;	   // sum of all DC mean values;

	int32_t latest_ac_sum = 0;
	int32_t sum_ac_sum = 0; // sum of all AC mean values;

	int32_t half_win_size_offset = nWinSize >> 1; // divided by 2

	float sum_fv = 0; // sum of feature values,i.e, sum of each mean values

	float fSampleInterval =
		nFlagUseSampleRate == 1 ? (1.0f / (float)nSampleRate) : 1.0f;

	int32_t i; // loop index variable

	// Calculate sum of sample values of the first window
	for (i = 0; i < nWinSize; i++)
	{
		latest_dc_sum += rb_read(rb, i + base_index);
	}

	// update statistical variables for the window
	sum_dc_sum += nABSBeforSum == 1 ? fabs(latest_dc_sum) : latest_dc_sum;

	if (isAC != 0)
	{
		// Chris pointed out that it should be the mid sample of the window
		latest_ac_sum =
			(rb_read(rb, half_win_size_offset + base_index) * nWinSize) -
			latest_dc_sum;

		sum_ac_sum +=
			nABSBeforSum == 1 ? fabs(latest_ac_sum) : latest_ac_sum;
	}
	// Bug fix to JSD-7213 by adding +1 to this loop
	for (i = 1; i < nFrameLen - nWinSize + 1; i++)
	{

		latest_dc_sum =
			latest_dc_sum - rb_read(rb, i - 1 + base_index) + rb_read(rb, i + nWinSize - 1 + base_index);
		sum_dc_sum +=
			nABSBeforSum == 1 ? fabs(latest_dc_sum) : latest_dc_sum;

		if (isAC != 0)
		{
			// Chris pointed out that it should be the mid sample of the window
			latest_ac_sum =
				(rb_read(rb, i + half_win_size_offset + base_index) *
				 nWinSize) -
				latest_dc_sum;

			sum_ac_sum +=
				nABSBeforSum == 1 ? fabs(latest_ac_sum) : latest_ac_sum;
		}
	}

	if (isAC != 0)
	{
		sum_fv = (sum_ac_sum * fSampleInterval) / nWinSize; // AC
	}
	else
	{
		sum_fv = (sum_dc_sum * fSampleInterval) / nWinSize; // DC
	}

	sum_fv = nABSAfterSum == 1 ? fabs(sum_fv) : sum_fv;

	switch (nFGName)
	{
	case absolute_area_high_frequency_name:
		*pFV = sum_fv;
		break;
	case absolute_area_low_frequency_name:
		*pFV = sum_fv;
		break;
	case total_area_low_frequency_name:
		*pFV = fabs(sum_fv);
		break;
	case total_area_high_frequency_name:
		*pFV = sum_fv;
		break;
	default:
	case global_p2p_high_frequency_name:
	case global_p2p_low_frequency_name:
	case max_p2p_half_high_frequency_name:
		pFV[0] = 1234.5678; // error flag value
		break;
	}

	return 1;
}

int32_t MA_Symmetric(ringb *pringb, int32_t base_index, int32_t nFrameLen,
					 int32_t nWinSize, int32_t nColToUse, int32_t nSampleRate, int32_t isAC,
					 int32_t nFlagUseSampleRate, int32_t nABSBeforSum,
					 int32_t nABSAfterSum, int32_t nFGName, FLOAT *pFV)
{
	nWinSize = nWinSize * 2 + 1;

	switch (nFGName)
	{
	case global_p2p_high_frequency_name:
	case global_p2p_low_frequency_name:
	case max_p2p_half_high_frequency_name:
		MA_Symmetric_mm(pringb, base_index, nFrameLen,
						nWinSize, nColToUse, nSampleRate, isAC,
						nFlagUseSampleRate, nABSBeforSum,
						nABSAfterSum, nFGName, pFV);
		break;

	case absolute_area_high_frequency_name:
	case absolute_area_low_frequency_name:
	case total_area_low_frequency_name:
	case total_area_high_frequency_name:
		MA_Symmetric_sum(pringb, base_index, nFrameLen,
						 nWinSize, nColToUse, nSampleRate, isAC,
						 nFlagUseSampleRate, nABSBeforSum,
						 nABSAfterSum, nFGName, pFV);
		break;
	default:
		pFV[0] = 1234.5678; // error flag value
		break;
	}

	return 1;
}

//
