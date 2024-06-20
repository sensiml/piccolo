cmake_minimum_required(VERSION 2.6)


# Locat PThread
set(THREADS_PREFER_PTHREAD_FLAG ON)
find_package(Threads REQUIRED)

# Locate GTest
find_package(GTest REQUIRED)
include_directories(${GTEST_INCLUDE_DIRS})

# where sensiml_sdk/include is
include_directories( ../include )
include_directories( ../../server/codegen/templates/common/ )

add_definitions( -DLINUX )
add_definitions( -DSML_DEBUG=1 )
add_definitions( -DENABLE_DTW_DISTANCE )

add_definitions( -DDEBUG )
add_definitions( -DUTEST )
add_definitions( -Wall )
add_definitions( -Werror )

# -g to add debug symbols; good for core dump debugging with gdb
set(CMAKE_BUILD_TYPE Debug)

# I don't know why these 2 lines do not work, so using add_definitions() instead
#set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG}" -Wall -Werror)
#set(CMAKE_C_FLAGS_DEBUG "${CMAKE_C_FLAGS_DEBUG}" -Wall -Werror)

# I don't know why I can't set compiler here, passing params to cmake instead
# see build.sh
#set(CMAKE_C_COMPLIER gcc)
#set(CMAKE_CXX_COMPLIER g++)

set( SENSIML_SDK
    ../src/utils_model_total_area.c
    ../src/utils_model_cross_column.c
    ../src/utils_model_mean_crossing_rate.c
    ../src/utils_model_total_energy.c
    ../src/utils_model_stats_max_min.c
    ../src/utils_model_pct_time_over_sigma.c
    ../src/utils_model_pct_time_over_threshold.c
    ../src/utils_model_crossing_rate.c
    ../src/utils_array.c
    ../src/rb.c
    ../src/mean.c
    ../src/std.c
    ../src/ma_symmetric.c
    ../src/sorted_copy.c
    ../src/stats_percentile_presorted.c
    ../src/sortarray.c
    ../src/fftr.c
    ../src/fftr_utils.c
    ../src/utils_buffer_cumsum.c
    ../src/utils_buffer_min.c
    ../src/utils_buffer_mean.c
    ../src/utils_buffer_min_max.c
    ../src/utils_buffer_abssum.c
    ../src/crossing_rate.c
    ../src/sum.c
    ../src/imfcc.c
    ../src/fixlog.c
    ../src/array_contains.c
    ../src/stat_moment.c
    ../src/tr_segment_strip
    ../src/tr_segment_pre_emphasis_filter.c
    ../src/fg_roc_zero_crossing_rate.c
    ../src/fg_frequency_mfcc.c
    ../src/fg_stats_stdev.c
    ../src/fg_area_total_area.c
    ../src/fg_area_total_area_high_frequency.c
    ../src/fg_area_total_area_low_frequency.c
    ../src/fg_roc_mean_crossing_rate.c
    ../src/fg_roc_sigma_crossing_rate.c
    ../src/fg_roc_second_sigma_crossing_rate.c
    ../src/fg_roc_mean_difference.c
    ../src/fg_time_pct_time_over_threshold.c
    ../src/fg_time_pct_time_over_zero.c
    ../src/fg_time_pct_time_over_sigma.c
    ../src/fg_time_pct_time_over_second_sigma.c
    ../src/fg_histogram.c
    ../src/fg_sampling_downsample.c
    ../src/fg_energy_average_energy.c
    ../src/fg_energy_total_energy.c
    ../src/fg_energy_average_demeaned_energy.c
    ../src/fg_time_signal_duration.c
    ../src/fg_frequency_dominant_frequency.c
    ../src/fg_frequency_spectral_entropy.c
    ../src/fg_physical_variance_movement_intensity.c
    ../src/fg_physical_average_movement_intensity.c
    ../src/fg_physical_average_signal_magnitude_area.c
    ../src/fg_transpose_signal.c
    ../src/fg_stats_abs_sum.c
    ../src/fg_area_absolute_area.c
    ../src/fg_area_absolute_area_high_frequency.c
    ../src/fg_area_absolute_area_low_frequency.c
    ../src/fg_stats_pct025.c
    ../src/fg_stats_pct075.c
    ../src/fg_stats_pct100.c
    ../src/fg_stats_iqr.c
    ../src/fg_stats_kurtosis.c
    ../src/fg_stats_maximum.c
    ../src/fg_stats_minimum.c
    ../src/fg_stats_mean.c
    ../src/fg_stats_median.c
    ../src/fg_stats_skewness.c
    ../src/fg_stats_abs_mean.c
    ../src/fg_stats_abs_sum.c
    ../src/fg_stats_sum.c
    ../src/fg_stats_positive_zero_crossings.c
    ../src/fg_sampling_downsample_avg_with_normalization.c
    ../src/st_average.c
    ../src/st_absolute_average.c
    ../src/fg_peak_frequencies.c
    ../src/tr_segment_horizontal_scale.c
    ../src/tr_segment_vertical_scale.c
    ../src/fg_amplitude_min_max_sum.c
    ../src/sg_filter_threshold.c
    ../src/sg_filter_mse.c
    ../src/fg_interleave_signal.c
    ../src/dsp_dtw_distance.c
    ../src/utils_buffer_median.c
    ../src/utils_buffer_argmax.c
    ../src/fg_cross_median_difference.c
    ../src/fg_cross_peak_location_difference.c
    ../src/fg_stats_zero_crossings.c
    ../src/fg_stats_negative_zero_crossings.c
    ../src/fg_stats_linear_regression.c
    ../src/utils_buffer_variance.c
    ../src/utils_buffer_std.c
    ../src/utils_buffer_autoscale.c
    ../src/fg_shape_median_difference.c
    ../src/fg_shape_absolute_median_difference.c
    ../src/tr_segment_normalize.c
    ../src/tr_segment_scale_factor.c
    ../src/tr_segment_offset_factor.c
    ../src/st_high_pass_filter.c
    ../src/fg_frequency_power_spectrum.c
    ../src/sg_filter_energy_threshold.c
    ../src/sg_filter_peak_ratio_energy_threshold.c
    ../src/utils_buffer_pass_threshold.c
    ../src/sg_filter_vad_webrtc.c
    ../src/sg_filter_vad_silk.c
    ../src/fg_frequency_harmonic_product_spectrum
    ../src/fg_frequency_peak_harmonic_product_spectrum
    ../src/kb_post_processing.c
    ../src/fg_roc_threshold_crossing_rate.c
)

set( KB_UTEST
    test_main.cpp
    test_rb.cpp    
    test_fg_roc_mean_crossing_rate.cpp
    test_fg_roc_sigma_crossing_rate.cpp
    test_fg_roc_second_sigma_crossing_rate.cpp    
    test_fg_roc_zero_crossing_rate.cpp
    test_fg_roc_threshold_crossing_rate.cpp  
    test_fg_stats_zero_crossings.cpp
    test_fg_stats_positive_zero_crossings.cpp    
    test_fg_stats_negative_zero_crossings.cpp        
    test_mean.cpp
    test_abs_sum.cpp    
    test_area_absolute_area.cpp
    test_fg_stats_maximum.cpp
    test_fftr_utils.cpp
    test_fftr_utils_int.cpp
    test_utils_array.cpp
    test_fg_stats_minimum.cpp
    test_tr_segment_strip.cpp
    test_fg_area_absolute_area_high_frequency.cpp
    test_fg_area_absolute_area_low_frequency.cpp   
    test_sum.cpp
    test_tr_segment_pre_emphasis_filter.cpp
    test_array.cpp
    test_fg_stats_stdev.cpp
    test_fg_stats_percentile.cpp
    test_fg_stats_iqr.cpp
    test_fg_stats_kurtosis.cpp
    test_fg_stats_mean.cpp
    test_fg_stats_median.cpp
    test_fg_stats_skewness.cpp
    test_fg_stats_abs_mean.cpp
    test_fg_stats_abs_sum.cpp
    test_fg_stats_sum.cpp
    test_fg_area_total_area.cpp
    test_fg_area_total_area_high_frequency.cpp
    test_fg_area_total_area_low_frequency.cpp   
    test_fg_roc_mean_difference.cpp
    test_fg_time_pct_time_over_zero.cpp
    test_fg_time_pct_time_over_sigma.cpp
    test_fg_time_pct_time_over_second_sigma.cpp
    test_fg_histogram.cpp
    test_stat_moment.cpp
    test_fg_sampling_downsample.cpp
    test_fg_energy_average_energy.cpp
    test_fg_energy_total_energy.cpp
    test_fg_energy_average_demeaned_energy.cpp
    test_fg_time_signal_duration.cpp
    test_ma_symmetric.cpp
    test_fg_frequency_dominant_frequency.cpp
    test_fg_frequency_spectral_entropy.cpp
    test_fg_physical_variance_movement_intensity.cpp
    test_fg_physical_average_movement_intensity.cpp
    test_fg_physical_average_signal_magnitude_area.cpp
    test_fg_transpose_signal.cpp
    test_fg_sampling_downsample_avg_with_normalization.cpp
    test_st_average.cpp
    test_st_absolute_average.cpp
    test_fg_peak_frequencies.cpp
    test_tr_segment_horizontal_scale.cpp
    test_tr_segment_vertical_scale.cpp
    test_fg_amplitude_min_max_sum.cpp
    test_sg_filter_threshold.cpp
    test_sg_filter_peak_ratio_energy_threshold.cpp
    test_fg_interleave_signal.cpp
    test_dsp_dtw_distance.cpp
    test_utils_buffer_median.cpp
    test_utils_buffer_argmax.cpp
    test_fg_cross_median_difference.cpp
    test_fg_cross_peak_location_difference.cpp
    test_fg_stats_linear_regression.cpp
    test_fg_shape_median_difference.cpp
    test_fg_shape_absolute_median_difference.cpp
    test_fg_stats_linear_regression_edge_case.cpp
    test_tr_segment_normalize.cpp
    test_tr_segment_scale_factor.cpp
    test_tr_segment_offset_factor.cpp
    test_sg_filter_mse.cpp
    test_st_high_pass_filter.cpp
    test_fg_frequency_power_spectrum.cpp
    test_sg_filter_energy_threshold.cpp
    test_sg_filter_vad_webRTC.cpp
    test_sg_filter_vad_silk.cpp
    test_fg_frequency_harmonic_product_spectrum
    test_kb_post_processing.cpp
)#
# removed for
# test_fg_mfcc.cpp


#[SDL-233] 1/10/2018 Justin Moore:
#Removed because it is broken:
#test_fg_convolution_avg_large.cpp

# Link runTests with what we want to test and the GTest and pthread library
add_executable(kbgtest
    ${SENSIML_SDK}
    ${KB_UTEST}
)

# GTest needs pthread lib to be linked in
target_link_libraries(kbgtest ${GTEST_LIBRARIES} pthread)
target_link_libraries(kbgtest ${GTEST_LIBRARIES} Threads::Threads)

# KB needs math lib to be linked in - this is -lm to gcc
target_link_libraries(kbgtest m)
