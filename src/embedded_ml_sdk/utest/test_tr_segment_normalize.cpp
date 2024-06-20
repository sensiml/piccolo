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

static int16_t tr_segment_normalize_std_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {-18834, -16254, 6966, 32767, 6966, -16254, -18834, -16254, 6966, 32767},
    {18834, 16254, -6966, -32767, -6966, 16254, 18834, 16254, -6966, -32767},
    {1708, 155, -13821, -29350, -13821, 155, 1708, 3261, 17237, 32767}};

static int16_t tr_segment_normalize_median_outputs[NUM_INPUT_COLS][NUM_ROWS] = {
    {-12428, -10169, 10169, 32767, 10169, -10169, -12428, -10169, 10169, 32767},
    {12428, 10169, -10169, -32767, -10169, 10169, 12428, 10169, -10169, -32767},
    {799, -799, -15184, -31168, -15184, -799, 799, 2397, 16783, 32767}};

class TRSGNormalizeTest : public testing::Test
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
        params.data[0] = 1;
        ret = 0;
    }
};

TEST_F(TRSGNormalizeTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = tr_segment_normalize(NULL, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
}

TEST_F(TRSGNormalizeTest, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = tr_segment_normalize(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
}

TEST_F(TRSGNormalizeTest, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = tr_segment_normalize(&kb_model, NULL, &params);
    ASSERT_EQ(0, ret);
}

TEST_F(TRSGNormalizeTest, return_number_of_cols_test)
{
    ret = tr_segment_normalize(&kb_model, &cols_to_use, &params);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_INPUT_COLS, ret);
}

TEST_F(TRSGNormalizeTest, return_value_of_tr_segment_normalize_mean)
{
    params.data[0] = 0;
    ret = tr_segment_normalize(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            printf("%d, ", get_axis_data(kb_model.pdata_buffer->data + i, kb_model.sg_index + j));
            ASSERT_EQ(tr_segment_normalize_std_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data  + i, kb_model.sg_index + j));
        }
        printf("},\n{");
    }
}

TEST_F(TRSGNormalizeTest, return_value_of_tr_segment_normalize_median)
{

    params.data[0] = 1;
    ret = tr_segment_normalize(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            printf("%d, ", get_axis_data(kb_model.pdata_buffer->data  + i, kb_model.sg_index + j));

            ASSERT_EQ(tr_segment_normalize_median_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data  + i, kb_model.sg_index + j));
        }
        printf("},\n{");
    }
}
