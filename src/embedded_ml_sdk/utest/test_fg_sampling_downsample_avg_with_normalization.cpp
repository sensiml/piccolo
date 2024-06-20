#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_ROWS 10
#define NUM_INPUT_COLS 2
#define NUM_FG_OUTPUTS 3

// Specific to fg_sampling_downsample
#define NUM_FEATURE_SELECTIONS 5

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    3, 4, 5, 4, 3, 3, 4, 5, 4, 3, -1000, -1000, 0, 0, 1000, 1000, 2000, 2000, 5000, 5000};

//static float expected_outputs[NUM_INPUT_COLS] = {
static int expected_num_ret_values_col1 = 1 * NUM_FEATURE_SELECTIONS;
static float expected_outputs_col1[1 * NUM_FEATURE_SELECTIONS] = {
    0.0f, 255.0f, 0.0f, 255.0f, 0.0f};

static int expected_num_ret_values_col2 = 1 * NUM_FEATURE_SELECTIONS;
static float expected_outputs_col2[1 * NUM_FEATURE_SELECTIONS] = {
    0.0f, 42.5f, 85.0f, 127.5f, 255.0f};

class FGConvolutionAvg : public testing::Test
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
    FGConvolutionAvg()
    {
    }
};

TEST_F(FGConvolutionAvg, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_sampling_downsample_avg_with_normalization(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGConvolutionAvg, NULL_cols_to_use_param_test)
{
    ret = fg_sampling_downsample_avg_with_normalization(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGConvolutionAvg, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_sampling_downsample_avg_with_normalization(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGConvolutionAvg, NULL_feature_vector_test)
{
    ret = fg_sampling_downsample_avg_with_normalization(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGConvolutionAvg, generate_features_test_delta_less_255)
{
    printf("About To Run Test");
    cols_to_use.data[0] = 0; //use the first column
    num_cols = 1;
    ret = fg_sampling_downsample_avg_with_normalization(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(expected_num_ret_values_col1, ret);
    float tolerance = 0.001f;
    if (ret == expected_num_ret_values_col1)
    {
        int i;
        //printf("pFV[] = ");
        for (i = 0; i < expected_num_ret_values_col1; i++)
        {
            //printf("%f ", pFV[i]);
            EXPECT_NEAR(pFV[i], expected_outputs_col1[i], tolerance);
        }
        //printf("\n");
    }
}

TEST_F(FGConvolutionAvg, generate_features_test_delta_greater_255)
{
    printf("About To Run Test");
    cols_to_use.data[0] = 1; //use the second column
    num_cols = 1;
    ret = fg_sampling_downsample_avg_with_normalization(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(expected_num_ret_values_col2, ret);
    float tolerance = 0.001f;
    if (ret == expected_num_ret_values_col2)
    {
        int i;
        //printf("pFV[] = ");
        for (i = 0; i < expected_num_ret_values_col2; i++)
        {
            //printf("%f ", pFV[i]);
            EXPECT_NEAR(pFV[i], expected_outputs_col2[i], tolerance);
        }
        //printf("\n");
    }
}
