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




#ifndef _KB_COMMON_H_
#define _KB_COMMON_H_
#include "kb_defines.h"
#include "rb.h"

// clang-format off
#ifdef __cplusplus
extern "C" {
#endif


// FILL_SEGMENTER_TYPEDEF
#ifndef SEG_PARAMS
#define SEG_PARAMS SEG_PARAMS
typedef struct{
    int32_t window_size;
    int32_t delta;
} seg_params;
#endif //SEG_PARAMS

typedef struct
{
  /*@{*/
  ring_buffer_t *data; /**< internal index to head of ring - oldest data */
  int32_t size;
  /*@}*/
} data_buffers_t;

typedef struct{
        bool enabled;
        float *feature_gen_times;
        uint32_t *feature_gen_cycles;
        float classifier_time;
        uint32_t classifier_cycles;
} kb_profile_t;

typedef struct feature_bank
{
    uint16_t bank_size; // number of features in a bank
    bool filled_flag;   // Flag to set if the feature bank has been filled at least once
    uint8_t num_banks;  // number of feature banks
    float *pFeatures;   // pointer to the feature vector array
} feature_bank_t;

typedef int32_t (*model_feature_gen_f)(void *kb_model, int32_t *);
typedef int32_t (*model_data_streaming_f)(void *kb_model, int16_t *);
typedef int32_t (*model_data_segmentation_f)(void *kb_model, int32_t model_index);
typedef int32_t (*model_recognize_vector_f)(void *kb_model);
typedef int32_t (*model_feature_transform_f)(void *kb_model);


 
// kb_model_t is the basic data structure for our kb pipeline. It contains all of the information
// Necessary to run a pipeline. It can be considered a state machine that is passed around to different
// functions inside of the pipeline which act on it depending on its current state.

typedef struct{
    // MODEL INFO
    uint8_t *model_uuid; //Contains the 16-bytes used to identify the model in the cloud.           
    uint8_t parent;              // index of the parent model
    uint16_t streaming_filter_length;          // the amount of filtering performed on the input data   
    uint8_t classifier_type; // This is the classifier type that the model uses
    uint8_t classifier_id;   // context to use when submitting this models feature vector           
    // MODEL STATE
    int32_t total_classifications; //Contains the total classifications run on system per power cycle.       
    int32_t sg_length;           // This is the length of an identified segment of data.
    int32_t sg_index;            // This is the position of the start of the index in the ring buffer
    int32_t last_read_idx;       // This is the index of the last read value from the rb
    uint8_t feature_bank_index;   // index of the head of the feature bank      
    // MODEL STORAGE 
    int16_t *input_data; // pointer to array containing the most recently added data sample (placed here then into the ring buffer)
    data_buffers_t *psdata_buffer;  // Pointer to the streaming data buffer    
    data_buffers_t *pdata_buffer;   // pointer to the ring buffer    
    seg_params *psegParams;  // Pointer to the segmenter data structure
    feature_bank_t *pfeature_bank; // pointer to feature bank
    feature_vector_t *pfeature_vector;  // pointer to the current feature vector
    model_results_t *pmodel_results; // pointer to model results                                                 
    // MODEL FUNCTIONS
    model_data_streaming_f data_streaming; // Pointer to the streaming data function
    model_data_segmentation_f data_segmentation; // Pointer to the data segmentation function
    model_feature_gen_f feature_gen; // Pointer to the feature generator function    
    model_feature_transform_f feature_transform; // Pointer to the feature transform function
    model_recognize_vector_f recognize_vector; // Pointer to the feature vector classifier function
    kb_profile_t m_profile; //model profiler                        
} kb_model_t;


#ifdef __cplusplus
}
#endif

// clang-format on

#endif //_KB_COMMON_H_
