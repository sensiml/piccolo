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




#include <stdio.h>
#include "kbalgorithms.h"
#include "fftr_utils.h"

static void calc_peak_frequencies(FLOAT *pFV, int16_t *input_data, int32_t len, FLOAT sample_rate, FLOAT threshold, int32_t num_peaks, int32_t min_bin, int32_t max_bin)
{

    int32_t i;
    struct compx_int16_t *data;

    data = fftr_rm_as(input_data, len);

    int16_t val;
    int16_t min_peak = threshold;
    int32_t found_peaks = 0;
    int8_t peak_idx[num_peaks];

    for (int32_t i = 0; i < num_peaks; i++)
    {
        peak_idx[i] = 0;
    }

    for (i = min_bin + 1; i < max_bin; i++)
    {
        val = abs(data[i].real) + abs(data[i].imag);

        if (val > min_peak)
        {
            if (val > abs(data[i - 1].real) + abs(data[i - 1].imag))
            {
                if (val > (abs(data[i + 1].real) + abs(data[i + 1].imag)))
                {
                    for (int32_t j = 0; j < num_peaks; j++)
                    {
                        if ((abs(data[peak_idx[j]].real) + abs(data[peak_idx[j]].imag)) < val)
                        {
                            for (int32_t k = found_peaks + 1; k > j; k--)
                            {
                                peak_idx[k] = peak_idx[k - 1];
                            }
                            peak_idx[j] = i;
                            if (found_peaks < num_peaks)
                            {
                                found_peaks++;
                                min_peak = threshold;
                            }
                            else
                            {
                                min_peak = abs(data[peak_idx[num_peaks - 1]].real) + abs(data[peak_idx[num_peaks - 1]].imag);
                            }

                            break;
                        }
                    }
                }
            }
        }
    }

    for (int32_t j = 0; j < found_peaks; j++)
    {
        for (int32_t i = j + 1; i < found_peaks; i++)
        {
            if (peak_idx[i] < peak_idx[j])
            {
                threshold = peak_idx[i];
                peak_idx[i] = peak_idx[j];
                peak_idx[j] = threshold;
            }
        }
    }

    for (int32_t i = 0; i < num_peaks; i++)
    {
        pFV[i] = (FLOAT)(peak_idx[i] * sample_rate) / (FLOAT)len;
    }
}

int32_t fg_frequency_peak_frequencies(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
#define PEAK_FREQUNCIES_NUM_PARAMS 6
#define PEAK_FREQUENCIES_SAMPLE_RATE_PARAM_IDX 0
#define PEAK_FREQUENCIES_MIN_FREQUENCY_PARAM_IDX 1
#define PEAK_FREQUENCIES_MAX_FREQUENCY_PARAM_IDX 2
#define PEAK_FREQUENCIES_THRESHOLD_PARAM_IDX 3
#define PEAK_FREQUENCIES_NUM_PEAKS_PARAM_IDX 4
#define PEAK_FREQUENCIES_WINDOW_TYPE_PARAM_IDX 5

#if SML_DEBUG
    if (!kb_model || kb_model->sg_length <= 0 || !cols_to_use || cols_to_use->size <= 0 || !params || params->size != PEAK_FREQUNCIES_NUM_PARAMS || !pFV)
    {
        return 0;
    }
#endif

    FLOAT sample_rate = params->data[PEAK_FREQUENCIES_SAMPLE_RATE_PARAM_IDX];
    FLOAT min_freq = params->data[PEAK_FREQUENCIES_MIN_FREQUENCY_PARAM_IDX];
    FLOAT max_freq = params->data[PEAK_FREQUENCIES_MAX_FREQUENCY_PARAM_IDX];
    FLOAT threshold = params->data[PEAK_FREQUENCIES_THRESHOLD_PARAM_IDX];
    int32_t num_peaks = (int32_t)params->data[PEAK_FREQUENCIES_NUM_PEAKS_PARAM_IDX];

    int32_t icol, len;
    ringb *rb;
    int32_t start_index;

    int32_t min_bin = (int32_t)(min_freq * (FLOAT)kb_model->sg_length / sample_rate);
    int32_t max_bin = (int32_t)(max_freq * (FLOAT)kb_model->sg_length / sample_rate);

    if (max_bin > 512)
    {
        max_bin = 512;
    }

    if (kb_model->sg_length > NUM_FFTR)
    {
        len = NUM_FFTR;
    }
    else
    {
        len = kb_model->sg_length;
    }

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        int32_t i;
        rb = kb_model->pdata_buffer->data + cols_to_use->data[icol];
        start_index = kb_model->sg_index;
        ;

        for (i = 0; i < len; i++)
        {
            sortedData[i] = MOD_READ_RINGBUF(rb, start_index++);
        }

        calc_peak_frequencies(pFV, sortedData, len, sample_rate, threshold, num_peaks, min_bin, max_bin);
    }

    return num_peaks;
}
