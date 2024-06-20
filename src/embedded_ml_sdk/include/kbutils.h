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




#ifndef KBUTILS_H
#define KBUTILS_H

#include <stddef.h>
#include <stdint.h>
#include <stdbool.h>
#include <limits.h>

#include <math.h>
#define MODF modff
#define SQRT(x) sqrt((float)x)
#define ABS(x) fabs(x)
#define POW(x, y) pow((float)x, (float)y)
#define ROUND(x) (int32_t)(x + 0.5f)
#define sign(d) ((d) < 0 ? -1 : ((d) > (0)))
#include "string.h"

#include "stdint.h"
#include "stdlib.h"
#include "kb_typedefs.h"
#include "kb_common.h"
#include "rb.h"

#ifndef max
#define max(a, b) \
	({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a > _b ? _a : _b; })
#endif

#ifndef min
#define min(a, b) \
	({ __typeof__ (a) _a = (a); \
       __typeof__ (b) _b = (b); \
     _a < _b ? _a : _b; })
#endif

#ifndef MOD
#define MOD(a, b) \
	({ int _a = (a); \
       int _b = (b); \
	   int _r = _a % _b; \
     _r < 0 ? _r + _b : _r; })
#endif

#ifndef fabs
#define fabs(x) ((x) >= 0 ? (x) : (-(x)))
#endif

#define roundoff(x) (int32_t)(x + 0.5f)
#define LOG10(x) log10(x)

#ifndef INT_MIN
#define INT_MIN 0x80000000
#endif
#ifndef INT_MAX
#define INT_MAX 0x7FFFFFFF
#endif
#ifndef KB_SHORT_INT_MIN
#define KB_SHORT_INT_MIN SHRT_MIN
#endif
#ifndef KB_SHORT_INT_MAX
#define KB_SHORT_INT_MAX SHRT_MAX
#endif

enum convops
{
	OP_ABS_SUM = 0, // Compute absolute value of the area
	OP_SUM_ABS		// Compute sum of absolute values of area
};

struct minmax
{
	uint16_t index;
	float min;
	float max;
};

typedef enum _FGFunctionName_
{
	global_p2p_high_frequency_name = 0,
	global_p2p_low_frequency_name,
	max_p2p_half_high_frequency_name,
	absolute_area_high_frequency_name,
	absolute_area_low_frequency_name,
	total_area_low_frequency_name,
	total_area_high_frequency_name
} FGFunctionName;

// Modes
enum convmode
{
	MOD_RAW = 0, // MOD_RAW - No conversion will be done to the raw data before applying the operation
	MOD_LF,		 // MOD_LF - Data will be transformed to the moving average before applying the operation
	MOD_HF		 // MOD_HF - Data will have the moving average subtracted before applying the operation
};

// Modes
typedef enum _crossingType_
{
	CROSSING_RATE = 0,		 // Original version in KB transcode
	CROSSING_RATE_OVER_ZERO, // Added for zero crossing optimization
	CROSSING_RATE_OVER_SUM,	 // Added for mean crossing optimization
	NUMBER_OF_CROSSINGS_OVER_THRESHOLD,
	NUMBER_OF_POSITIVE_CROSSINGS_OVER_THRESHOLD,
	NUMBER_OF_NEGATIVE_CROSSINGS_OVER_THRESHOLD,
	NUMBER_OF_CROSSINGS_OVER_THRESHOLD_REGIONS,
	NUMBER_OF_POSITIVE_CROSSINGS_OVER_THRESHOLD_REGIONS,
	NUMBER_OF_NEGATIVE_CROSSINGS_OVER_THRESHOLD_REGIONS
} crossingType;
// Buffer Modes
#define BUFFER_NO_ABS 0	 // take no abs()
#define BUFFER_USE_ABS 1 // take abs() of the buffer

#define BUFFER_NO_OFFSET 0	// use no offset
#define BUFFER_USE_OFFSET 1 // use offset

#define FIND_MAX_VAL 0 // find the max
#define FIND_MIN_VAL 1 // find the min

#define USE_FIRST_SIGMA 1  // uses first sigma
#define USE_SECOND_SIGMA 2 // uses 2.0 sigma

#define USE_ZERO_VAL 0		// uses zero value
#define USE_THRESHOLD_VAL 1 // uses threshold value

#define FIND_P2P_VAL 0	   // find the P2P valuen
#define FIND_MIN_MAX_VAL 1 // finds the min max

#define FLOAT_MAX 3.3928236692093846346337460743177e+38f
#define FLOAT_MIN 5.8774717541114375398436826861112e-39f

#define KB_FLT_MAX (FLOAT)0x7f7fffff
#define KB_FLT_MIN -(KB_FLT_MAX)

#ifndef SMOOTHING_FACTOR
#define SMOOTHING_FACTOR 50
#endif
#ifndef PI
#define PI 3.1415926f
#endif
#ifndef FFT_N
#define FFT_N 128
#endif

// Pre allocated data structures that are used by sub functions
extern int32_t sorted_data_len;
extern int32_t feature_selection[];
extern int16_t sortedData[];

// clang-format off

#ifdef __cplusplus
extern "C"
{
#endif

int32_t tr_sensor_sensors(int16_t *rawdata, int16_data_t *cols_to_use, int16_t *input_data);

FLOAT calc_area(ringb *pringb, int32_t col, int32_t nframes, FLOAT sample_rate, int32_t smoothing_factor, int32_t mode, int32_t op);
int32_t max_min_high_low_freq(ringb *pringb, int32_t base_index, int32_t nframes, int32_t col, int32_t offset, int32_t sf, int32_t lowhigh, FLOAT *max, FLOAT *min);
void column_to_row_complex(ringb *pringb, int32_t col, int32_t nframes, struct compx *cmpxData, int32_t complen);
int32_t calculate_positive_crossing_xor(int16_t *signal, int32_t length);
int32_t calculate_negative_crossing_xor(int16_t *signal, int32_t length);
int32_t calculate_zc_with_xor(int16_t *signal, int32_t length);
int32_t calculate_zc_with_threshold_xor(int16_t *signal, int32_t length, int32_t threshold);
int32_t calculate_negative_crossing_rate_xor_threshold(int16_t *signal, int32_t length, int32_t threshold);
int32_t calculate_positive_crossing_rate_xor_threshold(int16_t *signal, int32_t length, int32_t threshold);



void sortarray(int16_t *a, int32_t len);
int16_t *sorted_copy(ringb *pringb, int32_t base_index, int32_t len, int32_t force_sort);
FLOAT kb_std(ringb *pringb, int32_t base_index, int32_t datalen);
FLOAT mean(ringb *pringb, int32_t base_index, int32_t datalen);
FLOAT stat_moment(ringb *pringb, int32_t base_index, int32_t datalen, int32_t moment);
FLOAT sum(ringb *pringb, int32_t base_index, int32_t datalen);

//INT returns
int32_t i_mean(ringb *pringb, int32_t base_index, int32_t datalen);

//BUFFER FUNCTIONS
FLOAT buffer_cumulative_sum_0(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t abs_val);
int16_t buffer_max_0(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t abs_val);
int32_t utils_model_total_area(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t abs_val);
int32_t utils_model_cross_column(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t abs_val);
int32_t utils_model_mean_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, FLOAT *pFV, int32_t offset);
int32_t utils_model_total_energy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t abs_val);
int32_t utils_model_stats_max_min(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t max);
int32_t utils_model_pct_time_over_sigma(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t second_sigma);
int32_t utils_model_pct_time_over_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t threshold_val);
int32_t utils_model_cross_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV, int32_t min_max);
int32_t utils_model_crossing_rate(ringb *rb, int32_t base_index, int32_t num_rows, int32_t positive_threshold, int32_t negative_threshold, crossingType cross_type);


FLOAT buffer_mean(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
FLOAT buffer_standard_deviation(ringb *pringb, int32_t base_index, int32_t offset, int32_t nrows);
FLOAT buffer_variance(ringb *pringb, int32_t base_index, int32_t offset, int32_t nrows);
FLOAT buffer_cumulative_sum(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
FLOAT buffer_absolute_mean(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
FLOAT buffer_absolute_cumulative_sum(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
FLOAT buffer_median(ringb *pringb, int32_t index, int32_t datalen);
int16_t buffer_min(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
int16_t buffer_max(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
int32_t buffer_min_max(ringb *pringb, int32_t base_index, int32_t nrows, int32_t offset, int32_t *min, int32_t *max);
int32_t buffer_argmax(ringb *pringb, int32_t base_index, int32_t datalen);
void buffer_autoscale(ringb *pringb, int32_t base_index, int32_t length);
bool buffer_pass_threshold(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t threshold);
bool buffer_pass_threshold_peak_ratio(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen, int32_t threshold_upper, int32_t threshold_lower, float_t ratio_limit);
int16_t buffer_abs_max(ringb *pringb, int32_t base_index, int32_t offset, int32_t datalen);
int32_t i_mean_buff(rb_data_t *buff, int32_t len);
int32_t i_std_buffer(rb_data_t *buffer, int32_t len);

//ARRAY FUNCTIONS
void remove_mean_data_float(FLOAT *pdata, int32_t len);
void autoscale_data_float(FLOAT *pdata, int32_t len);
void apply_hanning_float(FLOAT *pdata, int32_t len);
void remove_mean_data_int(int16_t *pdata, int32_t len);
void autoscale_data_int(int16_t *pdata, int32_t len);
void apply_hanning_int(int16_t *pdata, int32_t len);
void array_max_uint8(uint8_t *pSrc, uint32_t blockSize, uint8_t *pResult);

//FEATURE SELECTION FUNCTIONS
bool selection_contains(int32_t feature, int32_t num_feature_selection, int32_t *feature_selection);
int32_t selection_index(int32_t feature, int32_t num_feature_selection, int32_t *feature_selection);

FLOAT stats_percentile_presorted(const int16_t *input_data, int32_t nframes, FLOAT pct);

void saveSensorData(ringb *pringb, int16_t *rawdata, int32_t count);

int32_t MA_Symmetric(ringb *pringb, int32_t base_index, int32_t nFrameLen, int32_t nWinSize, int32_t nColToUse, int32_t nSampleRate,
					int32_t nFlagDC_AC, int32_t nFlagUseSampleRate, int32_t nABSBeforSum, int32_t nABSAfterSum, int32_t nFGName, FLOAT *pFV);

int32_t ratio_diff_impl(ringb *pringb, int32_t base_index, int32_t nlen, int32_t window_size, int32_t flag_h_l, float *out);

//OTHER UTILITY FUNCTIONS
uint16_t bitwise_absolute_value(int16_t x);

#ifdef __cplusplus
}
// clang-format on
#endif
#endif
