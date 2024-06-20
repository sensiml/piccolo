#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"
#include "sindata_512.h"
#include "sindata_512_with_noise.h"
#include "test_data_400.h"

#define NUM_ROWS 512
#define NUM_INPUT_COLS 1
#define NUM_FG_OUTPUTS 1

static float fg_outputs[NUM_FG_OUTPUTS] = {0.371815945};
static float fg_outputs_sin_with_noise[NUM_FG_OUTPUTS] = {0.909471691};
static float fg_outputs_test_data[NUM_FG_OUTPUTS] = {0.0};

static float tolerance = 0.001f;

class FGSpectralEntropy : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =0;
        sg_index = 0;
        sg_length = num_rows;
        ret = 0;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512, num_cols, num_rows);
    }
};

TEST_F(FGSpectralEntropy, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_frequency_spectral_entropy(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSpectralEntropy, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = fg_frequency_spectral_entropy(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSpectralEntropy, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = fg_frequency_spectral_entropy(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSpectralEntropy, pFV_NULL_param_test)
{
    // pFV = NULL test, expect 0 as return value
    ret = fg_frequency_spectral_entropy(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGSpectralEntropy, return_number_of_cols_test)
{
    ret = fg_frequency_spectral_entropy(&kb_model, &cols_to_use, &params, pFV);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
}

/* Seeing some weird stuff, need some help to figure this one out
 */
TEST_F(FGSpectralEntropy, return_value_of_each_cols_test)
{

fg_frequency_spectral_entropy(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        EXPECT_NEAR(fg_outputs[i], pFV[i], tolerance);
    }
}

TEST_F(FGSpectralEntropy, return_value_of_each_col_with_noise)
{

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512_with_noise, num_cols, num_rows);
fg_frequency_spectral_entropy(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        EXPECT_NEAR(fg_outputs_sin_with_noise[i], pFV[i], tolerance);
    }
}

TEST_F(FGSpectralEntropy, return_value_of_each_col_with_test_data)
{

    init_kb_model(&kb_model, &rb[0], sg_index, 400, test_data_400, num_cols, num_rows);
    fg_frequency_spectral_entropy(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        //printf("%f\n", pFV[i]);
        EXPECT_NEAR(fg_outputs_test_data[i], pFV[i], tolerance);
    }
}
