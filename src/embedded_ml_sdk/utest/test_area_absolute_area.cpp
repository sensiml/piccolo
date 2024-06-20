/* ----------------------------------------------------------------------
* Copyright (c) 2022 SensiML Corporation
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
* 1. Redistributions of source code must retain the above copyright notice,
*    this list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
* 3. Neither the name of the copyright holder nor the names of its contributors
*    may be used to endorse or promote products derived from this software
*    without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
* ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
* LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
* ---------------------------------------------------------------------- */

#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include <stdio.h>
#include "kb_utest_init.h"

#define NUM_COLS 3
#define NUM_ROWS_TEST1 8
#define NUM_ROWS_TEST2 12

static int16_t testdata1[NUM_COLS * NUM_ROWS_TEST1] = {
   1, -2, -3, 1, 2, 5, 2, -2,
   0, 9, 5, -5, -9, 0, 9, 5,
   1, -2, 3, -1, 2, 5, 2, -2};

static float abs_area_outputs1[NUM_COLS][1] = {
    {1.8},
    {4.2},
    {1.8}};

static int16_t testdata2[NUM_COLS * NUM_ROWS_TEST2] = {
    -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1,
    -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9,
    -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1};

static float abs_area_outputs2[NUM_COLS][1] = {
    {2.9},
    {7.0},
    {2.9}};


class FGAreaAbsoluteArea : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_COLS;
        num_rows = NUM_ROWS_TEST1;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, testdata1, num_cols, num_rows);
        params.size =1;
        params.data[0] = 10;
        ret = 0;
    }
};

TEST_F(FGAreaAbsoluteArea, kb_model_NULL_test)
{

    int ret = fg_area_absolute_area(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_area_absolute_area(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_area_absolute_area(&kb_model, &cols_to_use, NULL, pFV);
    ASSERT_EQ(0, ret);

}


TEST_F(FGAreaAbsoluteArea, calculation_dataset1_test)
{
    cols_to_use.size=3;
    cols_to_use.data[0] = 2;
    cols_to_use.data[0] = 0;
    cols_to_use.data[0] = 1;
    params.data[0] = 10; // sample rate
    params.size = 1; // sample rate

    int ret = fg_area_absolute_area(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(ret, num_cols);

    // abs_sum computation test, expects an array of outputs
    int i;
    for (i = 0; i < ret; i++)
    {
        ASSERT_NEAR(abs_area_outputs1[cols_to_use.data[i]][0], pFV[i], 0.0001);
    }
}


TEST_F(FGAreaAbsoluteArea, calculation_dataset2_test)
{


    init_kb_model(&kb_model, &rb[0], 0, NUM_ROWS_TEST2, testdata2, NUM_COLS, NUM_ROWS_TEST2);
    cols_to_use.size=3;
    cols_to_use.data[0] = 0;
    cols_to_use.data[1] = 1;
    cols_to_use.data[2] = 2;
    params.data[0] = 10; // sample rate
    params.size = 1; // sample rate
    int ret = fg_area_absolute_area(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(ret, num_cols);

    // abs_sum computation test, expects an array of outputs
    int i;
    for (i = 0; i < ret; i++)
    {
        printf("index %d result %f expected %f\n", i, pFV[i], abs_area_outputs2[cols_to_use.data[i]][0]);
        ASSERT_NEAR(abs_area_outputs2[cols_to_use.data[i]][0], pFV[i], 0.0001);
    }
}
