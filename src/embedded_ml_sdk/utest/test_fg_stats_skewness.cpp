#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"

#define NUM_ROWS 5
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 3

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    -3, 3, 0,
    -2, 2, 6,
    7, 6, 8,
    9, 5, 8,
    3, 7, 6};
static float stats_skew_outputs[NUM_INPUT_COLS] = {0.0f, 0.363173f, -0.39587f};

class FGStatsSkewness : public testing::Test
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
        params.data[0] = 1; // mean by default
        ret = 0;
    }
};

TEST_F(FGStatsSkewness, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_stats_skewness(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsSkewness, NULL_cols_to_use_param_test)
{
    ret = fg_stats_skewness(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsSkewness, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_stats_skewness(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsSkewness, NULL_feature_vector_test)
{
    ret = fg_stats_skewness(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsSkewness, generate_features_test)
{
    ret = fg_stats_skewness(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(3, ret);
    float tolerance = 0.001f;
    if (ret == 3)
    {
        int icol;
        for (icol = 0; icol < 3; icol++)
        {
            ASSERT_NEAR(pFV[icol], stats_skew_outputs[icol], tolerance);
        }
    }
}