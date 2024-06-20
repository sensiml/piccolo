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


#define ARM_MATH_CM4
#define __FPU_PRESENT 1
#include "arm_math.h"
#define DIMENSION_D 5
#define DIMENSION_D_HAT 3
#define DIMENSION_L 2
#define NUM_NODES 3
#define DEPTH 2

const int16_t B_i16[4] =
	{
		782, 7577, 470, 4505};
/* --------------------------------------------------------------------------------

* -------------------------------------------------------------------------------- */
const int16_t Theta_i16[DIMENSION_D_HAT * NUM_NODES] =
	{
		1, 1, 1,
		2, 2, 2,
		3, 3, 3};

const int16_t W_i16[DIMENSION_D_HAT * DIMENSION_L * NUM_NODES] =
	{
		1, 1, 1, 1, 1, 1,
		2, 2, 2, 2, 2, 2,
		3, 3, 3, 3, 3, 3};

const int16_t V_i16[DIMENSION_D_HAT * DIMENSION_L * NUM_NODES] =
	{
		1, 1, 1, 1, 1, 1,
		2, 2, 2, 2, 2, 2,
		3, 3, 3, 3, 3, 3};

const int16_t Z_i16[DIMENSION_D_HAT * DIMENSION_D] =
	{
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
		1,
};

const int16_t X_i16[DIMENSION_D] =
	{
		1, 1, 1, 1, 1};

int16_t tree_path[2] = {0, 0};

/* ----------------------------------------------------------------------
* Temporary buffers  for storing intermediate values
* ------------------------------------------------------------------- */
int16_t ZX_q15[DIMENSION_D_HAT];

int16_t VZX_q15[DIMENSION_L];

int16_t WZX_q15[DIMENSION_L];

int16_t ThetaZX_q15[1];

q15_t sigma = 1;

static int32_t score[DIMENSION_L];

void update_treePath(arm_matrix_instance_q15 ZX)
{
	arm_matrix_instance_q15 ThetaZX;
	arm_matrix_instance_q15 Theta;
	int32_t curr_node = 0;
	int32_t index = 0;

	arm_mat_init_q15(&ThetaZX, 1, 1, (int16_t *)ThetaZX_q15);
	arm_mat_init_q15(&Theta, DIMENSION_D_HAT, 1, (int16_t *)Theta_i16);

	while (curr_node < NUM_NODES)
	{
		arm_mat_mult_q15(&Theta, &ZX, &ThetaZX, NULL);
		curr_node = ThetaZX_q15[0] > 0 ? 2 * curr_node + 1 : 2 * curr_node + 2;
		arm_mat_init_q15(&Theta, DIMENSION_D_HAT, 1, (q15_t *)&Theta_i16[curr_node * DIMENSION_D_HAT]);
		tree_path[index] = curr_node;
		index += 1;
	}
}

q15_t fast_tanh_q15(q15_t x)
{
	return x < 0 ? -1 : x;
}

void predict(arm_matrix_instance_q15 ZX)
{
	arm_matrix_instance_q15 VZX;
	arm_matrix_instance_q15 WZX;
	arm_matrix_instance_q15 W;
	arm_matrix_instance_q15 V;

	arm_mat_init_q15(&VZX, DIMENSION_L, 1, VZX_q15);
	arm_mat_init_q15(&WZX, DIMENSION_L, 1, WZX_q15);
	for (int32_t i = 0; i < DEPTH; i++)
	{
		arm_mat_init_q15(&W, DIMENSION_D_HAT, DIMENSION_L, (q15_t *)&W_i16[tree_path[i] * DIMENSION_D_HAT * DIMENSION_L]);
		arm_mat_init_q15(&V, DIMENSION_D_HAT, DIMENSION_L, (q15_t *)&V_i16[tree_path[i] * DIMENSION_D_HAT * DIMENSION_L]);
		arm_mat_mult_q15(&V, &ZX, &VZX, NULL);
		arm_mat_mult_q15(&W, &ZX, &WZX, NULL);
		arm_mat_scale_q15(&WZX, sigma, 0, &WZX);

		//hardmon and tanh
		for (int32_t j = 0; j < DIMENSION_L; j++)
		{
			score[j] += WZX_q15[j] * fast_tanh_q15(VZX_q15[j]);
		}
	}
}

int32_t main(void)
{
	arm_matrix_instance_q15 Z;
	arm_matrix_instance_q15 X;
	arm_matrix_instance_q15 ZX;

	/* Initialise A Matrix Instance with numRows, numCols and data array(A_f32) */
	arm_mat_init_q15(&Z, DIMENSION_D, DIMENSION_D_HAT, (q15_t *)Z_i16);
	arm_mat_init_q15(&X, DIMENSION_D, 1, (q15_t *)X_i16);
	arm_mat_init_q15(&ZX, DIMENSION_D_HAT, 1, (q15_t *)ZX_q15);

	arm_mat_mult_q15(&Z, &X, &ZX, NULL);

	update_treePath(ZX);
	predict(ZX);

	while (1)
		;
}
