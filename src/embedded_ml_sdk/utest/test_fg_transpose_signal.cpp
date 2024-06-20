
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "rb.h"
#include "kb_common.h"
#include "kb_utest_init.h"
#include <stdio.h>

#define NUM_ROWS 10
#define NUM_INPUT_COLS 2
#define NUM_FG_OUTPUTS 2

// Specific to fg_transpose_signal
#define CUTOFF 3

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {
    3, 4, 5, 4, 3, 3, 4, 5, 4, 3,
    3, 5, 7, 6, 1, 1, 3, 5, 7, 6};

static float expected_outputs_col2[3] = {
    3.0f, 5.0f, 7.0f};

static float expected_outputs_2_cols_with_padding[24] = {
    3.0f, 4.0f, 5.0f, 4.0f, 3.0f, 3.0f, 4.0f, 5.0f, 4.0f, 3.0f, 3.0f, 3.0f, 3.0f, 5.0f, 7.0f, 6.0f, 1.0f, 1.0f, 3.0f, 5.0f, 7.0f, 6.0f, 6.0f, 6.0f};

class FGTransposeSignalTest : public testing::Test
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
        params.data[0] = CUTOFF;
        ret = 0;
    }
};

TEST_F(FGTransposeSignalTest, kb_model_NULL_param_test)
{
    ret = fg_transpose_signal(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTransposeSignalTest, NULL_cols_to_use_param_test)
{
    ret = fg_transpose_signal(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTransposeSignalTest, ZERO_num_cols_param_test)
{
   cols_to_use.size=0;
   ret  = fg_transpose_signal(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGTransposeSignalTest, NULL_feature_vector_test)
{
    ret = fg_transpose_signal(&kb_model, &cols_to_use, &params, NULL);
}

TEST_F(FGTransposeSignalTest, generate_features_features_col_2)
{

    cols_to_use.size = 1;
    cols_to_use.data[0] = 1;

    ret = fg_transpose_signal(&kb_model, &cols_to_use, &params, pFV);

    ASSERT_EQ(3, ret);
    float tolerance = 0.001f;
    if (ret == 3)
    {
        int i;
        // printf("pFV[] = ");
        for (i = 0; i < 3; i++)
        {
            // printf("%f ", pFV[i]);
            EXPECT_NEAR(pFV[i], expected_outputs_col2[i], tolerance);
        }
        // printf("\n");
    }
}

TEST_F(FGTransposeSignalTest, generate_features_features_2_cols_with_padding)
{

    num_cols = 2;
    cols_to_use.data[0] = 0;
    cols_to_use.data[1] = 1;
    params.data[0] = 12;

    ret = fg_transpose_signal(&kb_model, &cols_to_use, &params, pFV);

    ASSERT_EQ(24, ret);
    float tolerance = 0.001f;

    int i;
    // printf("pFV[] = ");
    for (i = 0; i < ret; i++)
    {
        printf("%d %f\n", i, pFV[i]);
        EXPECT_NEAR(pFV[i], expected_outputs_2_cols_with_padding[i], tolerance);
    }
    // printf("\n");
}
