#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kbutils.h"
#include <stdio.h>
#include "kb_utest_init.h"
//#include "kb_utest.h"

#define RB_SIZE 512 // must be larger than data length of each test input

#define NUM_COLS 3
#define NUM_ROWS_TEST1 8
#define NUM_ROWS_TEST2 12

static int16_t testdata1[NUM_COLS * NUM_ROWS_TEST1] = {
    1, -2, -3, 1, 2, 5, 2, -2,
    0, 9, 5, -5, -9, 0, 9, 5,
    1, -2, 3, -1, 2, 5, 2, -2};


static float abs_area_outputs1[NUM_COLS][1] = {
    {0.37999},
    {0.0},
    {0.5400}};

static int16_t testdata2[NUM_COLS * NUM_ROWS_TEST2] = {
    -3, -1, 1, -3, -4, 1, 2, 6, 2, -3, -2, -1,
    -5, -9, 0, 9, 5, -5, -9, 0, 9, 5, -5, -9,
    -3, 1, 1, 3, 4, 1, 2, 6, 2, -3, -2, -1};

static float abs_area_outputs2[NUM_COLS][1] = {
    {0.86},
    {0.0},
    {1.46}};

class FGTAreaAbsoluteAreaLowFrequency : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_COLS;
        num_rows = NUM_ROWS_TEST1;
        sg_index = 0;
        sg_length = num_rows;
        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, testdata1, num_cols, num_rows);
        params.size =0;        
        ret = 0;
    }
};

TEST_F(FGTAreaAbsoluteAreaLowFrequency, ring_size_vs_test_data_len_test)
{
    ASSERT_GT(RB_SIZE, NUM_ROWS_TEST1);
    ASSERT_GT(RB_SIZE, NUM_ROWS_TEST2);
}

TEST_F(FGTAreaAbsoluteAreaLowFrequency, kb_model_NULL_test)
{
    int ret = fg_area_absolute_area_low_frequency(NULL, &cols_to_use, &params, pFV);

    ASSERT_EQ(0, ret);
}

TEST_F(FGTAreaAbsoluteAreaLowFrequency, num_cols_zero_test)
{


    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size=0;
    int ret = fg_area_absolute_area_low_frequency(&kb_model, &cols_to_use, &params, pFV);

    ASSERT_EQ(ret, 0);
}

TEST_F(FGTAreaAbsoluteAreaLowFrequency, cols_to_use_NULL_test)
{

    cols_to_use.size = 0; // test, expect 0 as return value
    int ret = fg_area_absolute_area_low_frequency(&kb_model, NULL, &params, pFV);

    ASSERT_EQ(ret, 0);
}

TEST_F(FGTAreaAbsoluteAreaLowFrequency, pFV_NULL_test)
{
      int ret = fg_area_absolute_area_low_frequency(&kb_model, &cols_to_use, &params, NULL);

    ASSERT_EQ(ret, 0);
}

TEST_F(FGTAreaAbsoluteAreaLowFrequency, calculation_dataset1_test)
{
    //cols_to_use.data[NUM_COLS] = { 2, 0, 1 };
    cols_to_use.size = NUM_COLS;
    params.size =2;
    params.data[0] = 10; // sample rate
    params.data[1] = 2;  //


    int ret = fg_area_absolute_area_low_frequency(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(ret, num_cols);

    // abs_sum computation test, expects an array of outputs
    int i;
    for (i = 0; i < ret; i++)
    {
        //printf("pFV[%d] = %f\n", i, pFV[i]);
        EXPECT_NEAR(abs_area_outputs1[cols_to_use.data[i]][0], pFV[i], 0.0001);
    }
}

TEST_F(FGTAreaAbsoluteAreaLowFrequency, calculation_dataset2_test)
{
    

    init_kb_model(&kb_model, &rb[0], 0, NUM_ROWS_TEST2, testdata2, NUM_COLS, NUM_ROWS_TEST2);
    cols_to_use.data[0] = 0;
    cols_to_use.data[1] = 1;
    cols_to_use.data[2] = 2;
    cols_to_use.size = NUM_COLS;
    params.size =2;
    params.data[0] = 10; // sample rate
    params.data[1] = 2;  // ??
    
    int ret = fg_area_absolute_area_low_frequency(&kb_model, &cols_to_use, &params, pFV);
    ASSERT_EQ(ret, num_cols);

    // abs_sum computation test, expects an array of outputs
    int i;
    for (i = 0; i < ret; i++)
    {
        //printf("pFV[%d] = %f\n", i, pFV[i]);
        EXPECT_NEAR(abs_area_outputs2[cols_to_use.data[i]][0], pFV[i], 0.0001);
    }
}
