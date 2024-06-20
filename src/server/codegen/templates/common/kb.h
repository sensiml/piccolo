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




/**
 * @file kb.h
 *
 * @brief Contains the main APIs for interfacing with the Knowledge Pack.
 *
 */

#ifndef __KB_H__
#define __KB_H__
#include "kb_typedefs.h"
#include "kb_defines.h"
// Total Models in this Knowledge Pack
// FILL_MODEL_COUNT

// Model Indexes to use for calls
// FILL_KB_MODEL_INDEXES

// FILL_MAX_VECTOR_SIZE

// FILL_SENSOR_USAGES

//clang-format off
#ifdef __cplusplus
extern "C"
{
#endif

    /**
     * @brief Initialize the parameters of all the models, this function must be run
     * before calling any other functions in the knowledge pack.
     *
     * @return void.
     */
    void kb_model_init();

    /**
     * @brief Advance the model so it is ready for new sample data. Call this after
     * every classification event is received prior to passing in more data.
     *
     * This function will increment the feature bank index and call the
     * segmenter advance function.
     *
     * @param[in] model_index - index of the model to reset
     * @return 1 for success
     */
    int32_t kb_reset_model(int32_t model_index);

    /**
     * @brief Flush the internal data stored in the models ring buffer.
     *
     * Sets the
     *
     * @param[in] model_index - index of the model to reset
     */
    int32_t kb_flush_model_buffer(int32_t model_index);

    // MODEL RUN HIGH LEVEL APIs

    /**
     * @brief Stream single sample of data into model pipeline
     *
     * This is the main entry point into the pipeline. It is designed to work on streaming data
     * and takes a single timepoint of data as an array as input.
     *
     * This function implements the following logic:
     *   1. Runs any sensor transforms or sensor filters
     *   2. Adds that new to the internal ring buffer of the model
     *   3. Runs the segmentation against the ring buffer including the new sample
     *   4. Runs any segment filters or segment transforms
     *   5. Generates Features
     *   6. Runs any Feature Transforms
     *   7. Classify the resulting feature vector using the classifier and returns the result.
     *
     * @param[in] pSample Pointer to a single time point of data across sensors (ie. ax,ay,az)
     * @param[in] nsensors number of channels of data or columns in pSample
     * @param[in] model_index model index to run.
     * @returns Classification results. 0 if Unknown
     *                                 -1 when a segment hasn't yet been identified
     *                                 -2 when a segment has been filtered
     */
    int32_t kb_run_model(int16_t *pSample, int32_t nsensors, int32_t model_index);

    /**
     * @brief Add a custom segment to the pipeline
     *
     * Setup the model ring buffer with the user provided
     * buffer to be used as well as its size.
     *
     * @param[in] pSample Pointer to a buffer to use.
     * @param[in] len length of the ring buffer.
     * @param[in] nbuffs Number of buffers of length len to create in pBuffer pointer.
     * @param[in] model_index Model index to use.
     */
    void kb_add_segment(uint16_t *pBuffer, int32_t len, int32_t nbuffs, int32_t model_index);

    /**
     * @brief Used to run a segment of data through the pielines.
     *
     * This is the main entry point for running chunks of data. Use this after calling
     * kb_add_segment. Note, this skips the Sensor Transform and Sensor Filter Logic.
     *
     * This function implements the following logic:
     *   1. Runs the segmentation against the ring buffer including the new sample
     *   2. Runs any segment filters or segment transforms
     *   3. Generates Features
     *   4. Runs any Feature Transforms
     *   5. Classify the resulting feature vector using the classifier and returns the result.
     *
     * @param[in] model_index model index to run.
     * @returns Classification results. 0 if Unknown
     *                                 -1 when a segment hasn't yet been identified
     *                                 -2 when a segment has been filtered
     */
    int32_t kb_run_segment(int32_t model_index);

    // ADVANCED LOW LEVEL APIs for controlling the model pipeline

    /**
     * @brief Takes a single frame of data from the sensor at a time
     * adds the data to the models internal ring buffer
     *
     * @param[in] pSample pointer to the sensor data array.
     * @param[in] nsensors number of channels of data or columns in pSample
     * @param[in] model_index model index to run.
     * @returns 1 if added 0 if filtered.
     */
    int32_t kb_data_streaming(int16_t *pSample, int32_t nsensors, int32_t model_index);

    /**
     * @brief Performs segmentation on data stored in the models internal ring buffer
     *
     * @param[in] model_index model index to run.
     * @returns 1 if segment found -1 if filtered.
     */
    int32_t kb_segmentation(int32_t model_index);

    /**
     * @brief Reset the Feature Generator Bank Index to 0
     *
     * @param[in] model_index model index to run.
     * @returns Void.
     */
    void kb_feature_generation_reset(int32_t model_index);

    /**
     * @brief Generates features from the data stored in the models ring buffer
     *
     * @param[in] model_index model index to run.
     * @returns 1 if features generated -1 if filtered.
     */
    int32_t kb_feature_generation(int32_t model_index);

    /**
     * @brief Transform operations on the feature generators stored in the feature banks
     *  and places them into the model feature_vector array. This is performed before classification.
     *
     * @param[in] model_index model index to run.
     * @returns 1 if success
     */
    uint16_t kb_feature_transform(int32_t model_index);

    /**
     * @brief Increment the feature bank by one for a model
     *
     * @param[in] model_index model index to run.
     * @returns Void.
     */
    void kb_feature_generation_increment(int32_t model_index);

    /**
     * @brief Set the Feature Bank index to 0
     *
     * @param[in] model_index model index to run.
     * @returns Void.
     */
    void kb_reset_feature_banks(int32_t model_index);

    /**
     * @brief Set the feature vector for model index
     *
     * @param[in] model_index Model index to use.
     * @param[in] feature_vector to set the model input to
     *
     * @returns the count of features that were set
     */
    void kb_set_feature_vector(int32_t model_index, void *feature_vector);

    /**
     * @brief perform only the classification step classifier for the model
     *
     * @param[in] model_index Model index to use.
     * @returns classification result
     */
    int32_t kb_recognize_feature_vector(int32_t model_index);

    /**
     * @brief Performs the feature transform and classification step on a
     * feature vectors
     *
     * @param[in] model_index Model index to use.
     * @returns classification result
     */
    int32_t kb_generate_classification(int32_t model_index);

    // MODEL INFO APIs

    /**
     * @brief Get the model header information for model index
     *
     * @param[in] model_index Model index to use.
     * @param[in] pointer struct for the particular type of classifier (defined in kb_typdefs.h).
     * @returns 1 if successful
     *          0 if not supported for this classifier
     */
    int32_t kb_get_model_header(int32_t model_index, void *model_header);

    /**
     * @brief Gets the pointer to 16-byte UUID of model
     *
     * @param[in] model_index Model index to get UUID from
     * @return pointer to 16-byte UUID for model
     */
    const uint8_t *kb_get_model_uuid_ptr(int32_t model_index);

    /**
     * @brief Gets the length of the segment in the ring buffer.
     *
     * @param[in] model_index Model index to use.
     * @return size of the current segment in the model
     */
    int32_t kb_get_model_sg_length(int32_t model_index);

    /**
     * @brief Gets the length of segment used for the prediction
     *
     * @param[in] model_index Model index to use.
     * @return size of the current segment in the model
     */
    int32_t kb_get_segment_length(int32_t model_index);

    /**
     * @brief Gets the number of feature banks used by a model. Feature banks allow stacking of
     * features from multiple segments of data as input into the classifier.
     *
     * @param[in] model_index Model index to use.
     * @param[in] p_num_banks pointer to fill with number of feature banks used by model
     */
    int32_t sml_get_feature_bank_number(int32_t model_index);

    /**
     * @brief Gets the current index of the segment  used for generating inference, after applying cascading
     *
     * @param[in] model_index Model index to use.
     * @return current segment index (number of samples the model has received so far)
     */
    int32_t kb_get_segment_start(int32_t model_index);

    /**
     * @brief Gets the current index of the last segment
     *
     * @param[in] model_index Model index to use.
     * @return current segment index (number of samples the model has received so far)
     */
    int32_t kb_get_sg_start_index(int32_t model_index);

    /**
     * @brief Get a copy of the current segment in the buffer
     *
     * @param[in] model_index Model index to use.
     * @param[in] number_samples the number of samples to pull out of the segment
     * @param[in] index the index from the start of the segment to start copying data from
     * @param[in] p_sample_data array of size number_samples * number_of_columns (number_columns is depended on the model)
     * @returns Void.
     */
    void kb_get_segment_data(int32_t model_index, int32_t number_samples, int32_t index, int16_t *p_sample_data);

    /**
     * @brief Get number of expected columns in the input sensor
     *
     * @param[in] model_index Model index to use.
     * @returns Integer.
     */
    int32_t kb_get_num_sensor_buffers(int32_t model_index);

    /**
     * @brief Sets the feature vector
     *
     */
    int32_t kb_set_feature_vector_raw(int32_t model_index, float *feature_vector);

    /**
     * @brief Gets the raw feature vector size
     *
     */
    int32_t kb_get_feature_vector_raw_size(int32_t model_index);

    /**
     * @brief Copy the raw feature vectors to the fv_arr buffer
     *
     */
    int32_t kb_copy_feature_vector_raw(int32_t model_index, float *fv_arr);

    /**
     * @brief Get a pointer to the raw feature vector buffer
     *
     */
    float *get_feature_vector_raw_pointer(int32_t model_index);

    /**
     * @brief Gets the currently computed feature vector pointer
     *
     *
     * @param[in] model_index Model index to use.
     * @returns pointer to feature_vector_t
     */
    feature_vector_t *get_feature_vector_pointer(int32_t model_index);

    /**
     * @brief Gets the currently computed feature vector for model index
     *
     * deprecated
     *
     * @param[in] model_index Model index to use.
     * @param[in] fv_arr Feature Vector to copy into
     */
    void kb_get_feature_vector(int32_t model_index, uint8_t *fv_arr);

    /**
     * @brief Gets the data type for the feature vector array
     *
     * @param[in] model_index Model index to use.
     * @returns data type.
     */
    uint8_t get_feature_vector_type(int32_t model_index);

    /**
     * @brief Gets the size of the feature vector for a model
     *
     */
    uint16_t kb_get_feature_vector_size(int32_t model_index);

    /**
     * @brief Gets the pointer to the feature vector array for a model
     *
     * @param[in] model_index model index to use.
     * @param[in] fv_arr pointer to the array type of the feature vector
     */
    void get_feature_vector_data_pointer(int32_t model_index, void **fv_arr);

    /**
     * @brief Copy the feature vector stored inside a model to the feature vector array
     *  the feature vector can be different types, so you should check the feature_vector
     *  type first
     *
     * @param[in] model_index model index to use.
     * @param[in] fv_arr pointer to the array to copy data to
     */
    void copy_feature_vector(int32_t model_index, void *fv_arr);

    /**
     * @brief Returns a pointer to the model results for the specified model
     *
     * @param[in] model_index model index to use.
     *
     * @returns 1 if success, 0 if not applicatbale to this model type
     */
    model_results_t *kb_get_model_result_info(int32_t model_index);

    // Cascade Sliding APIs

    /**
     * @brief Run model with cascade features that slides
     *
     * This performs the same as kb_run_model, but is meant for models using cascade
     * feature generation this is different than run model as it will also compute the
     * features for each of its children models when it receives a classification,
     * Classification results will be 0 if unknown through the classification numbers
     * you have. This function returns -1 when it is waiting for more data to create
     * a classification.* returns -2 when features were generated for a feature bank
     *
     *
     * @param[in] pSample Pointer to a single time point of data across sensors (ie. ax,ay,az)
     * @param[in] nsensors (unused currently)
     * @param[in] model_index Model index to use.
     */

    int32_t kb_run_model_with_cascade_features(int16_t *pSample, int32_t nsensors, int32_t model_index);

    /**
     * @brief Run model with cascade features that does not slide.
     *
     * This performs the same as kb_run_model, but is meant for models using cascade
     * feature generation where it will only classify after all of the feature banks
     * in the cascade have been filled, then reset the number of feature banks to 0.
     * This is different from run model with cascade features, which treats the feature
     * banks as a circular buffer and constantly classifiers
     * Classification results will be 0 if unknown through the classification numbers
     * you have. This function returns -1 when it is waiting for more data to create
     * a classification.* returns -2 when features were generated for a feature bank
     *
     *
     * @param[in] pSample Pointer to a single time point of data across sensors (ie. ax,ay,az)
     * @param[in] nsensors (unused currently)
     * @param[in] model_index Model index to use.
     */

    int32_t kb_segment_with_cascade_features(int16_t *pSample, int32_t nsensors, int32_t model_index);

    // Cascade Reset APIs

    /**
     * @brief Run model with cascade features which waits until an entire new set of
     * features is created before performing classification.
     *
     * This performs the same as kb_run_model, but is meant for models using cascade
     * feature generation where it will only classify after all of the feature banks
     * in the cascade have been filled, then reset the number of feature banks to 0.
     * This is different from run model with cascade features, which treats the feature
     * banks as a circular buffer and constantly classifiers
     * Classification results will be 0 if unknown through the classification numbers
     * you have. This function returns -1 when it is waiting for more data to create
     * a classification.* returns -2 when features were generated for a feature bank
     *
     *
     * @param[in] pSample Pointer to a single time point of data across sensors (ie. ax,ay,az)
     * @param[in] nsensors (unused currently)
     * @param[in] model_index Model index to use.
     */
    int32_t kb_run_model_with_cascade_reset(int16_t *pSample, int32_t nsensors, int32_t model_index);

    /**
    * @brief This performs the same as kb_run_segment, but is meant for models using cascade
    * feature generation where the user desires classifications only after all of the feature banks
    * in the cascade have been filled.

    * After classification all of the feature banks are emptied.
    * This is different from run model, which treats the feature banks as a circular
    * buffer and constantly classifiers popping the oldest and adding the newest.
    * Classification results will be 0 if unknown through the classification numbers
    * you have. This function returns -1 when it is waiting for more data to create
    * returns -2 when features were generated for a feature bank
    * a classification
    *
    * @param[in] model_index Model index to use.
    */
    int32_t kb_run_segment_with_cascade_reset(int32_t model_index);

    // Model Profiling APIs

    /***
     * @brief Gets the Feature generation times for a given model
     *
     *
     * @param[in] model_index Model index to use.
     * @param[out] time_arr Pointer to array to use for feature times
     *
     */
    void kb_get_feature_gen_times(int32_t model_index, float *time_arr);

    /***
     * @brief Gets the Feature generation cycle counts for a given model
     *
     *
     * @param[in] model_index Model index to use.
     * @param[in] cycle_arr Pointer to array to use for feature cycles
     *
     */
    void kb_get_feature_gen_cycles(int32_t model_index, uint32_t *cycle_arr);

    /***
     * @brief Gets the time spent in classification for a given model
     *
     *
     * @param[in] model_index Model index to use.
     *
     * @returns Time spent in classifier for a model classification
     */
    float kb_get_classifier_time(int32_t model_index);

    /***
     * @brief Gets the cycle count of classification for a given model
     *
     *
     * @param[in] model_index Model index to use.
     *
     * @returns Cycle count of classifier for a model classification
     */
    uint32_t kb_get_classifier_cycles(int32_t model_index);

    /***
     * @brief Gets the profiling enabled status of the model
     *
     *
     * @param[in] model_index Model index to use.
     *
     * @returns 0 or 1, if profiling is disabled or enabled.
     */
    bool kb_is_profiling_enabled(int32_t model_index);

    // PME MODEL SPECIFIC APIs

    /**
     * @brief Set the number of stored patterns in a PME model to 0
     *
     * @param[in] model_index model index to use.
     */
    int32_t kb_flush_model(int32_t model_index);

    /**
     * @brief Get the information for a pattern from the database
     *
     * @param[in] model_index Model index to use.
     * @param[in] pattern_index Pattern index in the classifier to retrieve.
     * @param[in] pointer struct for the particular type of classifier pattern (defined in kb_typdefs.h).
     *
     * @return 1 if successful
     *         0 if not supported for this classifier, or pattern index is out of bounds
     */
    int32_t kb_get_model_pattern(int32_t model_index, int32_t pattern_index, void *pattern);

    /**
     * @brief Add the most recently classified pattern to the database of patterns.
     *
     * After receiving a classification, you can tell the model to add this classification as
     * a pattern with a specific category as well as an influence field. The larger the field
     * the larger the area this pattern can be activated in.
     *
     * @param[in] model_index Model index to use.
     * @param[in] category Category to set the for the new pattern.
     * @param[in] influence the size of the influence to set (defined in kb_typdefs.h).
     * @return 1 if successful
     *         0 if not supported for this classifier, or pattern index is out of bounds
     */
    int32_t kb_add_last_pattern_to_model(int32_t model_index, uint16_t category, uint16_t influence);

    /**
     * @brief Adds a new custom pattern to the database with a label and influence field
     *
     * @param[in] model_index Model index to use.
     * @param[in] feature_vector the new pattern that you are going to add.
     * @param[in] category Category to set the for the new pattern.
     * @param[in] influence the size of the influence to set (defined in kb_typdefs.h).
     *
     * @returns 0 if model does not support dynamic updates
     * 		   1 if model was successfully updated
     *         -1 if model cannot be updated anymore
     */
    int32_t kb_add_custom_pattern_to_model(int32_t model_index, uint8_t *feature_vector, uint16_t category, uint16_t influence);

    /***
     * @brief scores the current model based on the input category
     *
     *
     * @param[in] model_index Model index to use.
     * @param[in] category Category to set the for the new pattern.
     *
     * @returns 0 if model does not support scoring
     * 		   -1 if model cannot be scored anymore
     * 		    1 if model was successfully scored
     */
    int32_t kb_score_model(int32_t model_index, uint16_t category);

    /***
     * @brief retrain model based on scores
     *
     *
     * @param[in] model_index Model index to use.
     *
     * @returns 0 if model does not support retraining
     * 	       1 if model was successfully retrained
     */
    int32_t kb_retrain_model(int32_t model_index);

#ifdef __cplusplus
}
#endif

//clang-format on

#endif //__KB_H__
