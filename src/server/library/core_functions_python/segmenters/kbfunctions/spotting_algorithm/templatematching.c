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




/*
 * Author(s) : Giuseppe Raffa, Noura Farra
 * Group : IXR/Intel Labs
 * modified to linux kernel coding style by Alek Du (PSI, MCG)
 * code cleanup and maintained by Han Ke (PSI, MCG)
 */

/*#define CPP_DBG*/
#ifdef CPP_DBG
#include <fstream>
#endif

#include "templatematching.h"
#include "gesturespotting.h"
#include "movementdetection.h"
#include "mathcontext.h"

struct gesture_api_config
{
    int temp_match_relax_factor_all; /* for general early template matching */
};

/*static variables*/
/*this is the template which contains the feature boundaries for all gestures*/
static struct template_entry entry[TEMPLATE_MATHING_NUM_DIM];
static u8 num_dim;
static s16 one_g;
static int features[TEMPLATE_MATHING_NUM_DIM];
static u8 init_flag = 0;

int *calculatefeatures(struct gesture_struct *gesture, u8 sample_size_items);

u8 temp_match_init(s16 _one_g, struct template_entry features_entry[], u8 _num_dim)
{
    u8 i;
    if (unlikely(features_entry == NULL))
    {
        init_flag = 0;
        return init_flag;
    }

    one_g = _one_g;
    num_dim = _num_dim;
    if (unlikely(num_dim > TEMPLATE_MATHING_NUM_DIM))
        num_dim = TEMPLATE_MATHING_NUM_DIM;

    for (i = 0; i < num_dim; i++)
    {
        entry[i].max = features_entry[i].max;
        entry[i].max_valid = features_entry[i].max_valid;
        entry[i].min = features_entry[i].min;
        entry[i].min_valid = features_entry[i].min_valid;
        entry[i].ndim = features_entry[i].ndim;
    }
    init_flag = 1;
    return init_flag;
}

int temp_match_apply(struct gesture_struct *g, u8 sample_size_items)
{
    u8 res[TEMPLATE_MATHING_NUM_DIM];
    u8 match = 1;
    int *vals;
    u16 i;
    int val;
    int min;
    int max;
    int range;
    int softmargin;
    struct gesture_api_config gesture_config;

    if (unlikely(init_flag == 0 || g == NULL)) /* if not initialize, or g invalid */
        return 0;                              /* return false */

    /*indicates range>>factor will be used as a soft margin*/
    gesture_config.temp_match_relax_factor_all = 1;

    vals = calculatefeatures(g, sample_size_items); /*num_dim will be 2*/
    if (unlikely(vals == NULL))
        return 0;

    for (i = 0; i < num_dim; i++)
    {
        val = vals[i];
        min = entry[i].min;
        max = entry[i].max;
        range = max - min;
        softmargin = range >> gesture_config.temp_match_relax_factor_all;

        max = max + softmargin;
        min = min - softmargin;

        if (val >= min && val <= max)
            res[i] = 1;
        else
            res[i] = 0;
    }

    for (i = 0; i < num_dim; i++)
    {
        if (!res[i])
        {
            match = 0;
            break;
        }
    }
    return match;
}

int *calculatefeatures(struct gesture_struct *gesture, u8 sample_size_items)
{
    s16 *sample;
    s16 max = -32000; /*power*/
    s16 ax;
    s16 ay;
    s16 az;
    int s;
    u32 i;

    if (unlikely(init_flag == 0 || gesture == NULL)) /* not initialize, or g invalid */
        return NULL;                                 /* return NULL */
    sample = gesture->sample;

    for (i = 0; i < gesture->size_samples * sample_size_items; i += sample_size_items)
    {
        ax = sample[i];
        ay = sample[i + 1];
        az = sample[i + 2];

        s = (int)m_abs(m_sqrt(ax * ax + ay * ay + az * az) - one_g);
        if (s > max)
            max = s;
    }

    features[0] = gesture->size_samples;
    features[1] = max;

    return features;
}
