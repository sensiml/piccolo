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



#ifndef KB_PIPELINE_H
#define KB_PIPELINE_H

#ifdef WIN32
#include <stdio.h>
#include <math.h>
#include <time.h>
#else
#pragma GCC diagnostic ignored "-Wunused-function"
#pragma GCC diagnostic ignored "-Wunused-variable"
#endif

#include <stdint.h>
#include <stddef.h>

#include "kb_defines.h"
#include "kb_common.h"
#include "kb_typedefs.h"
#include "kbalgorithms.h"
#include "kbutils.h"

#ifdef __cplusplus
extern "C"
{
#endif

    // FILL_SENSOR_COLUMN_NAMES

    // FILL_DATA_COLUMN_NAMES

    // FILL_MODEL_FUNCTION_DEFS

#ifdef __cplusplus
}
#endif

#endif // KB_PIPELINE_H
