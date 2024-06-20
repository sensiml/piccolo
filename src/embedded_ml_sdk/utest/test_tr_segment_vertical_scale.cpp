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

static int16_t tr_vertical_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {0, 1638, 16383, 32766, 16383, 1638, 0, 1638, 16383, 32766},
    {0, -1638, -16383, -32766, -16383, -1638, 0, -1638, -16383, -32766},
    {0, -1638, -16383, -32766, -16383, -1638, 0, 1638, 16383, 32766}};

class TRVerticalScaleTest : public testing::Test
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
        ret = 0;
    }
};

TEST_F(TRVerticalScaleTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = tr_segment_vertical_scale(NULL, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_vertical_scale(&kb_model, NULL, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_vertical_scale(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(0, ret);

}


TEST_F(TRVerticalScaleTest, return_value_of_tr_hz_scale_same_length)
{
    ret = tr_segment_vertical_scale(&kb_model, &cols_to_use, &params);

    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {

        for (j = 0; j < sg_length; j++)
        {
            printf("%d, ", get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
            ASSERT_EQ(tr_vertical_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
        printf("},\n{");
    }
}