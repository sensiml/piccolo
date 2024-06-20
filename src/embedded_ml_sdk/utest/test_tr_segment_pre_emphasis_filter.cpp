

#include "tr_pre_emphasis_filter_test_vectors.h"
#include "tr_pre_emphasis_filter_ground_truth.h"
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_INPUT_COLS 5
#define NUM_FG_OUTPUTS 5

class TRPreEmphasisFilterTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =0;
        sg_index = 0;
        sg_length = num_rows;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, tr_segment_pre_emphasis_filter_tv, num_cols, num_rows);
        params.data[0] = 0.97f; //test the min
        params.data[1] = 0.0f;
        params.size =2;
        ret = 0;
        cols_to_use.size=NUM_INPUT_COLS;
    }
};

TEST_F(TRPreEmphasisFilterTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = tr_segment_pre_emphasis_filter(NULL, &cols_to_use, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_pre_emphasis_filter(&kb_model, NULL, &params);
    ASSERT_EQ(0, ret);
    ret = tr_segment_pre_emphasis_filter(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(0, ret);
}


TEST_F(TRPreEmphasisFilterTest, wrong_num_params_param_test)
{
    params.size=1;
    // pFV = NULL test, expect 0 as return value
    ret = tr_segment_pre_emphasis_filter(&kb_model, &cols_to_use,
                                         &params);
    ASSERT_EQ(0, ret);

}

TEST_F(TRPreEmphasisFilterTest, return_number_of_cols_test)
{
    params.data[0] = 0.97f; //test the min
    params.data[1] = 0.0f;
    params.size =2;
    ret = tr_segment_pre_emphasis_filter(&kb_model, &cols_to_use, &params);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
}

TEST_F(TRPreEmphasisFilterTest, return_value_of_each_cols_test)
{

    params.data[0] = 0.97f; //test the min
    params.data[1] = 0.0f;
    params.size =2;
    ret = tr_segment_pre_emphasis_filter(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(NUM_INPUT_COLS, ret);
    // fg computation test, expects an array of outputs
    int i, j;
    for (i = 0; i < NUM_INPUT_COLS; i++)
    {
        for (j = 0; j < NUM_ROWS; j++)
        {
            ASSERT_EQ(tr_segment_pre_emphasis_filter_gt[i][j],
                      get_axis_data(kb_model.pdata_buffer->data+ i, kb_model.sg_index + j));
        }
    }
}
