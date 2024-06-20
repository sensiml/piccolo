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




#ifndef _KB_ALGORITHMS_H_
#define _KB_ALGORITHMS_H_

#include "kb_common.h"
#include "kbutils.h"

/* kb_model_t is a data structure that contains all of the information about a pipeline. The parts relevant to kbalgorithms are:

kb_model->pdata_buffer->data,: This is the pointer to the first ring buffer
kb_model->sg_index: This is the position of the start of the index in the pringbuffer
kb_model->sg_length: This is the length of an identified segment of data.
kb_model->pFeatures: The pointer to the feature vector
kb_model->feature_vector_size: The size of the feature vector
kb_model->framedata: The most current sample of data after sensor transforms have been applied
kb_model->pSegParams: Pointer to the segmenter parameter data structure
*/

// clang-format off


#ifdef __cplusplus
extern "C"
{
#endif

/*STREAMING SENSOR TRANSFORMS
Expected behavior
1. Takes on frame of sample(s) at a time and pointer to the streaming ring buffer
2. perfroms some operation which requires time lagging the signal
3. replaces transforms the data in the frame of samples
4. returns 1, or -1 if the sbuffer needs more data before performing the transform

Note: At the moment these must be applied to all columns
*/

int32_t streaming_moving_average(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, int32_t filter_order);
int32_t streaming_downsample_by_averaging(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, int32_t filter_length);
int32_t streaming_downsample_by_decimation(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, int32_t filter_length);
int32_t streaming_high_pass_filter(ring_buffer_t *pringb, int16_t *pSample, int16_data_t *cols_to_use, float alpha);

/*SENSOR TRANSFORMS
Expected behavior
1. Takes one frame of sample(s) at a time and a pointer to the end of the FrameIDX array.
2. performs an operation such as magnitude and stores it into the FrameIDX array
3. Returns the number of points added to FrameIDX array

The frameData contains the data that will eventually be added to the ring buffer
*/

int32_t tr_sensor_magnitude(int16_t *rawdata, int16_data_t *cols_to_use, int16_t *input_data);
int32_t st_sensor_abs_average(int16_t *rawdata, int16_data_t *cols_to_use, int16_t *input_data);
int32_t st_sensor_average(int16_t *rawdata, int16_data_t *cols_to_use, int16_t *input_data);

/*SEGEMENTERS
1. Returns 1 if a segment is found, otherwise returns 0.
2. Must have either window size or max buffer length defined as part of the algorithm.  This is used to define the buffer size of the circular buffer.
3. Must make use of the ring buffer without modification to input data or data inside of the ringbuffer.
4. All parameters must be passed through a struct seg_params.
5. All user facing parameters must be defined defined in the python input contract with a corresponding c_param:index.
6. All flags must be part of seg_params as multiple segmenter can use the same segmenter.
7. The start of the segment is added to kb_model->sg_index
8. The length of the segment is added to kb_model->sg_length
9. On segment found, lock the ring buffer
10. Must have an init function which describes reset the ring buffer after a segment has been found.
*/

int32_t windowing_threshold_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams);
void windowing_threshold_segmenter_init(kb_model_t *kb_model, seg_params *segParams);
int32_t sg_manual(kb_model_t *model, int16_data_t *columns, seg_params *segParams);
void sg_manual_init(kb_model_t *model, seg_params *segParams);
int32_t sg_windowing(kb_model_t *model, int16_data_t *columns, seg_params *segParams);
void sg_windowing_init(kb_model_t *model, seg_params *segParams);
int32_t p2p_threshold(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams);
void p2p_threshold_init(kb_model_t *kb_model, seg_params *segParams);
int32_t max_min_threshold_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams);
void max_min_threshold_segmenter_init(kb_model_t *kb_model, seg_params *segParams);
int32_t general_threshold_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams);
void general_threshold_segmenter_init(kb_model_t *kb_model, seg_params *segParams);
int32_t double_peak_key_segmenter(kb_model_t *kb_model, int16_data_t *columns, seg_params *segParams);
void double_peak_key_segmenter_init(kb_model_t *kb_model, seg_params *segParams);
int32_t sg_cascade_windowing(kb_model_t *model, int32_t *columns, int32_t num_cols, seg_params *segParams);
void sg_cascade_windowing_init(kb_model_t *model, seg_params *segParams);

/*SEGMENT FILTERS

Expected Behavior
1. Returns 1 or 0. 1 if we the pipeline should continue, 0 if the pipeline should be terminated for this segment.
(note this can potentially cause issues where data is modified more than once in the case of a sliding window)
*/

int32_t sg_filter_mse(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
void reset_sg_filter_mse();
int32_t sg_filter_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
void reset_sg_filter_threshold();
int32_t sg_filter_energy_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
void reset_sg_filter_energy_threshold();
int32_t sg_filter_peak_ratio_energy_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
void reset_sg_filter_peak_ratio_energy_threshold();
int32_t sg_filter_vad_silk(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
void reset_sg_filter_vad_silk();
int32_t sg_filter_vad_silk_init(void);
int32_t sg_filter_vad_webrtc(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
void reset_sg_filter_vad_webrtc();
int32_t sg_filter_vad_webrtc_init(void);

/*SEGMENT TRANSFORMS

Expected Behavior
1. Operates only on a single segment of data. Starting at position kb_model->sg_index to a length of kb_model->sg_length.
3. Can modify data in the ring buffer, but is not allowed to add new data to the ring buffer.
(note this can potentially cause issues where data is modified more than once in the case of a sliding window)
*/

int32_t tr_segment_scale_factor(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
int32_t tr_segment_offset_factor(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
int32_t tr_segment_strip(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
int32_t tr_segment_pre_emphasis_filter(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
int32_t tr_segment_normalize(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
int32_t tr_segment_vertical_scale(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);
int32_t tr_segment_horizontal_scale(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params);

/*FEATURE GENERATORS

Expected Behavior
1. Create a single or multiple features from a segment of data. Starting at position kb_model->sg_index to a length of kb_model->sg_length.
2. Adds a feature as a float to the feature vector.
3. Returns the number of features added to the feature vector.
*/

int32_t fg_transpose_signal(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_interleave_signal(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_signal_duration(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_pct_time_over_zero(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_pct_time_over_sigma(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_pct_time_over_second_sigma(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_pct_time_over_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_abs_pct_time_over_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_time_avg_time_over_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_mean(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_zero_crossings(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_positive_zero_crossings(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_negative_zero_crossings(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_median(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_linear_regression(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_stdev(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_skewness(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_kurtosis(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_iqr(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_pct025(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_pct075(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_pct100(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_minimum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_maximum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_sum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_abs_sum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_abs_mean(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_stats_variance(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_amplitude_global_p2p_low_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_amplitude_global_p2p_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_amplitude_max_p2p_half_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_amplitude_peak_to_peak(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_amplitude_min_max_sum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_shape_ratio_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_shape_difference_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_shape_median_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_shape_absolute_median_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_mean_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_mean_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_zero_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_sigma_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_second_sigma_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_threshold_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_roc_threshold_with_offset_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_physical_average_movement_intensity(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_physical_variance_movement_intensity(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_physical_average_signal_magnitude_area(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_mfcc(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_mfe(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_fixed_width_histogram(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_min_max_scaled_histogram(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_dominant_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_spectral_entropy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_power_spectrum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_energy_average_energy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_energy_total_energy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_energy_average_demeaned_energy(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_sampling_downsample(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_max_column(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_min_column(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_min_max_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_mean_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_p2p_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_abs_max_column(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_correlation(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_mean_crossing_rate(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_mean_crossing_rate_with_offset(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_median_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_cross_column_peak_location_difference(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_sampling_downsample_avg_with_normalization(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_sampling_downsample_max_with_normalization(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_total_area(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_absolute_area(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_total_area_low_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_absolute_area_low_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_total_area_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_absolute_area_high_frequency(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_area_power_spectrum_density(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_peak_frequencies(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_harmonic_product_spectrum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);
int32_t fg_frequency_peak_harmonic_product_spectrum(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV);


// FILL_CUSTOM_FEATURE_GENERATORS

/*FEATURE VECTOR TRANSFORM

Expected Behavior
1. Takes a pointer to the feature generator and feature params.
2. Operates on the feature vectors in place
*/

int32_t min_max_scale(float *pFeatures, feature_vector_t *feature_vector, int32_t nfeats, int32_t start, int32_t total_features, FLOAT minbound, FLOAT maxbound, struct minmax *m);
int32_t normalize(FLOAT *pFV, int32_t numComps);
int32_t quantize_254(FLOAT *pFV, int32_t ncomps);

#ifdef __cplusplus
}
#endif
// clang-format on

#endif //_KB_ALGORITHMS_H_
