

#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 2
#define NUM_INPUT_COLS 2

int16_t rb_inputs[NUM_ROWS * NUM_INPUT_COLS] = {
    0,
    0,
    0,
    0};

class TestSTHighPassFilter : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =0;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);
        ret = 0;
    }
};

TEST_F(TestSTHighPassFilter, return_value_of_each_cols_test)
{

    float alpha = 0.97f; // test the min
    int16_t pSample[NUM_ROWS] = {1, 1};
    cols_to_use.size = 1;
    ret = streaming_high_pass_filter(rb, pSample, &cols_to_use, alpha);

    ASSERT_EQ(-1, ret);

    pSample[0] = 5;
    pSample[1] = 5;
    ret = streaming_high_pass_filter(rb, pSample, &cols_to_use, alpha);

    // printf("%d %d\n", pSample[0], pSample[1]);

    ASSERT_EQ(1, ret);
    ASSERT_EQ(pSample[0], 4);
    ASSERT_EQ(pSample[1], 5);

    pSample[0] = 15;
    pSample[1] = 15;
    ret = streaming_high_pass_filter(rb, pSample, &cols_to_use, alpha);

    // printf("%d %d\n", pSample[0], pSample[1]);
    ASSERT_EQ(pSample[0], 14);
    ASSERT_EQ(pSample[1], 15);

    ASSERT_EQ(1, ret);

    alpha = 0.0f; // test the min

    pSample[0] = 30;
    pSample[1] = 30;
    ret = streaming_high_pass_filter(rb, pSample, &cols_to_use, alpha);

    // printf("%d %d\n", pSample[0], pSample[1]);
    ASSERT_EQ(pSample[0], 14);
    ASSERT_EQ(pSample[1], 30);

    ASSERT_EQ(1, ret);

    alpha = 0.5f; // test the min

    pSample[0] = 10;
    pSample[1] = 10;
    ret = streaming_high_pass_filter(rb, pSample, &cols_to_use, alpha);

    // printf("%d %d\n", pSample[0], pSample[1]);
    ASSERT_EQ(pSample[0], 12);
    ASSERT_EQ(pSample[1], 10);

    ASSERT_EQ(1, ret);
}
