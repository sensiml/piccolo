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

static int16_t tr_segment_offset_factor_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {32000, 32100, 32767, 32767, 32767, 32100, 32000, 32100, 32767, 32767},
    {32000, 31900, 31000, 30000, 31000, 31900, 32000, 31900, 31000, 30000},
    {32000, 31900, 31000, 30000, 31000, 31900, 32000, 32100, 32767, 32767}};

class TRSegmentOffsetFactorTest : public testing::Test
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
        params.data[0] = 32000;
        ret = 0;
    }
};

TEST_F(TRSegmentOffsetFactorTest, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = tr_segment_offset_factor(NULL, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_offset_factor(&kb_model, NULL, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_offset_factor(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(0, ret);    
}

TEST_F(TRSegmentOffsetFactorTest, num_params_invalid_param_test)
{
    // num_params > 1 test, expect 0 as return value
    params.size=2;
    ret = tr_segment_offset_factor(&kb_model, &cols_to_use, &params);
    params.size=1;

    ASSERT_EQ(0, ret);
}
TEST_F(TRSegmentOffsetFactorTest, return_value_of_offset_with_postiive_overflow)
{
    ret = tr_segment_offset_factor(&kb_model, &cols_to_use, &params);

    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {

        for (j = 0; j < sg_length; j++)
        {
            printf("%d, ", get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
            ASSERT_EQ(tr_segment_offset_factor_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
        printf("},\n{");
    }
}