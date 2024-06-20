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




#ifndef __TREE_ENSEMBLE_H__
#define __TREE_ENSEMBLE_H__

// clang-format off
#ifdef __cplusplus
extern "C"
{
#endif

#include "kbutils.h"

typedef struct tree
{
    uint16_t *left_children;
    uint16_t *right_children;
    uint8_t *threshold;
    uint16_t *features;
} tree_t;

typedef struct tree_ensemble_classifier_rows
{
    uint8_t number_of_classes;
    uint16_t number_of_trees;
    tree_t *tree_ensemble;
} tree_ensemble_classifier_rows_t;



uint8_t ensemble_classification(tree_t *forest_ensemble, uint8_t *classification_counts, uint16_t number_of_trees, uint8_t number_of_classses, uint8_t *feature_vector);
uint8_t tree_classification(tree_t *model, uint8_t *feature_vector);
uint8_t tree_ensemble_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t * model_results);
void tree_ensemble_init(tree_ensemble_classifier_rows_t *classifier_table, const uint8_t num_classifiers);
void tree_ensemble_model_results_object(int32_t classifier_id, model_results_t *model_results);

#ifdef __cplusplus
}
#endif

// clang-format on

#endif // __TREE_ENSEMBLE_H__
