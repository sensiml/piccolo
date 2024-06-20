#include "gtest/gtest.h"
//#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t and FLOAT
#include "kbutils.h"     // mean()
#include "rb.h"
#include "testdata_512.h" // #cols = 1, #rows = 512, int16_t testdata[nR][nC]
#include <stdio.h>

#define NUM_INPUT_COLS 2
#define NUM_INPUT_ROWS 10
#define RB_SIZE 16

static int16_t inputs[NUM_INPUT_COLS][NUM_INPUT_ROWS] = {
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9},
    {10, 10, 10, 10, 10, 20, 20, 20, 20, 20}};

static int16_t buff[NUM_INPUT_COLS][NUM_ROWS];
static ringb rb[NUM_INPUT_COLS];

class UtilsBufferArgmaxTest : public testing::Test
{

protected:
    virtual void SetUp()
    {

        int i, j;

        for (i = 0; i < NUM_INPUT_COLS; i++)
        {
            rb_init(&rb[i], buff[i], RB_SIZE);

            for (j = 0; j < NUM_INPUT_ROWS; j++)
            {
                rb_add(&rb[i], inputs[i][j]);
            }
        }
    }
};

TEST_F(UtilsBufferArgmaxTest, argmax_test)
{
    {
        int ret;
        int base_index = 0;
        int length = 9;
        ringb *pringb = rb;

        // *rb = NULL test, expect to get 0
        ret = buffer_argmax(pringb, base_index, length);
        ASSERT_EQ(8, ret);

        length = 10;
        // *rb = NULL test, expect to get 0
        ret = buffer_argmax(pringb, base_index, length);
        ASSERT_EQ(9, ret);
    }
}

TEST_F(UtilsBufferArgmaxTest, argmax_test_head_tail_offset)
{
    {
        ringb *pringb = rb + 1;
        int base_index = 0;
        int length = 5;

        int ret;

        ret = buffer_argmax(pringb, base_index, length);
        ASSERT_EQ(0, ret);

        base_index = 5;
        ret = buffer_argmax(pringb, base_index, length);
        ASSERT_EQ(0, ret);

        base_index = 0;
        length = 10;
        ret = buffer_argmax(pringb, base_index, length);
        ASSERT_EQ(5, ret);
    }
}