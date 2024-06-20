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

/* this is taken from Sphinx (sphinxbase-0.8.tar); Sphinx copyright header below */

/* ====================================================================
 * Copyright (c) 1996-2004 Carnegie Mellon University.  All rights
 * reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions
 * are met:
 *
 * 1. Redistributions of source code must retain the above copyright
 *    notice, this list of conditions and the following disclaimer.
 *
 * 2. Redistributions in binary form must reproduce the above copyright
 *    notice, this list of conditions and the following disclaimer in
 *    the documentation and/or other materials provided with the
 *    distribution.
 *
 * This work was supported in part by funding from the Defense Advanced
 * Research Projects Agency and the National Science Foundation of the
 * United States of America, and the CMU Sphinx Speech Consortium.
 *
 * THIS SOFTWARE IS PROVIDED BY CARNEGIE MELLON UNIVERSITY ``AS IS'' AND
 * ANY EXPRESSED OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 * THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL CARNEGIE MELLON UNIVERSITY
 * NOR ITS EMPLOYEES BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
 * LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
 * DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
 * THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * ====================================================================
 *
 */

#ifndef _AVSASR_ROCKHOPPER_MINI_FRONTEND_SRC_FIXLOG_H_
#define _AVSASR_ROCKHOPPER_MINI_FRONTEND_SRC_FIXLOG_H_

#include <stdint.h>

#define DEFAULT_RADIX 12

#define MIN_FIXLOG -2829416  /* log(1e-300) * (1<<DEFAULT_RADIX) */
#define MIN_FIXLOG2 -4081985 /* log2(1e-300) * (1<<DEFAULT_RADIX) */
#define FIXLN_2		((int32_t)(0.693147180559945 * (1<<DEFAULT_RADIX)))

#define FIXMUL(a,b) FIXMUL_ANY(a,b,DEFAULT_RADIX)
#define FIXMUL_ANY(a,b,radix) ((int32_t)(((int64_t)(a)*(b))>>(radix)))
#define FIXLN(x) (fixlog(x) - (FIXLN_2 * DEFAULT_RADIX))

#define COS_RADIX 11

#define MFCCMUL(a,b) FIXMUL(a,b)

#ifdef __cplusplus
extern "C" {
#endif

int32_t sphinx_fixlog2(uint32_t x);
int32_t sphinx_fixlog(uint32_t x);
int32_t sphinx_fe_log_add(int32_t x, int32_t y);
int32_t sphinx_get_fixlog_rom_size(void);

#ifdef __cplusplus
}
#endif

#endif  /* _AVSASR_ROCKHOPPER_MINI_FRONTEND_SRC_FIXLOG_H_ */
