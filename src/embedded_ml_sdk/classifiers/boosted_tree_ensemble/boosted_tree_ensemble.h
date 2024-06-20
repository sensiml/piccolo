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




#ifndef __GBTREE_ENSEMBLE_H__
#define __GBTREE_ENSEMBLE_H__

// clang-format off
#ifdef __cplusplus
extern "C"
{
#endif

#include "kbutils.h"

typedef struct boosted_tree
{
    uint8_t *node_list;
    float *leafs;
    uint8_t *threshold;
    uint8_t *features;
} boosted_tree_t;

typedef struct boosted_tree_ensemble_classifier_rows
{
    uint8_t number_of_trees;
    boosted_tree_t *boosted_tree_ensemble;
} boosted_tree_ensemble_classifier_rows_t;

uint8_t boosted_tree_ensemble_classification(boosted_tree_t *boosted_ensemble, uint8_t number_of_trees, uint8_t *feature_vector);
float boosted_tree_classification(boosted_tree_t *model, uint8_t *feature_vector);
uint8_t boosted_tree_ensemble_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results);
void boosted_tree_ensemble_init(boosted_tree_ensemble_classifier_rows_t *classifier_table, const uint8_t num_classifiers);

#ifdef __cplusplus
}
#endif
// clang-format on
#endif // __GBTREE_ENSEMBLE_H__
