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

// FILL_SENSOR_FILTERS

/*SENSOR TRANSFORMS
Expected behavior
1. Takes one frame of sample(s) at a time and a pointer to the end of the FrameIDX array.
2. performs an operation such as magnitude and stores it into the FrameIDX array
3. Returns the number of points added to FrameIDX array

The frameData contains the data that will eventually be added to the ring buffer
*/

// FILL_SENSOR_TRANSFORMS

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

// FILL_SEGMENTERS

/*SEGMENT FILTERS

Expected Behavior
1. Returns 1 or 0. 1 if we the pipeline should continue, 0 if the pipeline should be terminated for this segment.
(note this can potentially cause issues where data is modified more than once in the case of a sliding window)
*/

// FILL_SEGMENT_FILTERS

/*SEGMENT TRANSFORMS

Expected Behavior
1. Operates only on a single segment of data. Starting at position kb_model->sg_index to a length of kb_model->sg_length.
3. Can modify data in the ring buffer, but is not allowed to add new data to the ring buffer.
(note this can potentially cause issues where data is modified more than once in the case of a sliding window)
*/

// FILL_SEGMENT_TRANSFORMS

/*FEATURE GENERATORS

Expected Behavior
1. Create a single or multiple features from a segment of data. Starting at position kb_model->sg_index to a length of kb_model->sg_length.
2. Adds a feature as a float to the feature vector.
3. Returns the number of features added to the feature vector.
*/

// FILL_FEATURE_GENERATORS


// FILL_CUSTOM_FEATURE_GENERATORS

/*FEATURE VECTOR TRANSFORM

Expected Behavior
1. Takes a pointer to the feature generator and feature params.
2. Operates on the feature vectors in place
*/

// FILL_FEATURE_VECTOR_TRANSFORMS

#ifdef __cplusplus
}
#endif
// clang-format on

#endif //_KB_ALGORITHMS_H_
