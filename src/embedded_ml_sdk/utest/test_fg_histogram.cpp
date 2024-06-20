
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"  // int16_t
#include "rb.h"
#include "kb_common.h"    // kb_model_t
#include "kb_utest_init.h"


#define NUM_ROWS 50
#define NUM_INPUT_COLS 2
#define NUM_FG_OUTPUTS 10


static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {

	1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4,4, //column 1

	1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,3,3,3,3,3,3,3,3,3,3,4,4,4,4,4 // column 2
};


static float fg_one_col_outputs[NUM_FG_OUTPUTS] =  { 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 26.0f, 51.0f, 77.0f, 102.0f };
static float fg_two_col_outputs[NUM_FG_OUTPUTS] =  { 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 64.0f, 64.0f, 64.0f, 64.0f };


static int num_feature_selection = NUM_FG_OUTPUTS;

class FGHistogramTest : public testing::Test {
    protected:

    virtual void SetUp(){

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =0;
        sg_index = 0;
        sg_length = num_rows;
        ret=0;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);

        params.size =4;
        params.data[0] = 10.0f;
        params.data[1] = -5.0f;
        params.data[2] = 5.0f;
        params.data[3] = 255.0f;

        for (int i=0; i< num_feature_selection; i++){
                feature_selection[i] = i;
        }

    }

};

TEST_F(FGHistogramTest, kb_model_NULL_param_test) {
    // kb_model is NULL
    ret = fg_fixed_width_histogram(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHistogramTest, num_cols_zero_param_test) {
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = fg_fixed_width_histogram(&kb_model, &cols_to_use, &params, pFV);
    cols_to_use.size = 1;
    ASSERT_EQ(0, ret);
}

TEST_F(FGHistogramTest, cols_to_use_NULL_param_test) {
    // cols_to_use = NULL test, expect 0 as return value
    ret = fg_fixed_width_histogram(&kb_model, NULL, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHistogramTest, pFV_NULL_param_test) {
    // pFV = NULL test, expect 0 as return value
    ret = fg_fixed_width_histogram(&kb_model, &cols_to_use, &params, NULL);
    ASSERT_EQ(0, ret);
}

TEST_F(FGHistogramTest, return_number_of_cols_test) {
    ret = fg_fixed_width_histogram(&kb_model, &cols_to_use, &params, pFV);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
}

TEST_F(FGHistogramTest, return_value_one_cols_test) {
    cols_to_use.size = 1;

ret = fg_fixed_width_histogram(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i=0; i<NUM_FG_OUTPUTS; i++) {
        ASSERT_EQ(fg_one_col_outputs[i], pFV[i]);
    }
}

TEST_F(FGHistogramTest, return_value_two_cols_test) {
    cols_to_use.size = 2;

    ret = fg_fixed_width_histogram(&kb_model, &cols_to_use, &params, pFV);
    // fg computation test, expects an array of outputs
    int i;
    for (i=0; i<NUM_FG_OUTPUTS; i++) {
        ASSERT_EQ(fg_two_col_outputs[i], pFV[i]);
    }
}
