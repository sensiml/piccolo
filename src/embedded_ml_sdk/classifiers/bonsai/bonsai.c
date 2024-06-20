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




#include "arm_math.h"
#include "bonsai.h"
#include <stdio.h>

// FILL_MAX_BONSAI_TMP_PARAMETERS
#ifndef MAX_PROJECTION_DIMENSION
#define MAX_PROJECTION_DIMENSION 100
#endif
#ifndef MAX_INPUT_DIMENSION
#define MAX_INPUT_DIMENSION 100
#endif
#ifndef MAX_NUM_NODES
#define MAX_NUM_NODES 100
#endif
#ifndef MAX_NUMBER_CLASSES
#define MAX_NUMBER_CLASSES 100
#endif

#define PROJECTION_DIMENSION MAX_PROJECTION_DIMENSION
#define NUMBER_CLASSES MAX_NUMBER_CLASSES
#define NUM_NODES MAX_NUM_NODES

bonsai_classifier_rows_t *BonsaiClassifierTable;

/* ----------------------------------------------------------------------
 * Temporary buffers  for storing intermediate values
 * ------------------------------------------------------------------- */
static float32_t ZX_f32[PROJECTION_DIMENSION];

static float32_t VZX_f32[NUMBER_CLASSES];

static float32_t WZX_f32[NUMBER_CLASSES];

static float32_t ThetaZX_f32[1];

static int32_t tree_path[NUM_NODES + 1];

static float score[NUMBER_CLASSES];

/*------------------------------------------------------------------- */

static int32_t status;

/*
float32_t fast_tanh_f32(float x)
{
    return x < 0. ? -1 : x == 0. ? 0. : x;
}
*/

float32_t fast_tanh_f32(float x)
{
    if (x < -1)
    {
        return -1.0f;
    }
    if (x > 1)
    {
        return 1.0f;
    }
    return x;
}

void update_tree_path(bonsai_t *bonsai, arm_matrix_instance_f32 ZX)
{
    arm_matrix_instance_f32 ThetaZX;
    arm_matrix_instance_f32 Theta;
    int32_t curr_node = 0;
    int32_t index = 1;
    tree_path[0] = 0;

    arm_mat_init_f32(&ThetaZX, 1, 1, ThetaZX_f32);
    arm_mat_init_f32(&Theta, 1, bonsai->d_proj, bonsai->Theta);

    while (1)
    {
        status = arm_mat_mult_f32(&Theta, &ZX, &ThetaZX);
        // printf("\nStatus ThetaZx %d\n", status);

        /*
        printf("Theta_%d\n", curr_node);
        for (int32_t i=0; i < bonsai->d_proj; i++)
        {
           printf("%f, ", Theta.pData[i]);
        }
        printf("\n");

        printf("ThetaZX_%d\n", curr_node);
        for (int32_t i=0; i < 1; i++)
        {
           printf("%f, ", ThetaZX.pData[i]);
        }
        printf("\n");
        */

        curr_node = ThetaZX_f32[0] > 0 ? 2 * curr_node + 1 : 2 * curr_node + 2;
        if (curr_node > bonsai->num_nodes)
        {
            break;
        }
        arm_mat_init_f32(&Theta, 1, bonsai->d_proj, &bonsai->Theta[curr_node * bonsai->d_proj]);
        tree_path[index] = curr_node;
        index += 1;
    }
}

void bonsai_predict(bonsai_t *bonsai, arm_matrix_instance_f32 ZX)
{
    int32_t i, j;

    arm_matrix_instance_f32 VZX;
    arm_matrix_instance_f32 WZX;
    arm_matrix_instance_f32 W;
    arm_matrix_instance_f32 V;

    arm_mat_init_f32(&VZX, bonsai->d_l, 1, VZX_f32);
    arm_mat_init_f32(&WZX, bonsai->d_l, 1, WZX_f32);

    for (i = 0; i < bonsai->d_l; i++)
    {
        score[i] = 0;
    }

    for (i = 0; i <= bonsai->depth; i++)
    {

        arm_mat_init_f32(&W, bonsai->d_l, bonsai->d_proj,
                         &bonsai->W[tree_path[i] * bonsai->d_proj * bonsai->d_l]);

        arm_mat_init_f32(&V, bonsai->d_l, bonsai->d_proj,
                         &bonsai->V[tree_path[i] * bonsai->d_proj * bonsai->d_l]);

        status = arm_mat_mult_f32(&V, &ZX, &VZX);
        // printf("\nStatus VZx %d\n", status);

        status = arm_mat_mult_f32(&W, &ZX, &WZX);
        // printf("\nStatus WZx %d\n", status);

        /*
        printf("current node %d", tree_path[i]);
        printf("\n\nW_%d\n", tree_path[i]);
        for (int32_t k = 0; k < bonsai->d_l * bonsai->d_proj; k++)
        {
            if (k % bonsai->d_proj == 0)
            {
                printf("\n\t");
            }
            printf("%f ", W.pData[k]);
        }

        printf("\n\nWZx\n");
        for (int32_t k = 0; k < bonsai->d_l; k++)
        {
            printf("%f, ", WZX.pData[k]);
        }
        printf("\n");

        printf("\n\nV_%d\n", tree_path[i]);
        for (int32_t k = 0; k < bonsai->d_l * bonsai->d_proj; k++)
        {
            if (k % bonsai->d_proj == 0)
            {
                printf("\n\t");
            }
            printf("%f ", V.pData[k]);
        }

        printf("\n\nVZX\n");
        for (int32_t k = 0; k < bonsai->d_l; k++)
        {
            printf("%f, ", VZX.pData[k]);
        }
        printf("\n");

        */

        // hardmon and tanh
        for (j = 0; j < bonsai->d_l; j++)
        {
            score[j] += WZX_f32[j] * fast_tanh_f32(VZX_f32[j]);
            // printf("node %d, score %d: %f , WZX: %f, VZX: %f Tan %fh\n", tree_path[i], j, score[j], WZX.pData[j], VZX.pData[j], fast_tanh_f32(VZX.pData[j]));
        }
    }
}

uint8_t bonsai_classification(bonsai_t *bonsai, uint8_t *feature_vector)
{

    uint8_t y;
    float max_score = 0;

    arm_matrix_instance_f32 Z;
    arm_matrix_instance_f32 X;
    arm_matrix_instance_f32 ZX;
    arm_matrix_instance_f32 mean;

    for (int32_t i = 0; i < bonsai->d_input - 1; i++)
    {
        bonsai->X[i] = (float)feature_vector[i];
    }

    /* Initialise A Matrix Instance with numRows, numCols and data array */
    arm_mat_init_f32(&Z, bonsai->d_proj, bonsai->d_input, bonsai->Z);
    arm_mat_init_f32(&X, bonsai->d_input, 1, bonsai->X);
    arm_mat_init_f32(&mean, bonsai->d_proj, 1, bonsai->mean);
    arm_mat_init_f32(&ZX, bonsai->d_proj, 1, ZX_f32);

    status = arm_mat_mult_f32(&Z, &X, &ZX);
    // printf("\nStatus Zx %d", status);

    /*
    printf("\n\nZ\n");

    for (int32_t i = 0; i < bonsai->d_input * bonsai->d_proj; i++)
    {
        if (i % bonsai->d_input == 0)
        {
            printf("\n\t", i, bonsai->Z[i]);
        }
        printf("%f ", i, Z.pData[i]);
    }

    printf("\n\nX\n");
    for (int32_t i = 0; i < bonsai->d_input; i++)
    {
        printf("%f, ", i, X.pData[i]);
    }

    printf("\n\nZX\n");
    for (int32_t i = 0; i < bonsai->d_proj; i++)
    {
        printf("%f, ", i, ZX.pData[i]);
    }
    printf("\n");

    printf("\n\nMean\n");
    for (int32_t i = 0; i < bonsai->d_input; i++)
    {
        printf("%f, ", i, mean.pData[i]);
    }

    */

    status = arm_mat_sub_f32(&ZX, &mean, &ZX);

    // printf("\nStatus Zx after mean %d", status);

    /*
    printf("\n\nZX after subtraction\n");
    for (int32_t i = 0; i < bonsai->d_proj; i++)
    {
        printf("%f, ", i, ZX.pData[i]);
    }
    printf("\n");
    */

    update_tree_path(bonsai, ZX);
    bonsai_predict(bonsai, ZX);

    max_score = score[0];
    y = 1;

    if (bonsai->d_l > 2)
    {
        for (int32_t i = 1; i < bonsai->d_l; i++)
        {
            if (score[i] > max_score)
            {
                max_score = score[i];
                y = i + 1; // 0 is reserved
            }
        }
    }
    else
    {
        if (score[0] > 0)
            y = 2;
    }

    return y;
}

/*
 * Inititalize the PME
 */
void bonsai_init(bonsai_classifier_rows_t *classifier_table, const uint8_t num_classifiers)
{
    BonsaiClassifierTable = classifier_table;
}

uint8_t bonsai_simple_submit(uint8_t classifier_id, feature_vector_t *feature_vector, model_results_t *model_results)
{
    model_results->result = (float)bonsai_classification(BonsaiClassifierTable[classifier_id].bonsai, (uint8_t *)feature_vector->data);
    return (uint8_t)model_results->result;
}
