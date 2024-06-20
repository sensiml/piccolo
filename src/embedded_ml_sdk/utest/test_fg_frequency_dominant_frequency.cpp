#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"
#include "sindata_512.h"
#include "sindata_512_with_noise.h"

#define NUM_ROWS 512
#define NUM_INPUT_COLS 1
#define NUM_FG_OUTPUTS 1

static float fg_outputs[NUM_FG_OUTPUTS] = {4.0};

class FGDominantFrequency : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =1;
        sg_index = 0;
        sg_length = num_rows;
        ret = 0;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512, num_cols, num_rows);
        params.data[0] = 512.0f;
    }
};

TEST_F(FGDominantFrequency, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = fg_frequency_dominant_frequency(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGDominantFrequency, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = fg_frequency_dominant_frequency(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGDominantFrequency, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = fg_frequency_dominant_frequency(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGDominantFrequency, pFV_NULL_param_test)
{
    // pFV = NULL test, expect 0 as return value
    ret = fg_frequency_dominant_frequency(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGDominantFrequency, return_number_of_cols_test)
{
    ret = fg_frequency_dominant_frequency(&kb_model, &cols_to_use, &params, pFV);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
}

TEST_F(FGDominantFrequency, return_value_of_each_cols_test)
{

    fg_frequency_dominant_frequency(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        ASSERT_EQ(fg_outputs[i], pFV[i]);
    }
}

TEST_F(FGDominantFrequency, return_value_of_each_col_with_noise)
{

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, sindata_512_with_noise, num_cols, num_rows);
    params.data[0] = 512.0f;
    fg_frequency_dominant_frequency(&kb_model,&cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i = 0; i < NUM_FG_OUTPUTS; i++)
    {
        ASSERT_EQ(fg_outputs[i], pFV[i]);
    }
}
