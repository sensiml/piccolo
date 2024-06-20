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
    0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110,
    0, 0, 0, 10, 10, 10, 20, 20, 20, 30, 30, 30,
    -30000, 10000, 10000, 30000, 32000, 10000, 20000, 32000, 20000, -30000, -20000, -10000};

static float expected_outputs[NUM_INPUT_COLS] = {60, 20, 5000};
static float expected_outputs_threshold_75[NUM_INPUT_COLS] = {60, 20, 40000};
static float expected_outputs_threshold_25[NUM_INPUT_COLS] = {60, 20, 10000};

class FGShapeAbsoluteMedianDifference : public testing::Test
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

TEST_F(FGShapeAbsoluteMedianDifference, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_shape_absolute_median_difference(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGShapeAbsoluteMedianDifference, NULL_cols_to_use_param_test)
{
    ret = fg_shape_absolute_median_difference(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGShapeAbsoluteMedianDifference, ZERO_num_cols_param_test)
{
    cols_to_use.size=0;
    ret = fg_shape_absolute_median_difference(&kb_model, &cols_to_use, &params, pFV);
    cols_to_use.size=NUM_INPUT_COLS;
    ASSERT_EQ(0, ret);
}

TEST_F(FGShapeAbsoluteMedianDifference, NULL_feature_vector_test)
{
    ret = fg_shape_absolute_median_difference(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGShapeAbsoluteMedianDifference, generate_features_test)
{
    params.data[0] = .5;
    ret = fg_shape_absolute_median_difference(&kb_model, &cols_to_use, &params, pFV);
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

TEST_F(FGShapeAbsoluteMedianDifference, generate_features_threshold_75_test)
{
    params.data[0] = .75;
    ret = fg_shape_absolute_median_difference(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(num_cols, ret);
    float tolerance = 0.001f;

    if (ret == num_cols)
    {
        int icol;
        for (icol = 0; icol < cols_to_use.size; icol++)
        {
            printf("pFV[%d] = %f\n", icol, pFV[icol]);
            EXPECT_NEAR(pFV[icol], expected_outputs_threshold_75[icol], tolerance);
        }
    }
}

TEST_F(FGShapeAbsoluteMedianDifference, generate_features_threshold_25_test)
{
    params.data[0] = .25;
    ret = fg_shape_absolute_median_difference(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(num_cols, ret);
    float tolerance = 0.001f;

    if (ret == num_cols)
    {
        int icol;
        for (icol = 0; icol < cols_to_use.size; icol++)
        {
            printf("pFV[%d] = %f\n", icol, pFV[icol]);
            EXPECT_NEAR(pFV[icol], expected_outputs_threshold_25[icol], tolerance);
        }
    }
}