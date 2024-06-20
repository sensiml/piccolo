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

static float tr_segment_scale_factor_std_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {1, 2, 3, 0, 0, 1, 1, 2, 1, 3},
    {-1, -1, -2, -3, -0, -2, -3, -1, 0, -1},
    {0, 0, 0, 0, -1, 1, -1, 0, 1, 0}};

static float tr_segment_scale_factor_median_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {0, 1, 2, 0, 0, 0, 1, 1, 0, 2},
    {0, 0, 1, 1, 0, 1, 2, 1, 0, 0},
    {-1, 1, -1, 1, 2, -2, 2, 0, -3, 1}};

static float tr_segment_scale_factor_scalar_half_outputs[NUM_INPUT_COLS][NUM_ROWS] = {
    {2696, 6837, 9286, 2519, 2441, 2921, 4757, 7001, 2975, 8576},
    {-3155, -3960, -5407, -9089, -1709, -5909, -9954, -5065, -2463, -4381},
    {3319, -3569, 2636, -4156, -7161, 5462, -7075, -1624, 9739, -5080}};

static float tr_segment_scale_factor_scalar_double_outputs[NUM_INPUT_COLS][NUM_ROWS] = {
    {
        10786,
        27350,
        32767,
        10078,
        9764,
        11684,
        19028,
        28006,
        11902,
        32767,
    },
    {
        -12620,
        -15840,
        -21630,
        -32768,
        -6838,
        -23638,
        -32768,
        -20262,
        -9854,
        -17526,
    },
    {
        13276,
        -14276,
        10544,
        -16624,
        -28646,
        21850,
        -28302,
        -6496,
        32767,
        -20320,
    }};

class TRSGScaleFactorTest : public testing::Test
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
        params.data[0] = 1;
        params.data[1] = 1;
        ret = 0;
    }
};

TEST_F(TRSGScaleFactorTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = tr_segment_scale_factor(NULL, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_scale_factor(&kb_model, NULL, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_scale_factor(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(TRSGScaleFactorTest, return_value_of_tr_segment_scale_factor_std)
{
    params.data[0] = 0;
    ret = tr_segment_scale_factor(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_scale_factor_std_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRSGScaleFactorTest, return_value_of_tr_segment_scale_factor_median)
{

    params.data[0] = 1;
    ret = tr_segment_scale_factor(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_scale_factor_median_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRSGScaleFactorTest, return_value_of_tr_segment_scale_factor_double)
{

    params.data[0] = 2;
    params.data[1] = 2.0f;
    ret = tr_segment_scale_factor(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);

    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {

            ASSERT_EQ(tr_segment_scale_factor_scalar_half_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRSGScaleFactorTest, return_value_of_tr_segment_scale_factor_half)
{

    params.data[0] = 2;
    params.data[1] = .5;
    ret = tr_segment_scale_factor(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_scale_factor_scalar_double_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}
