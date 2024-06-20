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
    3, 4, 5, 4, 3, 3, 4, 5, 4, 3,
    3, 5, 7, 6, 1, 1, 3, 5, 7, 6};

//static float expected_outputs[NUM_INPUT_COLS] = {
static int expected_num_ret_values = NUM_INPUT_COLS * NUM_FEATURE_SELECTIONS;
static float expected_outputs[NUM_INPUT_COLS * NUM_FEATURE_SELECTIONS] = {
    3.5f, 4.5f, 3.0f, 4.5f, 3.5f, 4.0f, 6.5f, 1.0f, 4.0f, 6.5f};

class FGSamplingDownSample : public testing::Test
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
    FGSamplingDownSample()
    {
        num_feature_selection = NUM_FEATURE_SELECTIONS;

        //feature_selection[NUM_FEATURE_SELECTIONS] = { 0, 1, 2, 3, 4 };
        for (int i = 0; i < num_feature_selection; i++)
        {
            feature_selection[i] = i;
        }
    }
};

TEST_F(FGSamplingDownSample, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_sampling_downsample(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSamplingDownSample, NULL_cols_to_use_param_test)
{
    ret = fg_sampling_downsample(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSamplingDownSample, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_sampling_downsample(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSamplingDownSample, NULL_feature_vector_test)
{
    ret = fg_sampling_downsample(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSamplingDownSample, generate_features_test)
{
    ret = fg_sampling_downsample(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(expected_num_ret_values, ret);
    float tolerance = 0.001f;
    if (ret == expected_num_ret_values)
    {
        int i;
        //printf("pFV[] = ");
        for (i = 0; i < expected_num_ret_values; i++)
        {
            //printf("%f ", pFV[i]);
            EXPECT_NEAR(pFV[i], expected_outputs[i], tolerance);
        }
        //printf("\n");
    }
}
