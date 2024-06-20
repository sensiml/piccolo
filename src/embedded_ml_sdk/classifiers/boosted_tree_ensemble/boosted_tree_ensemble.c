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




#include "boosted_tree_ensemble.h"

boosted_tree_ensemble_classifier_rows_t *GBTClassifierTable;

float boosted_tree_classification(boosted_tree_t *model, uint8_t *feature_vector)
{

    int32_t next_node = 0;
    uint8_t current_node = 0;
    while (1)
    {
        next_node = model->node_list[current_node];
        if (feature_vector[model->features[current_node]] > model->threshold[current_node])
        {
            next_node += 1;
        }

        if (model->node_list[next_node] == 0)
        {
            return model->leafs[model->features[next_node]];
        }
        current_node = next_node;
    }
}

uint8_t boosted_tree_ensemble_classification(boosted_tree_t *forest_ensemble, uint8_t number_of_trees, uint8_t *feature_vector)
{

    uint8_t y = 0;
    uint8_t max_count = 0;
    float margin = 0.f;

    for (int32_t i = 0; i < number_of_trees; i++)
    {
        margin += boosted_tree_classification(&forest_ensemble[i], feature_vector);
    }

    return margin <= 0.f ? 1 : 2;
}

uint8_t boosted_tree_ensemble_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results)
{

    uint8_t y = 0;
    uint8_t max_count = 0;
    float margin = 0.f;

    for (int32_t i = 0; i < GBTClassifierTable[classifier_id].number_of_trees; i++)
    {
        margin += boosted_tree_classification(&GBTClassifierTable[classifier_id].boosted_tree_ensemble[i], (uint8_t *)feature_vector->data);
    }

    model_results->result = margin <= 0.f ? 1.0 : 2.0;

    return margin <= 0.f ? 1 : 2;
}

/*
 * Inititalize the PME
 */
void boosted_tree_ensemble_init(boosted_tree_ensemble_classifier_rows_t *classifier_table, const uint8_t num_classifiers)
{
    GBTClassifierTable = classifier_table;
}
