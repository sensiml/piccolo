# ----------------------------------------------------------------------
# Copyright (c) 2022 SensiML Corporation
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# ----------------------------------------------------------------------


THIS_DIR          := $(shell dirname $(abspath $(lastword $(MAKEFILE_LIST))))
OUT               := $(abspath $(THIS_DIR))

IFLAGS := -I../include -I. -I../../server/codegen/templates/common/
CFLAGS += -std=c99 -fPIC -fno-builtin -Werror $(IFLAGS)

fgsrc_path := ../src/
fgsrc := \
fftr.c \
imfcc.c \
fixlog.c \
fg_algorithms.c \
rb.c \
crossing_rate.c \
std.c \
mean.c \
sorted_copy.c \
sortarray.c \
sum.c \
stat_mean.c \
stat_moment.c \
fftr_utils.c \
utils_array.c \
utils_buffer_mean.c \
utils_buffer_median.c \
utils_buffer_argmax.c \
utils_buffer_std.c \
utils_buffer_min_max.c \
utils_buffer_max.c \
utils_bitwise_abs_val.c \
utils_buffer_pass_threshold.c \
utils_buffer_abs_max.c \
utils_buffer_cumsum.c \
utils_buffer_min.c \
utils_buffer_variance.c \
utils_buffer_absmean.c \
utils_buffer_abssum.c \
utils_buffer_autoscale.c \
utils_model_total_area.c \
utils_model_cross_column.c \
utils_model_cross_difference.c \
utils_model_mean_crossing_rate.c \
utils_model_total_energy.c \
utils_model_stats_max_min.c \
utils_model_pct_time_over_sigma.c \
utils_model_pct_time_over_threshold.c \
utils_model_crossing_rate.c \
dsp_dtw_distance.c \
ma_symmetric.c \
array_contains.c \
ratio_diff_impl.c \
max_min_high_low_freq.c \
stats_percentile_presorted.c \
fg_transpose_signal.c \
fg_interleave_signal.c \
fg_time_signal_duration.c \
fg_time_pct_time_over_zero.c \
fg_time_pct_time_over_sigma.c \
fg_time_pct_time_over_second_sigma.c \
fg_time_pct_time_over_threshold.c \
fg_time_abs_pct_time_over_threshold.c \
fg_time_average_time_over_threshold.c \
fg_stats_mean.c \
fg_stats_zero_crossings.c \
fg_stats_positive_zero_crossings.c \
fg_stats_negative_zero_crossings.c \
fg_stats_median.c \
fg_stats_linear_regression.c \
fg_stats_stdev.c \
fg_stats_skewness.c \
fg_stats_kurtosis.c \
fg_stats_iqr.c \
fg_stats_pct025.c \
fg_stats_pct075.c \
fg_stats_pct100.c \
fg_stats_minimum.c \
fg_stats_maximum.c \
fg_stats_sum.c \
fg_stats_abs_sum.c \
fg_stats_abs_mean.c \
fg_stats_variance.c \
fg_amplitude_global_p2p_low_frequency.c \
fg_amplitude_global_p2p_high_frequency.c \
fg_amplitude_max_p2p_half_high_frequency.c \
fg_amplitude_peak_to_peak.c \
fg_amplitude_min_max_sum.c \
fg_shape_ratio_high_freq.c \
fg_shape_difference_high_freq.c \
fg_shape_median_difference.c \
fg_shape_absolute_median_difference.c \
fg_roc_mean_difference.c \
fg_roc_mean_crossing_rate.c \
fg_roc_zero_crossing_rate.c \
fg_roc_sigma_crossing_rate.c \
fg_roc_second_sigma_crossing_rate.c \
fg_roc_threshold_crossing_rate.c \
fg_roc_threshold_with_offset_crossing_rate.c \
fg_physical_average_movement_intensity.c \
fg_physical_variance_movement_intensity.c \
fg_physical_average_signal_magnitude_area.c \
fg_frequency_mfcc.c \
fg_frequency_mfe.c \
fg_histogram.c \
fg_min_max_scaled_histogram.c \
fg_frequency_dominant_frequency.c \
fg_frequency_spectral_entropy.c \
fg_frequency_power_spectrum.c \
fg_energy_average_energy.c \
fg_energy_total_energy.c \
fg_energy_average_demeaned_energy.c \
fg_sampling_downsample.c \
fg_cross_max_column.c \
fg_cross_min_column.c \
fg_cross_min_max_difference.c \
fg_cross_mean_difference.c \
fg_cross_p2p_difference.c \
fg_cross_abs_max_column.c \
fg_cross_column_corr.c \
fg_cross_column_mean_crossing_rate.c \
fg_cross_column_mean_crossing_rate_with_offset.c \
fg_cross_median_difference.c \
fg_cross_peak_location_difference.c \
fg_sampling_downsample_avg_with_normalization.c \
fg_sampling_downsample_max_with_normalization.c \
fg_area_total_area.c \
fg_area_absolute_area.c \
fg_area_total_area_low_frequency.c \
fg_area_absolute_area_low_frequency.c \
fg_area_total_area_high_frequency.c \
fg_area_absolute_area_high_frequency.c \
fg_area_power_spectrum_density.c \
fg_peak_frequencies.c \
fg_frequency_harmonic_product_spectrum.c \
fg_frequency_peak_harmonic_product_spectrum.c \


fgsrc_full := $(addprefix $(fgsrc_path), $(fgsrc))
fgobjs_full := $(patsubst %.c, %.o, $(fgsrc_full))
fgobjs_local := $(patsubst %.c, %.o, $(fgsrc))

SRC := $(fgsrc_full)
OBJS := $(patsubst %.c, %.o, $(fgobjs_local))
COBJS := $(patsubst %.c, %.o, $(SRC))

LIB = $(OUT)/fg_algorithms.a

define copyofiles
#   ex1 := $(foreach of1,$(srcofiles1),cp -f $(of1) src/ &&)
#   ex1 += $(foreach of2,$(srcofiles2),cp -f $(of2) src/sensiml_sdk/ &&)

    for of1 in $(fgobjs_full); do \
        mv $$of1 ./; \
    done

endef

$(OUT)/%.o:$(SRC)
	@echo "what am i doing"
	@echo $(ANSI_RED)"[cPP]"$(ANSI_OFF) $@ $^
	@echo $(COBJS)
	$(AT)$(CC) $(CFLAGS) -c -o $@ $^



$(LIB): $(COBJS)
	@echo "making lib"
	$(call copyofiles)
	@echo $(LDFLAGS)
	$(AT)$(AR) rcs $@ $(OBJS)
	$(AT)$(CC) -shared -Wl,-soname,libfg_algorithms.so -o libfg_algorithms.so *.o
	# use this on mac
	#$(AT)$(CC) -shared -Wl,-install_name,libfg_algorithms.so -o libfg_algorithms.so *.o


clean:
	@echo $(ANSI_RED)"[CLEAN]"$(ANSI_OFF) $@
	rm -f $(OBJS) $(LIB)
	rm -f *.so

main: $(LIB)


all: lib

.PHONY:	lib all clean installofiles

