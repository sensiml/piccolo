#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"

#define NUM_ROWS 8
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 3

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    1, -2, -3, 1, 2, 5, 2, -2,
    0, 9, 5, -5, -9, 0, 9, 5,
    1, -2, 3, -1, 2, 5, 2, -2};

static float stats_sum_outputs[NUM_INPUT_COLS] = {4.0, 14.0, 8.0};

class FGAreaTotalArea : public testing::Test
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

TEST_F(FGAreaTotalArea, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_area_total_area(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGAreaTotalArea, NULL_cols_to_use_param_test)
{
    ret = fg_area_total_area(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGAreaTotalArea, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_area_total_area(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGAreaTotalArea, NULL_feature_vector_test)
{
    ret = fg_area_total_area(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGAreaTotalArea, generate_features_test)
{
    ret = fg_area_total_area(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(3, ret);
    float tolerance = 0.001f;
    if (ret == 3)
    {
        int icol;
        for (icol = 0; icol < 3; icol++)
        {
            ASSERT_NEAR(pFV[icol], stats_sum_outputs[icol], tolerance);
        }
    }
}
