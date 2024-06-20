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

static int16_t tr_segment_horizontal_scale_same_length_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    //all positive
    {0, 100, 1000, 2000, 1000, 100, 0, 100, 1000, 2000},

    //all negative
    {0, -100, -1000, -2000, -1000, -100, 0, -100, -1000, -2000},

    //mixture of positive and negative
    {0, -100, -1000, -2000, -1000, -100, 0, 100, 1000, 2000}};

static float tr_segment_horizontal_scale_half_outputs[NUM_INPUT_COLS][NUM_ROWS / 2] = {

    //all positive
    {0, 1250, 550, 75, 2000},

    //all negative
    {0, -1250, -550, -75, -2000},

    //mixture of positive and negative
    {0, -1250, -550, 75, 2000}};

static int16_t tr_segment_horizontal_scale_double_outputs[NUM_INPUT_COLS][NUM_ROWS * 2] = {

    //all positive
    {0, 47, 94, 478, 905, 1368, 1842, 1685, 1211, 764, 337, 79, 32, 15, 63, 194, 621, 1052, 1526, 2000},

    //all negative
    {0, -47, -94, -478, -905, -1368, -1842, -1685, -1211, -764, -337, -79, -32, -15, -63, -194, -621, -1052, -1526, -2000},

    //all negative
    {0, -47, -94, -478, -905, -1368, -1842, -1685, -1211, -764, -337, -79, -32, 15, 63, 194, 621, 1052, 1526, 2000}};

static float tr_segment_horizontal_scale_expand_outputs[NUM_INPUT_COLS][15] = {

    //all positive
    {0, 64, 357, 935, 1571, 1786, 1143, 550, 86, 22, 42, 164, 742, 1357, 2000},

    //all negative
    {0, -64, -357, -935, -1571, -1786, -1143, -550, -86, -22, -42, -164, -742, -1357, -2000},

    //mixture of positive and negative
    {0, -64, -357, -935, -1571, -1786, -1143, -550, -86, -22, 42, 164, 742, 1357, 2000}};

static float tr_segment_horizontal_scale_shrink_outputs[NUM_INPUT_COLS][7] = {

    //all positive
    {0, 550, 2000, 550, 0, 550, 2000},

    //all negative
    {0, -550, -2000, -550, 0, -550, -2000},

    //mixture of positive and negative
    {0, -550, -2000, -550, 0, 550, 2000}};

class TRHorizontalScaleTest : public testing::Test
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
        params.data[0] = sg_length; // new_length
        ret = 0;
    }
};

TEST_F(TRHorizontalScaleTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = tr_segment_horizontal_scale(NULL, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(TRHorizontalScaleTest, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(TRHorizontalScaleTest, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = tr_segment_horizontal_scale(&kb_model, NULL, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(TRHorizontalScaleTest, num_params_negative_param_test)
{

    params.size=10;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);
    params.size=1;
    ASSERT_EQ(-1, ret);
}

TEST_F(TRHorizontalScaleTest, return_value_of_tr_hz_scale_same_length)
{
    int new_length = 10;
    params.data[0] = (float)new_length;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);

    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < new_length; j++)
        {
            ASSERT_EQ(tr_segment_horizontal_scale_same_length_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data + i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRHorizontalScaleTest, return_value_of_tr_hz_scale_half_length)
{
    int new_length = 5;
    params.data[0] = (float)new_length;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);

    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < new_length; j++)
        {
            ASSERT_EQ(tr_segment_horizontal_scale_half_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data + i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRHorizontalScaleTest, return_value_of_tr_hz_scale_double_length)
{
    int new_length = 20;
    params.data[0] = (float)new_length;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < new_length; j++)
        {
            ASSERT_EQ(tr_segment_horizontal_scale_double_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data + i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRHorizontalScaleTest, return_value_of_tr_hz_scale_expand)
{

    int new_length = 15;
    params.data[0] = (float)new_length;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < new_length; j++)
        {
            ASSERT_EQ(tr_segment_horizontal_scale_expand_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data + i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRHorizontalScaleTest, return_value_of_tr_hz_scale_shrink)
{

    int new_length = 7;
    params.data[0] = (float)new_length;
    ret = tr_segment_horizontal_scale(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < new_length; j++)
        {
            ASSERT_EQ(tr_segment_horizontal_scale_shrink_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data + i, kb_model.sg_index + j));
        }
    }
}
