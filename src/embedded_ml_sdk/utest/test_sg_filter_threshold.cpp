#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_INPUT_COLS 3
static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {

    //all positive
    0,
    100,
    1000,
    2000,
    1000,
    100,
    0,
    100,
    1000,
    2000,

    //all negative
    0,
    -100,
    -1000,
    -2000,
    -1000,
    -100,
    0,
    -100,
    -1000,
    -2000,

    //mixture of positive and negative
    0,
    -100,
    -1000,
    -2000,
    -1000,
    -100,
    0,
    100,
    1000,
    2000,
};

class SGFilterThresholdTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);

        params.size =2;
        params.data[0] = 100; // threshold
        params.data[1] = 0;   // comparison >
        ret = 0;
    }
};

TEST_F(SGFilterThresholdTest, kb_model_NULL_param_test)
{
    ret = sg_filter_threshold(NULL, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
    ret = sg_filter_threshold(&kb_model, NULL, &params);
    ASSERT_EQ(-1, ret);
    ret = sg_filter_threshold(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(-1, ret);        
}


TEST_F(SGFilterThresholdTest, return_filters_out_segment_compare_greater)
{
    params.data[0] = (float)100;
    params.data[1] = (float)0;
    cols_to_use.data[0] = 0;
    num_cols = 1;

    ret = sg_filter_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterThresholdTest, return_filters_out_segment_compre_less)
{
    params.data[0] = (float)100;
    params.data[1] = (float)1;
    cols_to_use.data[0] = 0;
    num_cols = 1;

    ret = sg_filter_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterThresholdTest, return_allow_segment_compre_less)
{
    params.data[0] = (float)-20000;
    params.data[1] = (float)1;
    cols_to_use.data[0] = 0;
    num_cols = 1;

    ret = sg_filter_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);
}

TEST_F(SGFilterThresholdTest, return_allow_segment_compre_greater)
{
    params.data[0] = (float)2000;
    params.data[1] = (float)0;
    cols_to_use.data[0] = 0;
    num_cols = 1;

    ret = sg_filter_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);
}
