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

#ifndef _KB_DEFINES_H_
#define _KB_DEFINES_H_
#include "kb_typedefs.h"
#include "stdio.h"
#ifdef __cplusplus
extern "C"
{
#endif

#define SML_DEBUG 1
#define SML_PROFILER 0
#ifndef SML_DEBUG
#define SML_DEBUG 0
#endif
#ifndef SML_PROFILER
#define SML_PROFILER 0
#endif

#ifdef __cplusplus
}
#endif

#endif //_KB_DEFINES_H_
