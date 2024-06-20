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

class SGFilterMSETest : public testing::Test
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

TEST_F(SGFilterMSETest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = sg_filter_mse(NULL, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
    ret = sg_filter_mse(&kb_model, NULL, &params);
    ASSERT_EQ(-1, ret);
    ret = sg_filter_mse(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(-1, ret);        
}


TEST_F(SGFilterMSETest, return_value_passes)
{
    params.data[0] = (float)100;
    params.data[1] = (float)1130000;
    cols_to_use.data[0] = 1;
    num_cols = 1;

    ret = sg_filter_mse(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);
}

TEST_F(SGFilterMSETest, return_value_is_filtered)
{
    params.data[0] = (float)100;
    params.data[1] = (float)1130000;
    cols_to_use.data[0] = 0;
    num_cols = 1;

    ret = sg_filter_mse(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}
