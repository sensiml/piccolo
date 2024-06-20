#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_ROWS 8
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 3
#define NUM_OUTPUT_COLS 1

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    2, 2, 2, 2, 2, 2, 2, 2,
    -2, -2, -2, -2, -2, -2, -2, -2,
    32000, 32000, 32000, 32000, 32000, 32000, 32000, 32000};

static float fg_physical_average_movement_intensity_outputs[NUM_INPUT_COLS] = {32000.000000};

class FGPhyscicalAverageMovementIntensity : public testing::Test
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

TEST_F(FGPhyscicalAverageMovementIntensity, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_physical_average_movement_intensity(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPhyscicalAverageMovementIntensity, NULL_cols_to_use_param_test)
{
    ret = fg_physical_average_movement_intensity(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPhyscicalAverageMovementIntensity, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_physical_average_movement_intensity(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPhyscicalAverageMovementIntensity, NULL_feature_vector_test)
{
    ret = fg_physical_average_movement_intensity(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPhyscicalAverageMovementIntensity, generate_features_test)
{
    ret = fg_physical_average_movement_intensity(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(1, ret);
    float tolerance = 0.001f;
    if (ret == 1)
    {
        int icol = 0;
        printf("pFV[%d] = %f\n", icol, pFV[icol]);
        EXPECT_NEAR(pFV[icol], fg_physical_average_movement_intensity_outputs[icol], tolerance);
    }
}