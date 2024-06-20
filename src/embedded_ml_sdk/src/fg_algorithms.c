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




// author: c.knorowski
#include "rb.h"
#include "kb_typedefs.h"
#include "kb_common.h"
#include "kbalgorithms.h"

/* define size of sortedData - The extern sortedData is only declared but not defined */
#define RB_SIZE 32768 // max segment length
#define MAX_COLS 6    // matching setting in server/settings.py
#define MAX_PARAMS 10
static int16_t cols_to_use[MAX_COLS] = {0, 1, 2, 3, 4, 5};
static float params[MAX_PARAMS] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static int16_data_t input_columns = {.data = cols_to_use,
                                     .size = MAX_COLS};
static float_data_t input_params = {.data = params,
                                    .size = MAX_PARAMS};

int16_t sortedData[RB_SIZE];
static int16_t buff[MAX_COLS][RB_SIZE]; // The data buffer the ring buffer uses
static int32_t sg_index;                // start of segment in ring buffer
static int32_t sg_length;               // length of segment in ring buffer
static int32_t num_rows;                // number of rows in column in input data
static int32_t num_cols;                // number of column in input data
static ring_buffer_t rb[MAX_COLS];      // ring buffers
static kb_model_t kb_model;             // model struct for storing ring buffer and segment info
static data_buffers_t data_buffer = {.data = rb,
                                     .size = MAX_COLS};

static void init_rb(int16_t *rb_inputs, int32_t num_cols, int32_t num_rows)
{
    int32_t i, j;
    memset(buff, 0, sizeof(int16_t) * MAX_COLS * RB_SIZE);
    memset(sortedData, 0, sizeof(int16_t) * RB_SIZE);
    for (i = 0; i < MAX_COLS; i++)
    {
        rb_init(&rb[i], buff[i], RB_SIZE);
        for (j = 0; j < num_rows; j++)
        {
            rb_add(&rb[i], rb_inputs[i * num_rows + j]);
        }
    }
}

static void init_kb_model(kb_model_t *kb_model, int16_t *rb_inputs, int32_t sg_length, int32_t num_cols, int32_t num_rows)
{

    init_rb(rb_inputs, num_cols, num_rows);
    kb_model->pdata_buffer = &data_buffer;
    kb_model->sg_index = 0;
    kb_model->sg_length = sg_length;
}
// Transpose Signal
void fg_transpose_signal_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_transpose_signal(&kb_model, &input_columns, &input_params, out_array);
}

// Interleave Signal
void fg_interleave_signal_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_interleave_signal(&kb_model, &input_columns, &input_params, out_array);
}

// Duration of the Signal
void fg_time_signal_duration_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_signal_duration(&kb_model, &input_columns, &input_params, out_array);
}

// Percent Time Over Zero
void fg_time_pct_time_over_zero_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_pct_time_over_zero(&kb_model, &input_columns, &input_params, out_array);
}

// Percent Time Over Sigma
void fg_time_pct_time_over_sigma_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_pct_time_over_sigma(&kb_model, &input_columns, &input_params, out_array);
}

// Percent Time Over Second Sigma
void fg_time_pct_time_over_second_sigma_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_pct_time_over_second_sigma(&kb_model, &input_columns, &input_params, out_array);
}

// Percent Time Over Threshold
void fg_time_pct_time_over_threshold_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_pct_time_over_threshold(&kb_model, &input_columns, &input_params, out_array);
}

// Abs Percent Time Over Threshold
void fg_time_abs_pct_time_over_threshold_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_abs_pct_time_over_threshold(&kb_model, &input_columns, &input_params, out_array);
}

// Average Time Over Threshold
void fg_time_avg_time_over_threshold_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_time_avg_time_over_threshold(&kb_model, &input_columns, &input_params, out_array);
}

// Mean
void fg_stats_mean_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_mean(&kb_model, &input_columns, &input_params, out_array);
}

// Zero Crossings
void fg_stats_zero_crossings_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_zero_crossings(&kb_model, &input_columns, &input_params, out_array);
}

// Positive Zero Crossings
void fg_stats_positive_zero_crossings_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_positive_zero_crossings(&kb_model, &input_columns, &input_params, out_array);
}

// Negative Zero Crossings
void fg_stats_negative_zero_crossings_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_negative_zero_crossings(&kb_model, &input_columns, &input_params, out_array);
}

// Median
void fg_stats_median_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_median(&kb_model, &input_columns, &input_params, out_array);
}

// Linear Regression Stats
void fg_stats_linear_regression_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_linear_regression(&kb_model, &input_columns, &input_params, out_array);
}

// Standard Deviation
void fg_stats_stdev_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_stdev(&kb_model, &input_columns, &input_params, out_array);
}

// Skewness
void fg_stats_skewness_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_skewness(&kb_model, &input_columns, &input_params, out_array);
}

// Kurtosis
void fg_stats_kurtosis_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_kurtosis(&kb_model, &input_columns, &input_params, out_array);
}

// Interquartile Range
void fg_stats_iqr_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_iqr(&kb_model, &input_columns, &input_params, out_array);
}

// 25th Percentile
void fg_stats_pct025_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_pct025(&kb_model, &input_columns, &input_params, out_array);
}

// 75th Percentile
void fg_stats_pct075_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_pct075(&kb_model, &input_columns, &input_params, out_array);
}

// 100th Percentile
void fg_stats_pct100_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_pct100(&kb_model, &input_columns, &input_params, out_array);
}

// Minimum
void fg_stats_minimum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_minimum(&kb_model, &input_columns, &input_params, out_array);
}

// Maximum
void fg_stats_maximum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_maximum(&kb_model, &input_columns, &input_params, out_array);
}

// Sum
void fg_stats_sum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_sum(&kb_model, &input_columns, &input_params, out_array);
}

// Absolute Sum
void fg_stats_abs_sum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_abs_sum(&kb_model, &input_columns, &input_params, out_array);
}

// Absolute Mean
void fg_stats_abs_mean_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_abs_mean(&kb_model, &input_columns, &input_params, out_array);
}

// Variance
void fg_stats_variance_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_stats_variance(&kb_model, &input_columns, &input_params, out_array);
}

// Global Peak to Peak of Low Frequency
void fg_amplitude_global_p2p_low_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_amplitude_global_p2p_low_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Global Peak to Peak of High Frequency
void fg_amplitude_global_p2p_high_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_amplitude_global_p2p_high_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Max Peak to Peak of first half of High Frequency
void fg_amplitude_max_p2p_half_high_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_amplitude_max_p2p_half_high_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Global Peak to Peak
void fg_amplitude_peak_to_peak_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_amplitude_peak_to_peak(&kb_model, &input_columns, &input_params, out_array);
}

// Global Min Max Sum
void fg_amplitude_min_max_sum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_amplitude_min_max_sum(&kb_model, &input_columns, &input_params, out_array);
}

// Ratio of Peak to Peak of High Frequency between two halves
void fg_shape_ratio_high_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_shape_ratio_high_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Difference of Peak to Peak of High Frequency between two halves
void fg_shape_difference_high_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_shape_difference_high_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Shape Median Difference
void fg_shape_median_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_shape_median_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Shape Absolute Median Difference
void fg_shape_absolute_median_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_shape_absolute_median_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Mean Difference
void fg_roc_mean_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_mean_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Mean Crossing Rate
void fg_roc_mean_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_mean_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Zero Crossing Rate
void fg_roc_zero_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_zero_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Sigma Crossing Rate
void fg_roc_sigma_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_sigma_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Second Sigma Crossing Rate
void fg_roc_second_sigma_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_second_sigma_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Threshold Crossing Rate
void fg_roc_threshold_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_threshold_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Threshold With Offset Crossing Rate
void fg_roc_threshold_with_offset_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_roc_threshold_with_offset_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Average of Movement Intensity
void fg_physical_average_movement_intensity_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_physical_average_movement_intensity(&kb_model, &input_columns, &input_params, out_array);
}

// Variance of Movement Intensity
void fg_physical_variance_movement_intensity_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_physical_variance_movement_intensity(&kb_model, &input_columns, &input_params, out_array);
}

// Average Signal Magnitude Area
void fg_physical_average_signal_magnitude_area_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_physical_average_signal_magnitude_area(&kb_model, &input_columns, &input_params, out_array);
}

// MFCC
void fg_frequency_mfcc_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_mfcc(&kb_model, &input_columns, &input_params, out_array);
}

// MFE
void fg_frequency_mfe_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_mfe(&kb_model, &input_columns, &input_params, out_array);
}

// Histogram
void fg_fixed_width_histogram_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_fixed_width_histogram(&kb_model, &input_columns, &input_params, out_array);
}

// Histogram Auto Scale Range
void fg_min_max_scaled_histogram_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_min_max_scaled_histogram(&kb_model, &input_columns, &input_params, out_array);
}

// Dominant Frequency
void fg_frequency_dominant_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_dominant_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Spectral Entropy
void fg_frequency_spectral_entropy_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_spectral_entropy(&kb_model, &input_columns, &input_params, out_array);
}

// Power Spectrum
void fg_frequency_power_spectrum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_power_spectrum(&kb_model, &input_columns, &input_params, out_array);
}

// Average Energy
void fg_energy_average_energy_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_energy_average_energy(&kb_model, &input_columns, &input_params, out_array);
}

// Total Energy
void fg_energy_total_energy_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_energy_total_energy(&kb_model, &input_columns, &input_params, out_array);
}

// Average Demeaned Energy
void fg_energy_average_demeaned_energy_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_energy_average_demeaned_energy(&kb_model, &input_columns, &input_params, out_array);
}

// Downsample
void fg_sampling_downsample_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_sampling_downsample(&kb_model, &input_columns, &input_params, out_array);
}

// Max Column
void fg_cross_column_max_column_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_max_column(&kb_model, &input_columns, &input_params, out_array);
}

// Min Column
void fg_cross_column_min_column_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_min_column(&kb_model, &input_columns, &input_params, out_array);
}

// Two Column Min Max Difference
void fg_cross_column_min_max_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_min_max_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Two Column Mean Difference
void fg_cross_column_mean_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_mean_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Two Column Peak To Peak Difference
void fg_cross_column_p2p_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_p2p_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Abs Max Column
void fg_cross_column_abs_max_column_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_abs_max_column(&kb_model, &input_columns, &input_params, out_array);
}

// Cross Column Correlation
void fg_cross_column_correlation_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_correlation(&kb_model, &input_columns, &input_params, out_array);
}

// Cross Column Mean Crossing Rate
void fg_cross_column_mean_crossing_rate_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_mean_crossing_rate(&kb_model, &input_columns, &input_params, out_array);
}

// Cross Column Mean Crossing with Offset
void fg_cross_column_mean_crossing_rate_with_offset_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_mean_crossing_rate_with_offset(&kb_model, &input_columns, &input_params, out_array);
}

// Two Column Median Difference
void fg_cross_column_median_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_median_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Two Column Peak Location Difference
void fg_cross_column_peak_location_difference_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_cross_column_peak_location_difference(&kb_model, &input_columns, &input_params, out_array);
}

// Downsample Average with Normalization
void fg_sampling_downsample_avg_with_normalization_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_sampling_downsample_avg_with_normalization(&kb_model, &input_columns, &input_params, out_array);
}

// Downsample Max With Normaliztion
void fg_sampling_downsample_max_with_normalization_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_sampling_downsample_max_with_normalization(&kb_model, &input_columns, &input_params, out_array);
}

// Total Area
void fg_area_total_area_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_total_area(&kb_model, &input_columns, &input_params, out_array);
}

// Absolute Area
void fg_area_absolute_area_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_absolute_area(&kb_model, &input_columns, &input_params, out_array);
}

// Total Area of Low Frequency
void fg_area_total_area_low_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_total_area_low_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Absolute Area of Low Frequency
void fg_area_absolute_area_low_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_absolute_area_low_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Total Area of High Frequency
void fg_area_total_area_high_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_total_area_high_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Absolute Area of High Frequency
void fg_area_absolute_area_high_frequency_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_absolute_area_high_frequency(&kb_model, &input_columns, &input_params, out_array);
}

// Absolute Area of Spectrum
void fg_area_power_spectrum_density_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_area_power_spectrum_density(&kb_model, &input_columns, &input_params, out_array);
}

// Peak Frequencies
void fg_frequency_peak_frequencies_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_peak_frequencies(&kb_model, &input_columns, &input_params, out_array);
}

// Harmonic Product Spectrum
void fg_frequency_harmonic_product_spectrum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_harmonic_product_spectrum(&kb_model, &input_columns, &input_params, out_array);
}

// Peak Harmonic Product Spectrum
void fg_frequency_peak_harmonic_product_spectrum_w(int16_t *in_array, float *out_array, float *params, int32_t num_params, int32_t num_cols, int32_t num_rows)
{

    init_kb_model(&kb_model, in_array, num_rows, num_cols, num_rows);
    input_columns.size = num_cols;
    for (int i = 0; i < num_params; i++)
    {
        input_params.data[i] = params[i];
    }
    input_params.size = num_params;
    fg_frequency_peak_harmonic_product_spectrum(&kb_model, &input_columns, &input_params, out_array);
}
