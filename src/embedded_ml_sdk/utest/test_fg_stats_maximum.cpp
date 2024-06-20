#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_INPUT_COLS 3
#define NUM_FG_OUTPUTS 3
static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    //all positive
    5393, 13675, 18572, 5039, 4882, 5842, 9514, 14003, 5951, 17153,

    //all negative
    -6310, -7920, -10815, -18178, -3419, -11819, -19908, -10131, -4927, -8763,

    //mixture of positive and negative
    6638, -7138, 5272, -8312, -14323, 10925, -14151, -3248, 19479, -10160};

static float fg_outputs[NUM_FG_OUTPUTS] = {
    18572.0,
    -3419.0,
    19479.0,
};

class FGMaximumTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =0;
        sg_index = 0;
        sg_length = num_rows;
        ret = 0;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);
    }
};

TEST_F(FGMaximumTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_stats_maximum(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_stats_maximum(&kb_model, NULL,&params, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_stats_maximum(&kb_model, &cols_to_use ,NULL, pFV);
    ASSERT_EQ(0, ret);    
}


TEST_F(FGMaximumTest, return_number_of_cols_test)
{
    cols_to_use.size = 3;
    ret = fg_stats_maximum(&kb_model, &cols_to_use, &params, pFV);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
}

TEST_F(FGMaximumTest, return_value_of_each_cols_test)
{

    fg_stats_maximum(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        ASSERT_EQ(fg_outputs[i], pFV[i]);
    }
}
