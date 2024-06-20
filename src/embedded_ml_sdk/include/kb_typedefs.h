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




#ifndef _KB_TYPEDEFS_H_
#define _KB_TYPEDEFS_H_

#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

typedef float FLOAT;
typedef unsigned short NORMTYPE;

// clang-format off

/*
Expected sensor column ordering for each model

// FILL_SENSOR_COLUMN_NAMES

*/

#ifdef __cplusplus
extern "C"
{
#endif

typedef struct
{
    int16_t *data; // Array to columns to use
    int size;  // Total number of columns
} int16_data_t;

typedef struct
{
    float *data; // Array to params to use
    int size;  // Total number of params
} float_data_t;

struct compx
{
    float real;
    float imag;
};

struct compx_int16_t
{
    int16_t real;
    int16_t imag;
};



/** @struct model_results
 *  @brief This structure is used to get the output of the classifier before the classification
 *  @var typeID: the type of data stored in the feature vector
 *  @var size: The size of the data
 *  @var data: pointer to the data array
 */
typedef struct{
    uint8_t typeID; // 0 uint8_t, 1 int8_t, 2 uint16_t, 3 int16_t, 4 uint32_t, 5 int32_t, 6 float
    uint16_t size; // number of elements in the feature vector
    void * data; // pointer to the feature vector
} feature_vector_t;




/** @struct model_results
 *  @brief This structure is used to get the output of the classifier before the classification
 *  @var model_type: the type of model that is putting the results
 *  @var result: the output of the model
 *  @var output_tensor: output array from the model that stores information about classification, such as class probabilities
 */
typedef struct model_results
{
	uint8_t model_type;
    float result;
    float_data_t *output_tensor; // the output tensor results
} model_results_t;



typedef struct
{
    uint16_t influence; //influence of a pattern
    uint16_t category;  //category of pattern
    uint8_t *vector;    // vector containing the features of a pattern
} pme_pattern_t;

typedef struct
{
    uint16_t number_patterns; //influence of a pattern
    uint16_t pattern_length;  //category of pattern
} pme_model_header_t;



#ifdef __cplusplus
}
#endif
// clang-format on

#endif //_KB_TYPEDEFS_H_
