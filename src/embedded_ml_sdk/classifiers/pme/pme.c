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




#include <stdlib.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>
#include "pme.h"
#include "kb_opt.h"

kb_classifier_row_t *KBClassifierTable;

/*
 * Allocate General Memory
 * This will allow mulitple classifiers
 * to be run at the same time
 * i.e. submit pattern for recognition
 */

/*
 * MEMORY_PME_MAX is currently 128 to match
 * the hardware as it can only return
 * up to 128 results per pattern submit
 * This can be different for software
 */

static pme_results memory_allocated[MEMORY_PME_MAX];
static int32_t memory_used = 0;
/* Static definitions */
static uint8_t number_of_classifiers_used = 0;
static pme_results *pointer;
typedef void (*func)(uint8_t classifier_id, uint8_t *number_of_results, void *results);
static func task[4];
static uint8_t pme_vector_dist[PME_COMMON_MAX_VECTOR_LENGTH];

/* Absolute Value Function */

/*
 * Function to delete a node in a Doubly Linked List.
 * headReference --> pointer to head node pointer.
 * nodeToDelete  -->  pointer to node to be deleted.
 */
void delete_node(pme_results **head_reference, pme_results *node_to_delete)
{
    /* Base Case */
    if (*head_reference == NULL || node_to_delete == NULL)
    {
        return;
    }

    /* If node to be deleted is head node */
    if (*head_reference == node_to_delete)
    {
        *head_reference = node_to_delete->next;
    }

    /* Change next only if node to be deleted is NOT the last node */
    if (node_to_delete->next != NULL)
    {
        node_to_delete->next->prev = node_to_delete->prev;
    }

    /* Change prev only if node to be deleted is NOT the first node */
    if (node_to_delete->prev != NULL)
    {
        node_to_delete->prev->next = node_to_delete->next;
    }

    return;
}

/*
 * Compare and Sort the Linked List
 * By Distance (Comparator function for ListToSort)
 */
int32_t sort_by_smallest_distance(void *a, void *b)
{
    pme_results *left = ((struct pme_results *)a);
    pme_results *right = ((struct pme_results *)b);

    return (left->distance - right->distance);
}

/*
 * This is a merge sort algorithm to
 * sort a Linked List
 * it runs in nlog(n) instructions
 */
pme_results *list_to_sort(pme_results *list, bool is_circular, bool is_double)
{
    pme_results *p, *q, *e, *tail, *old_head;
    int32_t in_size, number_of_merges, p_size, q_size, i;
    /*
     * Special case: if `list' was passed in as NULL, return
     * NULL immediately.
     */
    if (!list)
    {
        return NULL;
    }

    in_size = 1;
    while (1)
    {
        p = list;
        /* old_head is for Circular Linked List only */
        old_head = list;
        list = NULL;
        tail = NULL;
        /* number of merges to do in each pass */
        number_of_merges = 0;
        while (p)
        {
            /* p exists, a merge needs to be done */
            number_of_merges++;
            /* go in_size places from p */
            q = p;
            p_size = 0;
            for (i = 0; i < in_size; i++)
            {
                p_size++;
                if (is_circular)
                {
                    q = (q->next == old_head ? NULL : q->next);
                }
                else
                {
                    q = q->next;
                }
                if (!q)
                {
                    break;
                }
            }

            /* if q hasn't fallen off end, we have two lists to merge */
            q_size = in_size;

            /* now we have two lists to merge */
            while (p_size > 0 || (q_size > 0 && q))
            {
                /* decide whether next element of merge comes from p or q */
                if (p_size == 0)
                {
                    /* p is empty; e must come from q */
                    e = q;
                    q = q->next;
                    q_size--;
                    if (is_circular && q == old_head)
                    {
                        q = NULL;
                    }
                }
                else if (q_size == 0 || !q)
                {
                    /* q is empty; e must come from p */
                    e = p;
                    p = p->next;
                    p_size--;
                    if (is_circular && p == old_head)
                    {
                        p = NULL;
                    }
                }
                /* Compare p and q by distance */
                else if (sort_by_smallest_distance(p, q) <= 0)
                {
                    /*
                     * First element of p is lower (or same);
                     * e must come from p.
                     */
                    e = p;
                    p = p->next;
                    p_size--;
                    if (is_circular && p == old_head)
                    {
                        p = NULL;
                    }
                }
                else
                {
                    /* first element of q is lower; e must come from q */
                    e = q;
                    q = q->next;
                    q_size--;
                    if (is_circular && q == old_head)
                    {
                        q = NULL;
                    }
                }
                /* add the next element to the merged list */
                if (tail)
                {
                    tail->next = e;
                }
                else
                {
                    list = e;
                }
                if (is_double)
                {
                    /* maintain reverse pointers in a doubly linked list */
                    e->prev = tail;
                }
                tail = e;
            }
            /* now p has moved in_size places along, and q has too */
            p = q;
        }

        if (is_circular)
        {
            tail->next = list;
            if (is_double)
            {
                list->prev = tail;
            }
        }
        else
        {
            tail->next = NULL;
        }
        /*
         * If we have done only one merge, we're finished.
         * allow for numberOfMerges to equal 0 for an empty list
         */
        if (number_of_merges <= 1)
        {
            return list;
        }
        /* otherwise repeat, merging lists twice the size */
        in_size *= 2;
    }
}

/*
 * Sort the Linked List by Distance
 */
pme_results *sort_results_by_distance(uint8_t classifier_index)
{
    int32_t i;

    for (i = 0; i < MEMORY_PME_MAX; ++i)
    {
        if (memory_allocated[i].memory_pointer == classifier_index)
        {
            pointer = &memory_allocated[i];
            break;
        }
    }

    pointer = list_to_sort(pointer, true, true);

    return pointer;
}

/*
 * Allocate the memory needed for
 * this particular classifier
 */
pme_results *allocate_memory(uint8_t classifier_index)
{
    int32_t i;
    bool pointer_start = false;
    /*
     * Note: memoryUsed = 0 means everytime
     * pme_submit_pattern() is called
     * the memory of the prior classifier
     * is overwritten.  Design issue,
     * this does not have to be that way in
     * software.  Multiple classifiers could
     * hold their results for retrieval
     */
    memory_used = 0;

    if (memory_used < MEMORY_PME_MAX)
    {
        pointer_start = true;
    }

    if (pointer_start)
    {
        for (i = 0; i < KBClassifierTable[classifier_index].num_patterns; ++i)
        {
            memory_allocated[memory_used + i].next = &memory_allocated[memory_used + i + 1];
            memory_allocated[memory_used + i].memory_pointer = classifier_index;
            if (i == 0)
            {
                memory_allocated[memory_used + i].prev = NULL;
            }
            else
            {
                memory_allocated[memory_used + i].prev = &memory_allocated[memory_used + i - 1];
            }
        }
        memory_allocated[memory_used].memory_pointer = classifier_index;
        memory_allocated[memory_used + i - 1].next = &memory_allocated[memory_used];
        memory_allocated[memory_used].prev = &memory_allocated[memory_used + i - 1];
        pointer = &memory_allocated[memory_used];
        memory_used += KBClassifierTable[classifier_index].num_patterns;
    }
    return pointer;
}

/*
 * Inititalize the PME
 */
int8_t pme_init(kb_classifier_row_t *classifier_table, uint8_t num_classifiers)
{
    KBClassifierTable = classifier_table;
    number_of_classifiers_used = num_classifiers;
    return 0;
}

/*
 * Inititalize the PME in simple mode
 */
int8_t pme_simple_init(kb_classifier_row_t *classifier_table, uint8_t number_of_classifiers)
{
    KBClassifierTable = classifier_table;
    number_of_classifiers_used = number_of_classifiers;
    return 0;
}

/*
 * Find the Classifier in the K-Pack
 */
uint8_t find_classifier_index(uint8_t classifier_id)
{
    uint8_t i;
    uint16_t classifier_index = 0;
    /* Find the proper Classifier and configuration */
    for (i = 0; i < number_of_classifiers_used; ++i)
    {
        if (classifier_id == KBClassifierTable[i].classifier_id)
        {
            /*
             * Found the Classifier
             * Now allocate memory for
             * retrival of results
             */
            classifier_index = i;
            break;
        }
    }
    return classifier_index;
}

/*
 * Add a feature vector as a new pattern
 */
int32_t pme_add_new_pattern(int32_t classifier_id, uint8_t *feature_vector, uint16_t category, uint16_t influence)
{
    uint16_t classifier_index = 0;
    int16_t new_pattern_index;
    classifier_index = find_classifier_index(classifier_id);

    if (KBClassifierTable[classifier_index].num_patterns >= KBClassifierTable[classifier_index].max_patterns)
    {
        return -1;
    }
    new_pattern_index = KBClassifierTable[classifier_index].num_patterns;

    for (int32_t i = 0; i < KBClassifierTable[classifier_index].pattern_size; i++)
    {
        KBClassifierTable[classifier_index].stored_patterns[new_pattern_index].vector[i] = feature_vector[i];
    }

    KBClassifierTable[classifier_index].stored_attribs[new_pattern_index].influence = influence;
    KBClassifierTable[classifier_index].stored_attribs[new_pattern_index].category = category;
    KBClassifierTable[classifier_index].num_patterns += 1;

    return 1;
}

/*
 * Add a feature vector as a new pattern
 */
int32_t pme_learn_pattern(int32_t classifier_id, uint8_t *pattern, uint16_t category, uint16_t influence)
{
    // printf("Learning Vector\n");
    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;
    int16_t new_influence;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    pme_result_dist_cat_id_t result;

    if (category <= 0 || category > classifier_row->num_classes)
    {
        printf("Invalid category for this model");
        return -1;
    }
    // printf("result %d", result.category);
    result.category = 0;

    pme_simple_submit_pattern_set_result(classifier_id, pattern, &result);

    if (result.category == USHRT_MAX)
    {
        // printf("Unknown classificaiton");
        pme_add_new_pattern(classifier_id, pattern, category, influence);
    }
    else if (result.category != category)
    {
        // printf("Staring add of new pattern\n");
        reduce_influence_fields(classifier_id);
        // printf("Reduced Influence FIeld\n");
        new_influence = ((result.distance / 2) < influence) ? (result.distance / 2) : influence;
        // printf("New Influence %d\n", new_influence);
        pme_add_new_pattern(classifier_id, pattern, category, influence);
        // printf("Pattern Adden\n");
    }
    else if (result.category == category)
    {
        return 0;
    }

    return 1;
}

void pme_score_pattern(int32_t classifier_id, uint8_t *pattern, uint16_t category)
{

    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    pme_result_dist_cat_id_t result;

    if (category <= 0 || category > classifier_row->num_classes)
    {
        printf("Invalid category for this model");
        return;
    }

    pme_simple_submit_pattern_set_result(classifier_id, pattern, &result);

    if (result.category != category)
    {
        classifier_row->stored_scores[result.pattern_id].error--;
    }
    else if (result.category == category)
    {
        classifier_row->stored_scores[result.pattern_id].error++;
    }
    else if (result.category == USHRT_MAX)
    {
        printf("Unknown classificaiton");
        return;
    }

    classifier_row->stored_scores[result.pattern_id].class_vector[category - 1]++;
    printf("r: %d cat: %d pid: %d\n", result.category, category, result.pattern_id);
}

void pme_rebalance_patterns(int32_t classifier_id)
{

    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;
    uint8_t max_cat;
    uint8_t max_class_count = 0;
    int32_t i, j;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    for (i = 0; i < classifier_row->num_patterns; i++)
    {
        printf("Neuron %d error %d\n", i, classifier_row->stored_scores[i].error);
        if (classifier_row->stored_scores[i].error < 0)
        {
            max_cat = 1;
            for (j = 0; j < classifier_row->num_classes; j++)
            {
                if (classifier_row->stored_scores[i].class_vector[j] > max_class_count)
                {
                    max_class_count = classifier_row->stored_scores[i].class_vector[j];
                    max_cat = j + 1;
                }
            }
            printf("Updating Neuron %d to cat %d\n", i, max_cat);
            classifier_row->stored_attribs[i].category = max_cat;
        }
    }

    for (i = 0; i < classifier_row->num_patterns; i++)
    {
        for (j = 0; j < classifier_row->num_classes; j++)
        {
            classifier_row->stored_scores[i].class_vector[j] = 0;
        }
        classifier_row->stored_scores[i].error = 0;
    }
}

void pme_print_model_scores(int32_t classifier_id)
{
    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;
    int32_t i, j;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    for (i = 0; i < classifier_row->num_patterns; i++)
    {
        printf("{\"ID\":%d,\"ERR\":%d", i, classifier_row->stored_scores[i].error);
        for (j = 0; j < classifier_row->num_classes; j++)
        {
            printf(",\"%d\":%d", j + 1, classifier_row->stored_scores[i].class_vector[j]);
        }
        printf("}\n");
    }
}

void pme_return_pattern(int32_t classifier_id, int32_t pattern_index, pme_pattern_t *pattern)
{
    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    pattern->category = classifier_row->stored_attribs[pattern_index].category;
    pattern->influence = classifier_row->stored_attribs[pattern_index].influence;
    pattern->vector = classifier_row->stored_patterns[pattern_index].vector;
}

void pme_flush_model(int32_t classifier_id)
{
    uint16_t classifier_index = 0;

    classifier_index = find_classifier_index(classifier_id);
    KBClassifierTable[classifier_index].num_patterns = 0;
    pointer = NULL;

    for (int32_t i = 0; i < MEMORY_PME_MAX; ++i)
    {
        if (memory_allocated[i].memory_pointer == classifier_index)
        {
            memory_allocated[i].memory_pointer = -1;
            memory_allocated[i].category = 0;
        }
    }
}

int32_t pme_get_number_patterns(int32_t classifier_id)
{
    uint16_t classifier_index = 0;

    classifier_index = find_classifier_index(classifier_id);
    return KBClassifierTable[classifier_index].num_patterns;
}

/*
 * Submit a vector for recognition
 */
int32_t pme_submit_pattern(uint8_t classifier_id, uint8_t *pattern, qm_pme_network_status_t *result)
{
    uint16_t i;
    uint16_t temp_category;
    uint16_t classifier_index = 0;
    uint32_t temp_index;
    uint32_t tmp_distance_uint32;
    uint8_t tmp_distance_uint8;

    /* Find the proper Classifier and configuration */
    classifier_index = find_classifier_index(classifier_id);
    /*
     * Found the Classifier
     * Now allocate memory for
     * retrieved Classifier
     */
    pointer = allocate_memory(classifier_index);
    /*
     * Submit pattern and calculate the
     * Distances only and store in a
     * Distance array (non sorted)
     */
    temp_category = USHRT_MAX;
    *result = QM_PME_NEGATIVE_RESULT;

    for (i = 0; i < (KBClassifierTable[classifier_index].num_patterns); ++i)
    {

        pointer->category = KBClassifierTable[classifier_index].stored_attribs[i].category;
        pointer->active_influence_field = KBClassifierTable[classifier_index].stored_attribs[i].influence;
        pointer->pattern_id = i;
        pointer->distance = 0;

        if (KBClassifierTable[classifier_index].norm_mode == QM_PME_L1_DISTANCE)
        {
            l1_distance(KBClassifierTable[classifier_index].stored_patterns[i].vector, pattern, &tmp_distance_uint32, KBClassifierTable[classifier_index].pattern_size);
            pointer->distance = (uint16_t)tmp_distance_uint32;
        }
        else if ((KBClassifierTable[classifier_index].norm_mode == QM_PME_LSUP_DISTANCE))
        {
            tmp_distance_uint8 = 0u;
            lsup_distance(KBClassifierTable[classifier_index].stored_patterns[i].vector, pattern, pme_vector_dist, &tmp_distance_uint8, KBClassifierTable[classifier_index].pattern_size);
            pointer->distance = (uint16_t)tmp_distance_uint8;
        }
        else if ((KBClassifierTable[classifier_index].norm_mode == QM_PME_DTW_DISTANCE))
        {
            tmp_distance_uint8 = 0u;
            compute_distance_matrix(pattern,
                                    KBClassifierTable[classifier_index].stored_patterns[i].vector,
                                    KBClassifierTable[classifier_index].pattern_size / KBClassifierTable[classifier_index].num_channels,
                                    KBClassifierTable[classifier_index].pattern_size / KBClassifierTable[classifier_index].num_channels,
                                    KBClassifierTable[classifier_index].num_channels);
            pointer->distance = (uint16_t)compute_warping_distance(KBClassifierTable[classifier_index].pattern_size / KBClassifierTable[classifier_index].num_channels,
                                                                   KBClassifierTable[classifier_index].pattern_size / KBClassifierTable[classifier_index].num_channels);
        }

        if (pointer->distance < (int32_t)pointer->active_influence_field)
        {
            if ((temp_category != USHRT_MAX) && (temp_category != (int32_t)pointer->category))
            {
                temp_category = (int32_t)pointer->category;
                *result = QM_PME_UNCERTAIN_RESULT;
            }
            else if (temp_category == USHRT_MAX)
            {
                temp_category = (int32_t)pointer->category;
                *result = QM_PME_POSITIVE_RESULT;
            }
        }
        ++pointer;
    }
    return 0;
}

/*
 * TODO:
 * Return Unique Categories on in RBF
 */
void radial_bias_function_unique_category(uint8_t classifier_index, uint8_t *number_of_results, void *results) {}

/*
 * TODO:
 * Return a category by a weighting function
 */
void distance_by_weight(uint8_t classifier_index, uint8_t *number_of_results, void *results) {}

/*
 * RBF requested
 */
void radial_bias_function(uint8_t classifier_index, uint8_t *number_of_results, void *results)
{
    uint8_t i;
    uint8_t max = *number_of_results;
    uint8_t number_of_hits = 0;
    pme_result_dist_cat_id_t *return_struct = ((struct pme_result_dist_cat_id_t *)results);

    for (i = 0; i < KBClassifierTable[classifier_index].num_patterns; ++i)
    {
        // printf("rbf: index %d id %d distance %d influence %d\n", i, pointer->pattern_id, pointer->distance, pointer->active_influence_field);
        if (pointer->distance < (int32_t)pointer->active_influence_field)
        {
            if (number_of_hits < max)
            {
                return_struct[number_of_hits].distance = pointer->distance;
                return_struct[number_of_hits].category = (int32_t)pointer->category;
                return_struct[number_of_hits].pattern_id = (int32_t)pointer->pattern_id;
                ++number_of_hits;
                *number_of_results = number_of_hits;
            }
            else
            {
                *number_of_results = max;
                pointer = pointer->next;
                break;
            }
        }
        pointer = pointer->next;
    }
}

/*
 * KNN requested
 */
void k__nearest_neighbor(uint8_t classifier_index, uint8_t *number_of_results, void *results)
{
    uint16_t i;
    uint8_t max = *number_of_results;

    pme_result_dist_cat_id_t *return_struct = (struct pme_result_dist_cat_id_t *)results;

    for (i = 0; i < max; ++i)
    {
        return_struct[i].distance = pointer->distance;
        return_struct[i].category = (int32_t)pointer->category;
        return_struct[i].pattern_id = (int32_t)pointer->pattern_id;
        // pointer->memory_pointer = USHRT_MAX;
        // delete_node(&pointer, pointer);
        pointer = pointer->next;
    }

    /* TODO: if max > num paterns in model could cause an issue
        if (max > KBClassifierTable[classifier_index].num_patterns)
    {
        max = KBClassifierTable[classifier_index].num_patterns;
    }
    */
}

void reduce_influence_fields(int32_t classifier_id)
{
    int32_t i;
    int16_t classifier_index = find_classifier_index(classifier_id);

    for (i = 0; i < KBClassifierTable[classifier_index].num_patterns; ++i)
    {
        // printf("index %d id %d distance %d influence %d\n", i, pointer->pattern_id, pointer->distance, pointer->active_influence_field);
        if (pointer->distance < (int32_t)pointer->active_influence_field)
        {
            KBClassifierTable[classifier_index].stored_attribs[pointer->pattern_id].influence = pointer->distance;
        }
        pointer = pointer->next;
    }
}

/*
 * Return the results requested for
 * in the struct passed via void pointer
 */
void pme_retrieve_results(uint8_t classifier_id, qm_pme_classification_mode_t mode, uint8_t *number_of_results, void *results)
{
    uint8_t option;

    uint8_t classifier_index = 0;
    pme_results *pointer_cache;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);

    pointer_cache = sort_results_by_distance(classifier_index);

    option = mode;
    task[0] = radial_bias_function;
    task[1] = k__nearest_neighbor;
    task[2] = radial_bias_function_unique_category;
    task[3] = distance_by_weight;
    (*task[option])(classifier_index, number_of_results, results);

    pointer = pointer_cache;
}

/*
 * Submit a pattern and get a result
 * This will first try to get a match
 * by using RBF, if no match is found then
 * KNN will be used to find the nearest match
 */
int32_t pme_simple_submit_pattern(uint8_t classifier_id, feature_vector_t *pattern, model_results_t *model_results)
{
    uint8_t error = 0;
    uint8_t number_of_results;
    qm_pme_network_status_t network_status = QM_PME_NEGATIVE_RESULT;
    pme_result_dist_cat_id_t result;
    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;
    pme_results *pointer_cache;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    number_of_results = 1;
    error = pme_submit_pattern(classifier_id, (uint8_t *)pattern->data, &network_status);
    if ((network_status == QM_PME_POSITIVE_RESULT) || (network_status == QM_PME_UNCERTAIN_RESULT) || (network_status == QM_PME_NEGATIVE_RESULT && classifier_row->classifier_mode == QM_PME_KNN_CLASSIFICATION))
    {
        // If we're using classifier as KNN, then this will set the mode properly and give us a result.
        pme_retrieve_results(classifier_id, classifier_row->classifier_mode, &number_of_results, &result);
        // pme_retrieve_results(classifier_id, PME_RR_SORT_BY_DIST_WITH_AIF, &number_of_results, &result);
        model_results->output_tensor->data[0] = (float)result.pattern_id;
        model_results->output_tensor->data[1] = (float)result.category;
        model_results->output_tensor->data[2] = (float)classifier_row->stored_attribs[result.pattern_id].influence;
        model_results->output_tensor->data[3] = (float)result.distance;
    }
    else if (network_status == QM_PME_NEGATIVE_RESULT && classifier_row->classifier_mode == QM_PME_RBF_CLASSIFICATION)
    {
        result.category = USHRT_MAX;
        pointer_cache = sort_results_by_distance(classifier_index);
        model_results->output_tensor->data[0] = (float)pointer_cache->pattern_id;
        model_results->output_tensor->data[1] = (float)pointer_cache->category;
        model_results->output_tensor->data[2] = (float)classifier_row->stored_attribs[pointer_cache->pattern_id].influence;
        model_results->output_tensor->data[3] = (float)pointer_cache->distance;
    }

    if (result.category == USHRT_MAX)
    {
        model_results->result = 0.0f;
    }
    else
    {
        model_results->result = (float)result.category;
    }

    return result.category;
}

/*
 * Submit a pattern and set result set
 * This will first try to get a match
 * by using RBF, if no match is found then
 * KNN will be used to find the nearest match
 */
void pme_simple_submit_pattern_set_result(uint8_t classifier_id, uint8_t *pattern, pme_result_dist_cat_id_t *result)
{
    uint8_t error = 0;
    uint8_t number_of_results;
    qm_pme_network_status_t network_status = QM_PME_NEGATIVE_RESULT;
    kb_classifier_row_t *classifier_row;
    uint16_t classifier_index = 0;

    /* Find the Classifier */
    classifier_index = find_classifier_index(classifier_id);
    classifier_row = &KBClassifierTable[classifier_index];

    number_of_results = 1;
    error = pme_submit_pattern(classifier_id, pattern, &network_status);
    if ((network_status == QM_PME_POSITIVE_RESULT) || (network_status == QM_PME_UNCERTAIN_RESULT))
    {
        // If we're using classifier as KNN, then this will set the mode properly and give us a result.
        pme_retrieve_results(classifier_id, classifier_row->classifier_mode, &number_of_results, result);
        // pme_retrieve_results(classifier_id, PME_RR_SORT_BY_DIST_WITH_AIF, &number_of_results, &result);
    }
    else if (network_status == QM_PME_NEGATIVE_RESULT && classifier_row->classifier_mode == QM_PME_KNN_CLASSIFICATION)
    {
        // Network status = QM_PME_NEGATIVE_RESULT, use KNN to give a result anyway.
        pme_retrieve_results(classifier_id, classifier_row->classifier_mode, &number_of_results, result);
        // pme_retrieve_results(classifier_id, PME_RR_SORT_BY_DIST_NO_AIF, &number_of_results, &result);
    }
    else if (network_status == QM_PME_NEGATIVE_RESULT && classifier_row->classifier_mode == QM_PME_RBF_CLASSIFICATION)
    {
        // NOTE: because retrive results is not called the pointer is not set correctly, so calling reduce influence field
        //  fails, shouldn't be called for unknown category however.
        result->category = USHRT_MAX;
    }
}
