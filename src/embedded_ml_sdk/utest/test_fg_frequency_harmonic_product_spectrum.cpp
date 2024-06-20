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
#define NUM_FG_OUTPUTS 51

//static float fg_outputs[NUM_FG_OUTPUTS];
//static float fg_outputs_noise[NUM_FG_OUTPUTS];
//static float fg_outputs_phps[2] = {4.0, 0.0};
//static float fg_outputs_noise_phps[2] = {4.0, 88.};

//static float fg_outputs_noise_min_max[NUM_FG_OUTPUTS] = {14.0, 55.0, 59.0, 76.0};

class FGHarmonicProductSpectrum : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size = 1;
        sg_index = 0;
        sg_length = num_rows;
        ret = 0;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512, num_cols, num_rows);
        params.data[0] = 6.0f;
        cols_to_use.size=1;
        cols_to_use.data[0]=0;
    }
};

TEST_F(FGHarmonicProductSpectrum, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_frequency_harmonic_product_spectrum(&kb_model, &cols_to_use, NULL, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHarmonicProductSpectrum, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = fg_frequency_harmonic_product_spectrum(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHarmonicProductSpectrum, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = fg_frequency_harmonic_product_spectrum(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHarmonicProductSpectrum, pFV_NULL_param_test)
{
    // pFV = NULL test, expect 0 as return value
    ret = fg_frequency_harmonic_product_spectrum(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHarmonicProductSpectrum, return_value_of_each_cols_test)
{
    params.data[0] = 5.0f;
    cols_to_use.size=1;
    cols_to_use.data[0]=0;
    fg_frequency_harmonic_product_spectrum(&kb_model, &cols_to_use, &params,pFV);
    // fg computation test, expects an array of outputs
    int i;
    printf("hps FV=["); 
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        printf("%f, ", pFV[i]);
        //ASSERT_EQ(fg_outputs[i], pFV[i]);
    }
    printf("]\n");

    printf("phps FV=["); 
    fg_frequency_peak_harmonic_product_spectrum(&kb_model, &cols_to_use, &params,pFV);    
    for (i = 0; i < 2; i++)
    {
        printf("%f,", pFV[i]);
        //ASSERT_EQ(fg_outputs_phps[i], pFV[i]);
    }    
    printf("]\n");
}


TEST_F(FGHarmonicProductSpectrum, peak_return_value_of_each_cols_test)
{
    params.data[0] = 5.0f;
    cols_to_use.size=1;
    cols_to_use.data[0]=0;
    // fg computation test, expects an array of outputs
    int i;

    printf("phps FV=["); 
    fg_frequency_peak_harmonic_product_spectrum(&kb_model, &cols_to_use, &params,pFV);    
    for (i = 0; i < 2; i++)
    {
        printf("%f,", pFV[i]);
        //ASSERT_EQ(fg_outputs_phps[i], pFV[i]);
    }    
    printf("]\n");
}

TEST_F(FGHarmonicProductSpectrum, return_value_of_each_col_with_noise)
{

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512_with_noise, num_cols, num_rows);
    params.data[0] = 6.0f;
    cols_to_use.size=1;
    cols_to_use.data[0]=0;

    fg_frequency_harmonic_product_spectrum(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    printf("hps FV=["); 
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        printf("%f,", pFV[i]);
        //ASSERT_EQ(fg_outputs_noise[i], pFV[i]);
    }
    printf("]\n");
}


TEST_F(FGHarmonicProductSpectrum, peak_return_value_of_each_col_with_noise)
{

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512_with_noise, num_cols, num_rows);
    params.data[0] = 6.0f;
    cols_to_use.size=1;
    cols_to_use.data[0]=0;

    printf("phps FV=["); 
    fg_frequency_peak_harmonic_product_spectrum(&kb_model, &cols_to_use, &params, pFV);
    for (int i = 0; i < 2; i++)
    {
        printf("%f,", pFV[i]);
        //ASSERT_EQ(fg_outputs_noise_phps[i], pFV[i]);
    }
    printf("]\n");
}
