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




#ifndef __BONSAI_H__
#define __BONSAI_H__

// clang-format off
#ifdef __cplusplus
extern "C"
{
#endif

#include "kbutils.h"
typedef float float32_t;

typedef struct bonsai
{
    float32_t *Theta;
    float32_t *W;
    float32_t *V;
    float32_t *Z;
    float32_t *X;
    float32_t *mean;
    uint8_t depth;
    uint8_t d_l;
    uint8_t d_input;
    uint8_t d_proj;
    uint8_t num_nodes;
} bonsai_t;

typedef struct bonsai_classifier_rows
{
    bonsai_t *bonsai;
} bonsai_classifier_rows_t;

uint8_t bonsai_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t * model_results);
void bonsai_init(bonsai_classifier_rows_t *classifier_table, const uint8_t num_classifiers);
uint8_t bonsai_classification(bonsai_t *bonsai, uint8_t *feature_vector);



#ifdef __cplusplus
}
#endif

// clang-format on

#endif //__BONSAI__
