#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 3

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    5393, 13675, 18572, 5039, 4882, 5842, 9514, 14003, 5951, 17153,
    -6310, -7920, -10815, -18178, -3419, -11819, -19908, -10131, -4927, -8763,
    6638, -7138, 5272, -8312, -14323, 10925, -14151, -3248, 19479, -10160};
static float fg_stats_abs_sum_outputs[NUM_INPUT_COLS] = {100024.0f, 102190.0f, 99646.0f};

class FGStatsAbsSum : public testing::Test
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

TEST_F(FGStatsAbsSum, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_stats_abs_sum(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsAbsSum, NULL_cols_to_use_param_test)
{
    ret = fg_stats_abs_sum(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsAbsSum, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsAbsSum, NULL_feature_vector_test)
{
    ret = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGStatsAbsSum, generate_features_test)
{
    ret = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(3, ret);
    float tolerance = 0.001f;
    if (ret == 3)
    {
        int icol;
        for (icol = 0; icol < 3; icol++)
        {
            ASSERT_NEAR(pFV[icol], fg_stats_abs_sum_outputs[icol], tolerance);
        }
    }
}