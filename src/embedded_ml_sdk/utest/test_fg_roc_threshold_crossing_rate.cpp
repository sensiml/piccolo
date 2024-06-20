#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kbutils.h"
#include <stdio.h>
#include "kb_utest_init.h"


#define NUM_ROWS 20
#define NUM_INPUT_COLS 3

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] =
    {0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9,
     -100, 100, -100, 100, -100, 100, -100, 100, -100, 100, -100, 100, -100,  100, -100, 100, -100, 100, -100, 100,
     -100, 0, 50, 0, 100, 0, 50, 0, 100, 0, 50, 0, 100,  0, 50,  0, 100,  0, 50,  0};

static float expected_outputs[NUM_INPUT_COLS] = {0, 1.0, 0.42105263471603394};

class FGROCThresholdCrossingRate : public testing::Test
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


TEST_F(FGROCThresholdCrossingRate, kb_model_NULL_test)
{

    ret = fg_roc_threshold_crossing_rate(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(ret, 0);
    ret = fg_roc_threshold_crossing_rate(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(ret, 0);
    ret = fg_roc_threshold_crossing_rate(&kb_model, &cols_to_use, NULL, pFV);
    ASSERT_EQ(ret, 0);
    ret = fg_roc_threshold_crossing_rate(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(ret, 0);
}

TEST_F(FGROCThresholdCrossingRate, calculation_dataset1_test)
{

    cols_to_use.size = NUM_INPUT_COLS;
    params.size =1;
    params.data[0]=50;


    int ret = fg_roc_threshold_crossing_rate(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(ret, num_cols);

    int i;
    for (i = 0; i < ret; i++)
    {
        printf("pFV[%d] = %f\n", i, pFV[i]);
        ASSERT_NEAR(expected_outputs[i], pFV[i], 0.0001);
    }
}
