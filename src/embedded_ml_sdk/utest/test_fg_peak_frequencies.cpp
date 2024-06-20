#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"
#include "sindata_512.h"
#include "sindata_512_with_noise.h"
#include <stdio.h>

#define NUM_ROWS 512
#define NUM_INPUT_COLS 1
#define NUM_FG_OUTPUTS 4

static float fg_outputs[NUM_FG_OUTPUTS] = {4.0, 0.0, 0.0, 0.0};
static float fg_outputs_noise[NUM_FG_OUTPUTS] = {4.0, 88.0, 94.0, 112.0};
//static float fg_outputs_noise_min_max[NUM_FG_OUTPUTS] = {14.0, 55.0, 59.0, 76.0};

class FGPeakFrequencies : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =6;
        sg_index = 0;
        sg_length = num_rows;
        ret = 0;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512, num_cols, num_rows);
        params.data[0] = 512.0f;
        params.data[1] = 0.0f;
        params.data[2] = 200.0f;
        params.data[3] = 0.0f;
        params.data[4] = 4.0;
        params.data[5] = 0.;
    }
};

TEST_F(FGPeakFrequencies, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_frequency_peak_frequencies(&kb_model, &cols_to_use, NULL, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPeakFrequencies, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = fg_frequency_peak_frequencies(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPeakFrequencies, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = fg_frequency_peak_frequencies(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPeakFrequencies, pFV_NULL_param_test)
{
    // pFV = NULL test, expect 0 as return value
    ret = fg_frequency_peak_frequencies(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGPeakFrequencies, return_value_of_each_cols_test)
{

    fg_frequency_peak_frequencies(&kb_model, &cols_to_use, &params,pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        printf("feature vector %f\n", pFV[i]);
        ASSERT_EQ(fg_outputs[i], pFV[i]);
    }
}

TEST_F(FGPeakFrequencies, return_value_of_each_col_with_noise)
{

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512_with_noise, num_cols, num_rows);
    params.data[0] = 512.0f;
    params.data[1] = 0.0f;
    params.data[2] = 200.0f;
    params.data[3] = 0.0f;
    params.data[4] = 4.0;
    params.data[5] = 0.;
    fg_frequency_peak_frequencies(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        printf("feature vector %f %f\n", pFV[i], fg_outputs_noise[i]);
        ASSERT_EQ(fg_outputs_noise[i], pFV[i]);
    }
}

TEST_F(FGPeakFrequencies, return_value_of_each_col_with_noise_min_max_freq)
{

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512_with_noise, num_cols, num_rows);
    params.data[0] = 512.0f;
    params.data[1] = 5.0f;
    params.data[2] = 80.0f;
    params.data[3] = 0.0f;
    params.data[4] = 4.0;
    params.data[5] = 0.;
    fg_frequency_peak_frequencies(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        printf("feature vector %f\n", pFV[i]); //fg_outputs_noise_min_max[i]);
        //ASSERT_EQ(fg_outputs_noise_min_max[i], pFV[i]);
    }
}
