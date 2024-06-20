
#include "fg_mfcc_test_vectors.h"
#include "fg_mfcc_ground_truth.h"
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"  // int16_t
#include "rb.h"
#include "kb_common.h"    // kb_model_t
#include "kb_utest_init.h"


#define NUM_ROWS 400
#define NUM_INPUT_COLS 5 
#define NUM_FG_OUTPUTS 23 

static int num_feature_selection = 23;


class FGMFCCTest : public testing::Test {
    protected:
 
    virtual void SetUp(){

    num_cols = NUM_INPUT_COLS;
    num_rows = NUM_ROWS;
    params.size =0;
    sg_index = 0;
    sg_length = num_rows;
    
    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, fg_mfcc_tv, num_cols, num_rows);
    params.data[0] = 16000.0f; //test the min
    params.data[1] = 23.0f;
    num_params=2;
    ret=0;
    //set up the feature seleciton array to select all features from fg_mfcc
    for (int i=0; i< num_feature_selection; i++){
            feature_selection[i] = i;
    }

    }

};

TEST_F(FGMFCCTest, kb_model_NULL_param_test) {
    // kb_model is NULL
    ret = fg_frequency_mfcc(NULL, &cols_to_use, &params, pFV);
    ASSERT_EQ(0, ret);
}

TEST_F(FGMFCCTest, num_cols_zero_param_test) {
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = fg_frequency_mfcc(&kb_model, &cols_to_use, &params, pFV,num_feature_selection, feature_selection);
    ASSERT_EQ(0, ret);
}

TEST_F(FGMFCCTest, cols_to_use_NULL_param_test) {
    // cols_to_use = NULL test, expect 0 as return value
    ret = fg_frequency_mfcc(&kb_model, NULL, &params, pFV,num_feature_selection, feature_selection);
    ASSERT_EQ(0, ret);
}

TEST_F(FGMFCCTest, params_NULL_param_test) {
    // pFV = NULL test, expect 0 as return value
    ret = fg_frequency_mfcc(&kb_model, &cols_to_use,
                NULL, num_params, pFV,num_feature_selection, feature_selection);
    ASSERT_EQ(0, ret);
}

TEST_F(FGMFCCTest, wrong_num_params_param_test) {
    // pFV = NULL test, expect 0 as return value
    ret = fg_frequency_mfcc(&kb_model, &cols_to_use,
                params, 1,pFV);
    ASSERT_EQ(0, ret);

    ret = fg_frequency_mfcc(&kb_model, &cols_to_use,
                params, 3, pFV,num_feature_selection, feature_selection);
    ASSERT_EQ(0, ret);
}

TEST_F(FGMFCCTest, return_number_of_cols_test) {
    num_params=2;
    ret = fg_frequency_mfcc(&kb_model, cols_to_use, 1,
            &params, pFV);

    // return val test, expect to return number of cols passing in
    ASSERT_EQ(NUM_FG_OUTPUTS, ret);
}

TEST_F(FGMFCCTest, return_value_of_each_cols_test) {
    // fg computation test, expects an array of outputs
    int i, j;
    for (i=0; i<NUM_INPUT_COLS; i++)
    {
            cols_to_use.data[0] = i;
            ret = fg_frequency_mfcc(&kb_model, cols_to_use , 1,
                    &params, pFV);

            for (j=0; j<NUM_FG_OUTPUTS; j++) 
            {
                ASSERT_EQ(fg_mfcc_gt[i][j], pFV[j]);
            }
             
    memset(pFV, 0.0f, sizeof(FLOAT) * MAX_FEATURE_VECTOR);
    }

}

