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

#ifndef _PME_TRAINED_NEURONS_H_
#define _PME_TRAINED_NEURONS_H_

#include "pme.h"
#include "kb_classifier.h"

#ifdef __cplusplus
extern "C" {
#endif

#define KB_DISTANCE_L1 QM_PME_L1_DISTANCE
#define KB_DISTANCE_LSUP QM_PME_LSUP_DISTANCE
#define KB_DISTANCE_DTW QM_PME_DTW_DISTANCE
#define KB_CLASSIFICATION_RBF QM_PME_RBF_CLASSIFICATION
#define KB_CLASSIFICATION_KNN QM_PME_KNN_CLASSIFICATION

// FILL_PME_TRAINED_MODEL_HEADER

extern kb_classifier_row_t kb_classifier_rows[];

extern const int32_t neurons_count;

#ifdef __cplusplus
}
#endif

#endif //_PME_TRAINED_NEURONS_H_
