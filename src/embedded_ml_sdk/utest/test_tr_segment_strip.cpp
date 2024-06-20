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

static float tr_segment_strip_mean_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    //all positive
    {-4609, 3673, 8570, -4963, -5120, -4160, -488, 4001, -4051, 7151},

    //all negative
    {3909, 2299, -596, -7959, 6800, -1600, -9689, 88, 5292, 1456},

    //mixture of positive and negative
    {8139, -5637, 6773, -6811, -12822, 12426, -12650, -1747, 20980, -8659}};

static float tr_segment_strip_min_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    //all positive
    {511, 8793, 13690, 157, 0, 960, 4632, 9121, 1069, 12271},

    //all negative
    {13598, 11988, 9093, 1730, 16489, 8089, 0, 9777, 14981, 11145},

    //mixture of positive and negative
    {20961, 7185, 19595, 6011, 0, 25248, 172, 11075, 32767, 4163}};

static float tr_segment_strip_median_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {-2339, 5943, 10840, -2693, -2850, -1890, 1782, 6271, -1781, 9421},
    {3137, 1527, -1368, -8731, 6028, -2372, -10461, -684, 4520, 684},
    {11831, -1945, 10465, -3119, -9130, 16118, -8958, 1945, 24672, -4967}};

static float tr_segment_strip_zero_outputs[NUM_INPUT_COLS][NUM_ROWS] = {

    {0, 8282, 13179, -354, -511, 449, 4121, 8610, 558, 11760},
    {0, -1610, -4505, -11868, 2891, -5509, -13598, -3821, 1383, -2453},
    {0, -13776, -1366, -14950, -20961, 4287, -20789, -9886, 12841, -16798}};

class TRStripTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;
        cols_to_use.size=NUM_INPUT_COLS;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);

        params.size =1;
        params.data[0] = 1;
        ret = 0;
    }
};

TEST_F(TRStripTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = tr_segment_strip(NULL, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_strip(&kb_model, NULL, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_strip(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(0, ret);
}


TEST_F(TRStripTest, return_number_of_cols_test)
{

    cols_to_use.size=NUM_INPUT_COLS;
    ret = tr_segment_strip(&kb_model, &cols_to_use, &params);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_INPUT_COLS, ret);
}

TEST_F(TRStripTest, return_value_of_tr_segment_strip_min)
{

    cols_to_use.size=NUM_INPUT_COLS;
    params.data[0] = 0;
    
    ret = tr_segment_strip(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_strip_min_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}

TEST_F(TRStripTest, return_value_of_tr_segment_strip_mean)
{

    params.data[0] = 1;
ret = tr_segment_strip(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_strip_mean_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}



TEST_F(TRStripTest, return_value_of_tr_segment_strip_median)
{

    params.data[0] = 2;
ret = tr_segment_strip(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_strip_median_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}


TEST_F(TRStripTest, return_value_of_tr_segment_strip_zero)
{

    params.data[0] = 3;
    ret = tr_segment_strip(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_strip_zero_outputs[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}
