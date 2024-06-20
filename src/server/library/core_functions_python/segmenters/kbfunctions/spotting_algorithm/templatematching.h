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

#ifndef TEMP_MATCH_H
#define TEMP_MATCH_H

#include "gesturespotting.h"
#include "movementdetection.h"

/* public functions */
u8 temp_match_init(s16 _ONE_G, struct template_entry features_entry[], u8 num_dim);

/* we expect sample to be ax,ay,az,gx,gy,gz */
int temp_match_apply(struct gesture_struct *g, u8 sample_size_items);

#endif


