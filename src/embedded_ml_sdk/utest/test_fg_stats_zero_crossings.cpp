#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_ROWS 12
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 3

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    -300, -100, 0, 100, 300, 100, 0, -100, -300, -100, 0, 100,
    -5000, -9000, 0, 9000, 5000, -5000, -9000, 0, 9000, 5000, -5000, -9000,
    -30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000};

static float expected_outputs[NUM_INPUT_COLS] = {3, 4, 2};
static float expected_outputs_threshold_100[NUM_INPUT_COLS] = {6, 8, 4};
static float expected_outputs_threshold_1000[NUM_INPUT_COLS] = {0, 8, 4};

class FGStatsZeroCrossings : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);
        params.size =1;
        params.data[0] = 0;
        ret = 0;
    }
};

TEST_F(FGStatsZeroCrossings, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_stats_zero_crossings(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsZeroCrossings, NULL_cols_to_use_param_test)
{
    ret = fg_stats_zero_crossings(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsZeroCrossings, ZERO_num_cols_param_test)
{
    cols_to_use.size = 0;
    ret = fg_stats_zero_crossings(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsZeroCrossings, NULL_feature_vector_test)
{
    ret = fg_stats_zero_crossings(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsZeroCrossings, generate_features_test)
{
    ret = fg_stats_zero_crossings(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(num_cols, ret);
    float tolerance = 0.001f;
    if (ret == num_cols)
    {
        int icol;
        for (icol = 0; icol < cols_to_use.size; icol++)
        {
            printf("pFV[%d] = %f\n", icol, pFV[icol]);
            EXPECT_NEAR(pFV[icol], expected_outputs[icol], tolerance);
        }
    }
}

TEST_F(FGStatsZeroCrossings, generate_features_threshold_100_test)
{
    params.data[0] = 100;
    ret = fg_stats_zero_crossings(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(num_cols, ret);
    float tolerance = 0.001f;

    if (ret == num_cols)
    {
        int icol;
        for (icol = 0; icol < cols_to_use.size; icol++)
        {
            printf("pFV[%d] = %f\n", icol, pFV[icol]);
            EXPECT_NEAR(pFV[icol], expected_outputs_threshold_100[icol], tolerance);
        }
    }
}

TEST_F(FGStatsZeroCrossings, generate_features_threshold_1000_test)
{
    params.data[0] = 1000;
    ret = fg_stats_zero_crossings(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(num_cols, ret);
    float tolerance = 0.001f;

    if (ret == num_cols)
    {
        int icol;
        for (icol = 0; icol < cols_to_use.size; icol++)
        {
            printf("pFV[%d] = %f\n", icol, pFV[icol]);
            EXPECT_NEAR(pFV[icol], expected_outputs_threshold_1000[icol], tolerance);
        }
    }
}