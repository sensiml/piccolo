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




#ifndef PME_H_
#define PME_H_

#include "kb_typedefs.h"

#ifdef __cplusplus
extern "C"
{
#endif

// clang-format off


// FILL_PME_MAX_TMP_PARAMETERS

#ifndef PME_MAX_CLASSIFIERS
#define PME_MAX_CLASSIFIERS 128
#endif

#ifndef PME_COMMON_MAX_VECTOR_LENGTH
#define PME_COMMON_MAX_VECTOR_LENGTH 2048
#endif

#ifndef QM_PME_MAX_CATEGORY_LENGTH
#define QM_PME_MAX_CATEGORY_LENGTH 100
#endif

#ifndef MEMORY_PME_MAX
#define MEMORY_PME_MAX 2048
#endif



/*
 * Types of data structures to store
 * in general memory depending on
 * configuration of classifier
 */
typedef struct pme_results
{

    uint16_t memory_pointer;
    uint16_t distance;
    uint16_t category;
    uint16_t pattern_id;
    uint16_t active_influence_field;
    struct pme_results *next;
    struct pme_results *prev;

} pme_results;


/////////////////////////////////////
//
// Supporting Struct for KNN and RBF mode


typedef struct pme_result_dist_cat_id_t
{

	uint16_t distance;

	uint16_t category;

	uint16_t pattern_id;

} pme_result_dist_cat_id_t;

/**
 * Classification Mode
 *
 * Radial Basis Function  (RBF): Matches test vectors that are within any of the
 *                               Active Influence Fields of the vectors in the
 *                               neuron vector database.
 * Known Nearest Neighbor (KNN): Matches test vectors with their closest match
 *                               within the neuron vector database.
 */
typedef enum
{
	/** Radial Basis Function */
	QM_PME_RBF_CLASSIFICATION = 0,
	/** Known Nearest Neighbor */
	QM_PME_KNN_CLASSIFICATION = 1
} qm_pme_classification_mode_t;

/**
 * Distance Mode for Radial Basis Function (RBF) classification
 */
typedef enum
{
	/** L1 distance (Manhattan distance). */
	QM_PME_L1_DISTANCE = 0,
	/** LSUP distance */
	QM_PME_LSUP_DISTANCE = 1,
	/** DTW Distance */
	QM_PME_DTW_DISTANCE = 2
} qm_pme_distance_mode_t;

/**
 * Network status after loading loading a test vector.
 */
typedef enum
{
	/** None of the neurons have identified the broadcasted vector. */
	QM_PME_NEGATIVE_RESULT = 0,
	/**
 * One or more neurons with the same category have identified the
 * broadcasted vector.
 */
	QM_PME_POSITIVE_RESULT,
	/**
 * Multiple neurons with different categories have identified the
 * broadcasted vector indicating an uncertain result.
 */
	QM_PME_UNCERTAIN_RESULT,
} qm_pme_network_status_t;

/**
 * Neuron Attributes Data Structure
 */
typedef struct qm_pme_neuron_attribute
{
	uint16_t influence; /**< Neuron Active Influence Field */
	uint16_t category;  /**< Neuron Category */
} qm_pme_neuron_attribute_t;

/**
 * Neuron Vector Data Structure.
 *
 * *NB This is only used for the register interface
 * which is the slowest method of loading the database.
 */
typedef struct qm_pme_neuron_vector
{
	uint8_t vector[PME_COMMON_MAX_VECTOR_LENGTH];
} qm_pme_neuron_vector_t;

typedef struct qm_pme_stored_score
{
	int16_t error;									  /**< Error Rate */
	uint8_t class_vector[QM_PME_MAX_CATEGORY_LENGTH]; /**< Confusion Matrix for a pattern */
} qm_pme_stored_score_t;

typedef struct kb_classifier_row
{
	uint8_t classifier_id;
	uint16_t num_patterns;
	uint16_t pattern_size;
	uint16_t max_patterns;
	uint8_t num_classes;
	uint8_t num_channels;
	qm_pme_classification_mode_t classifier_mode;
	qm_pme_distance_mode_t norm_mode;
	qm_pme_neuron_vector_t *stored_patterns;
	qm_pme_neuron_attribute_t *stored_attribs;
	qm_pme_stored_score_t *stored_scores;
} kb_classifier_row_t;

/* There are multiple modes of returning results.
 *
 * TODO: Add more documentation here
 *
 * PME_RR_SORT_BY_DIST_WITH_AIF
 * PME_RR_SORT_BY_DIST_NO_AIF
 *
*/
typedef enum
{
	PME_RR_UNKNOWN = -1,
	PME_RR_SORT_BY_DIST_WITH_AIF,
	PME_RR_SORT_BY_DIST_NO_AIF,
	PME_RR_END
} PME_RESULT_MANAGEMENT;

/**
 * Initialize the PME middle layer with information on all the classifiers. We
 * will populate the KBClassifierTable and KBResourceTable structures.
 *
 * @param[in]  kb_classifier_row_t *classifier_table Pointer to table with
 *                                                        all classifier info
 *
 * @param[in]  uint8_t             num_classifiers   The number of classifiers
 *                                                        in classifier_table
 *
 * @return
 *             - TODO: return ?
 */
int8_t pme_init(kb_classifier_row_t *classifier_table,  uint8_t num_classifiers);

/*
 * Function to submit a test pattern to the PME and get the general outcome (positive,
 * negative, or uncertain)
 *
 * @param[in]  uint8_t           classifier_id         The ID of the classifier.
 *                                                          It is the value you set in the
 *                                                          classifier_id field of the
 *                                                          kb_classifier_row_t table
 *                                                          you defined.
 *
 * @param[in]  uint8_t           *pattern              Pointer to test pattern
 *
 * @param[in] qm_pme_network_status_t * network_status Pointer to place to store the
 *                                                          general classification outcome
 *
 * @return
 *             - TODO: return ?
 */
int32_t pme_submit_pattern( uint8_t classifier_id,
							 uint8_t * test_pattern,
							qm_pme_network_status_t * network_status);

/*
* Function to get the results from the last time the pme_submit_pattern was called
* This function may be called multiple times to read back more results until there are
 * no more results. For example, you may have a model with 128 patterns. In KNN mode
 * you can read back up to 128 distances, but it's not always practical to read all at
 * once. You may choose to read back the first 5, look at the results, then perhaps
 * read the next 5 as well, and so on until you've decided you looked at enough or
 * there are no results to read. IMPORTANT: You cannot go back and re-read results. If
 * you want to do that you have to call pme_submit_pattern with the same test_pattern
 * you called the first time.
 *
 * @param[in]      uint8_t         classifier_id      The ID of the classifier
 *                                                         used when you called
 *                                                         pme_submit_pattern. It is
 *                                                         the value you set in the
 *                                                         classifier_id field of the
 *                                                         kb_classifier_row_t table
 *                                                         you defined. This is only
 *                                                         used when you use the
 *                                                         software version of the
 *                                                         PME. It is ignored when
 *                                                         your platform has a
 *                                                         hardware PME.
 *
 * @param[in]     PME_RESULT_MANAGEMENT mode               An enum to specify what
 *                                                         method you want results
 *                                                         returned to you. See the
 *                                                         definition above for more
 *                                                         details.
 *
 * @param[in|out] uint8_t               *number_of_results You pass in a pointer to
 *                                                         the number of results you
 *                                                         desire. This should be the
 *                                                         less than or equal to the
 *                                                         size of the array pointed
 *                                                         to by the results parameter.
 *                                                         This function will set this
 *                                                         value to the number of
 *                                                         results that were actually
 *                                                         read. Stop reading back
 *                                                         values when this value is
 *                                                         set to a value less than
 *                                                         when you called
 *                                                         pme_retrieve_results.
 *
 * @param[out]    void                  *results           A pointer to the array of
 *                                                         structs you want to store
 *                                                         the results in. The type of
 *                                                         struct you use is determined
 *                                                         by the mode you use in the
 *                                                         'mode' parameter
 *
 * @return
 *             - TODO: return ?
*/
void pme_retrieve_results( uint8_t classifier_id, qm_pme_classification_mode_t mode,
							uint8_t *number_of_results, void *results);

/*
* Function to get the results from the last time the pme_submit_pattern was called
* This function may be called multiple times to read back more results until there are
* no more results. For example, you may have a model with 128 patterns. In KNN mode
 * you can read back up to 128 distances, but it's not always practical to read all at
 * once. You may choose to read back the first 5, look at the results, then perhaps
 * read the next 5 as well, and so on until you've decided you looked at enough or
 * there are no results to read. IMPORTANT: You cannot go back and re-read results. If
 * you want to do that you have to call pme_submit_pattern with the same test_pattern
 * you called the first time.
 *
 * @param[in]      uint8_t         classifier_id      The ID of the classifier
 *                                                         used when you called
 *                                                         pme_submit_pattern. It is
 *                                                         the value you set in the
 *                                                         classifier_id field of the
 *                                                         kb_classifier_row_t table
 *                                                         you defined. This is only
 *                                                         used when you use the
 *                                                         software version of the
 *                                                         PME. It is ignored when
 *                                                         your platform has a
 *                                                         hardware PME.
 *
 * @param[in]     PME_RESULT_MANAGEMENT mode               An enum to specify what
 *                                                         method you want results
 *                                                         returned to you. See the
 *                                                         definition above for more
 *                                                         details.
 *
 * @param[in|out] uint8_t               *number_of_results You pass in a pointer to
 *                                                         the number of results you
 *                                                         desire. This should be the
 *                                                         less than or equal to the
 *                                                         size of the array pointed
 *                                                         to by the results parameter.
 *                                                         This function will set this
 *                                                         value to the number of
 *                                                         results that were actually
 *                                                         read. Stop reading back
 *                                                         values when this value is
 *                                                         set to a value less than
 *                                                         when you called
 *                                                         pme_retrieve_results.
 *
 * @param[out]    void                  *results           A pointer to the array of
 *                                                         structs you want to store
 *                                                         the results in. The type of
 *                                                         struct you use is determined
 *                                                         by the mode you use in the
 *                                                         'mode' parameter
 *
 * @return
*             - TODO: return ?
*/
void pme_simple_submit_pattern_set_result( uint8_t classifier_id,  uint8_t *pattern, pme_result_dist_cat_id_t *result);



/**
 * Initialize the PME middle layer with information on all the classifiers. We
 * will populate the KBClassifierTable and KBResourceTable structures.
 *
 * @param[in]  kb_classifier_row_t *classifier_table Pointer to table with
 *                                                        all classifier info
 *
 * @param[in]  uint8_t              num_classifiers  The number of classifiers
 *                                                        in classifier_table
 *
 * @return
 *             - TODO: return ?
 */
int8_t pme_simple_init(kb_classifier_row_t *classifier_table,  uint8_t num_classifiers);

/**
 * Function to submit a test pattern to the PME and get results.
 *
 * @param[in]  uint8_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 *
 * @param[in]  uint8_t * pattern Pointer to test pattern
 *
 * @return
 *             - TODO: return ?
 */
int32_t pme_simple_submit_pattern( uint8_t  classifier_id,
                            feature_vector_t * test_pattern,
							model_results_t * model_result);


/**
 * Function to add a new pattern to the PME database.
 *
 * @param[in]  uint8_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 *
 * @param[in]  uint8_t * pattern Pointer to test pattern
*  @param[in]  int32_t * pattern Pointer to test pattern
 * @param[in]  uint8_t * pattern Pointer to test pattern
 *
 * @return
 *             - TODO: return 1 if pattern was added, -1 otherwise
 */
int32_t pme_add_new_pattern( int32_t classifier_id,  uint8_t * pattern,  uint16_t category,  uint16_t influence);


/**
 * Function to update neuron scores against a known category.
 *
 * @param[in]  uint8_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 *
 * @param[in]  uint8_t * pattern Pointer to test pattern
 * @param[in]  uint16_t category ground truth category of the pattern
 *
 * @return
 */
void pme_score_pattern(int32_t classifier_id, uint8_t * pattern,  uint16_t category);

/**
 * Rebalance the patterns stored in the database based on their current score. This will
 * reasign to each stored pattern the cateory with the highest ground truth score. After rebalancing
 * the scores are zeroes out.
 *
 * @param[in]  uint8_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 *
 *
 * @return
 */
void pme_rebalance_patterns(int32_t classifier_id);

/**
 * Print the scores currently held by the pattern
 *
 * @param[in]  uint8_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 *
 *
 * @return
 */
void pme_print_model_scores(int32_t classifier_id);

/**
 * Print the model that is currently stored in the database for classifier id
 *
 * @param[in]  uint8_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 *
 *
 * @return
 */
void pme_print_model(int32_t classifier_id);


/**
 * Return information about a specific pattern in a model
 *
 * @param[in] int32_t  classifier_id The ID of the classifier. It is the value you set
 *                                         in the classifier_id field of the
 *                                         kb_classifier_row_t table you defined.
 * @param[in] int32_t  pattern_index The ID of the pattern in the classifier to get
 * @param[in] pme_pattern_t pattern pointer to the pattern struct to fill
 *
 * @return
 */
void pme_return_pattern(int32_t classifier_id, int32_t pattern_index, pme_pattern_t * pattern);

/**
 * Set the number of patterns in a classifier to 0
 *
 *
 * @return
 */
void pme_flush_model(int32_t classifier_id);

/**
 * Get the number of patterns used by the classifier
 *
 *
 * @return
 */
int32_t pme_get_number_patterns(int32_t classifier_id);

void reduce_influence_fields(int32_t classifier_id);

// clang-format on
#ifdef __cplusplus
}
#endif

#endif /* PME_H_ */
