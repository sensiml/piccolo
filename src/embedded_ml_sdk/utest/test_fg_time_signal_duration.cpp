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

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    1, -2, -3, 1, 2, 5, 2, -2,
    0, 9, 5, -5, -9, 0, 9, 5,
    1, -2, 3, -1, 2, 5, 2, -2};

static float expected_outputs[NUM_FG_OUTPUTS] = {1.6, 1.6, 1.6};

/*
#define NUM_ROWS 12
static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    -3, -1, 1, -3, -4,  1,  2,  6,  2, -3, -2, -1,
    -5, -9, 0,  9,  5, -5, -9,  0,  9,  5, -5, -9,
    -3,  1, 1,  3,  4,  1,  2,  6,  2, -3, -2, -1
};

static float expected_outputs[NUM_FG_OUTPUTS] = { 2.4, 2.4, 2.4 };
*/

class FGTimeSignalDuration : public testing::Test
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
        params.data[0] = 5.0;
        ret = 0;
    }
};

TEST_F(FGTimeSignalDuration, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_time_signal_duration(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTimeSignalDuration, NULL_cols_to_use_param_test)
{
    ret = fg_time_signal_duration(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTimeSignalDuration, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_time_signal_duration(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTimeSignalDuration, NULL_feature_vector_test)
{
    ret = fg_time_signal_duration(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTimeSignalDuration, generate_features_test)
{
    ret = fg_time_signal_duration(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
    float tolerance = 0.001f;
    if (ret == NUM_FG_OUTPUTS)
    {
        int i;
        for (i = 0; i < NUM_FG_OUTPUTS; i++)
        {
            //printf("pFV[%d] = %f\n", i, pFV[i]);
            EXPECT_NEAR(pFV[i], expected_outputs[i], tolerance);
        }
    }
}
