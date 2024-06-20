#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_ROWS 133
#define NUM_INPUT_COLS 1
#define NUM_FG_OUTPUTS 40

// Specific to fg_sampling_downsample
#define NUM_FEATURE_SELECTIONS 40

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    23284, 23284, 23284, 21564, 21564, 20374, 20374, 20291, 20291, 21265, 21265, 30337, 30337, 33050, 33050, 38478, 38478, 46342, 46342, 46168, 46168, 36145, 36145, 31038, 31038, 30450, 30450, 30110, 30110, 30431, 30431, 26129, 26129, 19330, 19330, 15369, 15369, 14052, 14052, 13900, 13900, 13524, 13524, 12190, 12190, 10367, 10367, 8897, 8897, 7981, 7981, 7299, 7299, 6580, 6580, 5773, 5773, 4977, 4977, 4317, 4317, 3754, 3754, 3229, 3229, 2827, 2827, 2562, 2562, 2430, 2430, 2227, 2227, 1998, 1998, 1745, 1745, 1417, 1417, 1030, 1030, 719, 719, 400, 400, 185, 185, 294, 294, 516, 516, 778, 1075, 1232, 1352, 1486, 1594, 1600, 1501, 1398, 1381, 1286, 1222, 1237, 1171, 1040, 971, 889, 825, 897, 821, 962, 1282, 1742, 2215, 2470, 2669, 3032, 3530, 4027, 4609, 5209, 5556, 5910, 6231, 6612, 7288, 7950, 8582, 8455, 7444, 6498, 6504};

//static float expected_outputs[NUM_INPUT_COLS] = {
static int expected_num_ret_values_col = 1 * NUM_FEATURE_SELECTIONS;
static float expected_outputs_col[1 * NUM_FEATURE_SELECTIONS] = {
    220.92f,
    211.12f,
    207.19f,
    225.57f,
    59.68f,
    0.00f,
    23.73f,
    70.31f,
    255.00f,
    253.01f,
    240.73f,
    196.50f,
    180.21f,
    176.89f,
    171.61f,
    158.85f,
    151.49f,
    145.80f,
    141.10f,
    135.15f,
    131.37f,
    127.45f,
    125.39f,
    124.06f,
    122.73f,
    120.69f,
    118.49f,
    115.96f,
    114.31f,
    114.83f,
    116.78f,
    119.40f,
    120.37f,
    119.40f,
    118.73f,
    117.60f,
    117.05f,
    119.27f,
    124.47f,
};

class FGConvolutionAvgLarge : public testing::Test
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
        params.data[0] = 5;
        ret = 0;
    }

    // Specific to fg_sampling_downsample
protected:
    int num_feature_selection;
    int feature_selection[NUM_FEATURE_SELECTIONS];

public:
    // Specific to fg_sampling_downsample
    FGConvolutionAvgLarge()
    {
        num_feature_selection = NUM_FEATURE_SELECTIONS;

        //feature_selection[NUM_FEATURE_SELECTIONS] = { 0, 1, 2, 3, 4 };
        for (int i = 0; i < num_feature_selection; i++)
        {
            feature_selection[i] = i;
        }
    }
};

TEST_F(FGConvolutionAvgLarge, generate_features_test_delta_less_255)
{
    printf("About To Run Test");
    cols_to_use.data[0] = 0; //use the first column
    num_cols = 1;
    ret = fg_sampling_downsample_avg_with_normalization(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(expected_num_ret_values_col, ret);
    float tolerance = 0.001f;
    if (ret == expected_num_ret_values_col)
    {
        int i;
        //printf("pFV[] = ");
        for (i = 0; i < expected_num_ret_values_col; i++)
        {
            //printf("%f ", pFV[i]);
            EXPECT_NEAR(pFV[i], expected_outputs_col[i], tolerance);
        }
        //printf("\n");
    }
}
