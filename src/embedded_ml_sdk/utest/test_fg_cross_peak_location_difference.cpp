#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_INPUT_COLS 2
#define NUM_INPUT_ROWS 10

static int16_t inputs[NUM_INPUT_COLS * NUM_INPUT_ROWS] = {
    0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
    10, 10, 10, 10, 10, 20, 20, 20, 20, 20};

class FGCrossPeakLocationDifferenceTest : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_INPUT_ROWS;
        sg_index = 0;
        sg_length = NUM_INPUT_ROWS;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, inputs, num_cols, num_rows);
        params.size =0;
        num_cols = 2;
        ret = 0;
    }
};

TEST_F(FGCrossPeakLocationDifferenceTest, median_difference_1_minus_2)
{
    printf("About To Run Test");
    cols_to_use.data[0] = 0; //use the first column
    cols_to_use.data[1] = 1; //use the first column

    ret = fg_cross_column_peak_location_difference(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(1, ret);
    float tolerance = 0.001f;

    EXPECT_NEAR(pFV[0], 4, tolerance);
}

TEST_F(FGCrossPeakLocationDifferenceTest, median_difference_2_minus_1)
{
    printf("About To Run Test");
    cols_to_use.data[0] = 1; //use the first column
    cols_to_use.data[1] = 0; //use the first column

    ret = fg_cross_column_peak_location_difference(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(1, ret);
    float tolerance = 0.001f;

    EXPECT_NEAR(pFV[0], -4, tolerance);
}