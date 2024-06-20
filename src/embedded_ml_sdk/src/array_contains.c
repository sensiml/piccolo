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




#include "kbutils.h"

//              array_contains.c
//
//
//

bool selection_contains(int32_t feature, int32_t num_feature_selection,
                        int32_t *feature_selection)
//
// Given a feature number, return [is this feature in the list?]
// If the list is NULL, then return true.
//
{
    int32_t i;

    if (num_feature_selection == 0)
        return true;

    for (i = num_feature_selection; i > 0; i--)
    {
        if (*feature_selection++ == feature)
        {
            return true;
        }
    }

    return false;
}

int32_t selection_index(int32_t feature, int32_t num_feature_selection,
                        int32_t *feature_selection)
//
// Given a feature number, return the correct bin index.
// In other words, translate a selected feature back into the correct bin index.
// If the feature is not found, return -1.
//
//
{
    int32_t i;

    for (i = 0; i < num_feature_selection; i++)
    {
        if (*feature_selection++ == feature)
        {
            return i;
        }
    }

    return -1;
}

//
