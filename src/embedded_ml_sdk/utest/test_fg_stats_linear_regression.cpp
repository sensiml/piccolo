#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_ROWS 12
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 12

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110,
    0, 10, 20, 30, 40, 50, 60, 50, 40, 30, 20, 10,
    -30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000};

static float expected_outputs[NUM_FG_OUTPUTS] = {10, 0, 1, 0, 1.2587, 23.076, .244181, 1.580, -1293.7062937062938, 13282.051282051281, -0.201550846172971, 1988.134558476637};

class FGStatsLinearRegression : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);
        params.size =0;
        params.data[0] = 0;
        ret = 0;
    }
};

TEST_F(FGStatsLinearRegression, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_stats_linear_regression(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsLinearRegression, NULL_cols_to_use_param_test)
{
    ret = fg_stats_linear_regression(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsLinearRegression, ZERO_num_cols_param_test)
{
    cols_to_use.size = 0;
    ret = fg_stats_linear_regression(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsLinearRegression, NULL_feature_vector_test)
{
    ret = fg_stats_linear_regression(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsLinearRegression, generate_features_test)
{
    cols_to_use.size=3;
    ret = fg_stats_linear_regression(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
    float tolerance = 0.001f;
    for (int i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        //printf("pFV[%d] = %f\n", i, pFV[i]);
        EXPECT_NEAR(pFV[i], expected_outputs[i], tolerance);
    }
}
