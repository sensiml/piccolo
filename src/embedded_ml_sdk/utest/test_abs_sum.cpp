#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_COLS 3

int16_t abs_sum_inputs[NUM_COLS* NUM_ROWS] = {
    //all positive
    5393, 13675, 18572, 5039, 4882, 5842, 9514, 14003, 5951, 17153,

    //all negative
    -6310, -7920, -10815, -18178, -3419, -11819, -19908, -10131, -4927, -8763,

    //mixture of positive and negative
    6638, -7138, 5272, -8312, -14323, 10925, -14151, -3248, 19479, -10160};

float abs_sum_outputs[NUM_COLS][1] = {
    {100024.0},
    {102190.0},
    {99646.0},
};

class FGAbsSum : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_COLS;
        num_rows = NUM_ROWS;
        cols_to_use.size= NUM_COLS;
        cols_to_use.data[0]=0;
        cols_to_use.data[1]=1;
        cols_to_use.data[2]=2;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, abs_sum_inputs, num_cols, num_rows);
        params.size =1;
        params.data[0] = 10;
        ret = 0;
    }
};

TEST_F(FGAbsSum, kb_model_NULL_test)
{

    ret = fg_stats_abs_sum(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_stats_abs_sum(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_stats_abs_sum(&kb_model, &cols_to_use, NULL, pFV);
    ASSERT_EQ(0, ret);
    ret = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);

}


TEST_F(FGAbsSum, return_number_of_cols_test)
{
    cols_to_use.size=2;
    cols_to_use.data[0] = 2;
    cols_to_use.data[0] = 0;
    cols_to_use.data[0] = 1;
    params.data[0] = 10; // sample rate
    params.size = 1; // sample rate

    ret = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, pFV);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(2, ret);
}

TEST_F(FGAbsSum, return_value_of_each_cols_test)
{
    cols_to_use.size=3;
    cols_to_use.data[0] = 0;
    cols_to_use.data[0] = 1;
    cols_to_use.data[0] = 2;
    params.data[0] = 10; // sample rate
    params.size = 0; // sample rate

    ret = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, pFV);

    // ret should be the value of num_cols
    ASSERT_EQ(num_cols, ret);

    // abs_sum computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_COLS; i++)
    {
        ASSERT_EQ(abs_sum_outputs[cols_to_use.data[i]][0], pFV[i]);
    }
}
#if 0
//This Test is used to profile different methods to replayce get_axis_data() function
TEST(ABS_SUM_CALCULATION_TEST, TEST_Fprofiling)
{
    int num_cols = NUM_COLS;
    int cols_to_use.data[NUM_COLS] = {2, 0, 1};
    FLOAT pFV[NUM_COLS];
    int params.size =0; // not being used by abs_sum
    FLOAT params.data[1];    // not being used by abs_sum

    int sg_base_index = 0;
    int sg_length = NUM_ROWS;
    int ret = 0;

    init_kb_model(&kb_model, &rb[0], sg_base_index, sg_length);

    for (int i = 0; i < 100000; i++)
    {
        ret = fg_stats_abs_sum(&kb_model, &cols_to_use, &params, pFV);
    }

    // ret should be the value of num_cols
    ASSERT_EQ(num_cols, ret);

    // abs_sum computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_COLS; i++)
    {
        ASSERT_EQ(abs_sum_outputs[cols_to_use.data[i]][0], pFV[i]);
    }
}
#endif