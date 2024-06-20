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



#include "tree_ensemble.h"

tree_ensemble_classifier_rows_t *ClassifierTable;

// FILL_MAX_DECISION_TREE_ENSEMBLE_TMP_PARAMETERS
#ifndef MAX_DTE_CLASSIFICATIONS
#define MAX_DTE_CLASSIFICATIONS 10
#endif

uint8_t classification_counts[MAX_DTE_CLASSIFICATIONS];

uint8_t tree_classification(tree_t *model, uint8_t *feature_vector)
{
    int32_t classification = 0;
    int32_t current_node = 0;
    while (1)
    {
        if (feature_vector[model->features[current_node]] <= model->threshold[current_node])
        {
            current_node = model->left_children[current_node];
        }
        else
        {
            current_node = model->right_children[current_node];
        }
        if (model->right_children[current_node] == 0)
        {
            break;
        }
    }

    return model->features[current_node];
}

uint8_t ensemble_classification(tree_t *forest_ensemble, uint8_t *classification_counts, uint16_t number_of_trees, uint8_t number_of_classses, uint8_t *feature_vector)
{

    uint8_t y = 0;
    uint16_t max_count = 0;

    memset(classification_counts, 0, sizeof(uint8_t) * MAX_DTE_CLASSIFICATIONS);

    for (int32_t i = 0; i < number_of_trees; i++)
    {
        classification_counts[tree_classification(&forest_ensemble[i], feature_vector)]++;
    }

    max_count = classification_counts[0];

    for (int32_t i = 1; i < number_of_classses; i++)
    {
        if (classification_counts[i] > max_count)
        {
            max_count = classification_counts[i];
            y = i;
        }
    }

    return y + 1;
}

uint8_t tree_ensemble_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results)
{

    uint8_t y = 0;
    uint16_t max_count = 0;

    memset(classification_counts, 0, sizeof(uint8_t) * MAX_DTE_CLASSIFICATIONS);

    for (int32_t i = 0; i < ClassifierTable[classifier_id].number_of_trees; i++)
    {
        classification_counts[tree_classification(&ClassifierTable[classifier_id].tree_ensemble[i], (uint8_t *)feature_vector->data)]++;
    }

    max_count = classification_counts[0];
    model_results->output_tensor->data[0] = classification_counts[0];
    for (int32_t i = 1; i < ClassifierTable[classifier_id].number_of_classes; i++)
    {
        model_results->output_tensor->data[i] = (int16_t)classification_counts[i];
        if (classification_counts[i] > max_count)
        {
            max_count = classification_counts[i];

            y = i;
        }
    }

    model_results->result = (float)(y + 1);

    return y + 1;
}

void tree_ensemble_model_results_object(int32_t classifier_id, model_results_t *model_results)
{

    for (int32_t i = 0; i < ClassifierTable[classifier_id].number_of_classes; i++)
    {

        model_results->output_tensor->data[i] = classification_counts[i];
    }

    model_results->output_tensor->size = ClassifierTable[classifier_id].number_of_classes;
}

/*
 * Inititalize the PME
 */
void tree_ensemble_init(tree_ensemble_classifier_rows_t *classifier_table, const uint8_t num_classifiers)
{
    ClassifierTable = classifier_table;
}
