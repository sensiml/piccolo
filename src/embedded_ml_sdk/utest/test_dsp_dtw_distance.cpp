#include <stdio.h>
#include "gtest/gtest.h"

#include "kb_typedefs.h" 
#include "kb_opt.h"      


#define PATTERN_SIZE 6 

static uint8_t pattern_1[PATTERN_SIZE] ={ 0, 0, 0, 0, 0, 0 };

static int16_t expected_distance_1[PATTERN_SIZE][PATTERN_SIZE] ={
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0 },
    { 0, 0, 0, 0, 0, 0 },

};

static uint8_t pattern_2[PATTERN_SIZE] ={ 0, 10, 0, 20, 0, 30 };

static int16_t expected_distance_2[PATTERN_SIZE][PATTERN_SIZE] ={
    { 0, 100, 0, 400, 0, 900 },
    { 0, 100, 0, 400, 0, 900 },
    { 0, 100, 0, 400, 0, 900 },
    { 0, 100, 0, 400, 0, 900 },
    { 0, 100, 0, 400, 0, 900 },
    { 0, 100, 0, 400, 0, 900 },

};


static int16_t expected_distance_2_channel_pattern_2[PATTERN_SIZE/2][PATTERN_SIZE/2] ={
    { 100, 400, 900 },
    { 100, 400, 900 },
    { 100, 400, 900 },
};

class DTWdistanceTest : public testing::Test
{

protected:
    virtual void SetUp()
    {

    }
};

TEST_F(DTWdistanceTest, compute_distance_matrix_same_pattern)
{
    compute_distance_matrix(pattern_1, pattern_1, PATTERN_SIZE, PATTERN_SIZE, 1);

    for (int i=0; i<PATTERN_SIZE; i++)
    {
        for (int j=0; j<PATTERN_SIZE; j++)
        {
            ASSERT_EQ(get_distance_matrix_value(i, j), expected_distance_1[i][j]);
        }
    }

}


TEST_F(DTWdistanceTest, compute_distance_matrix_different_pattern)
{
    compute_distance_matrix(pattern_1, pattern_2, PATTERN_SIZE, PATTERN_SIZE, 1);

    for (int i=0; i<PATTERN_SIZE; i++)
    {
        for (int j=0; j<PATTERN_SIZE; j++)
        {
            ASSERT_EQ(get_distance_matrix_value(i, j), expected_distance_2[i][j]);
        }
    }

}




TEST_F(DTWdistanceTest, compute_warping_distance_different_pattern)
{
    int ret =0;
    compute_distance_matrix(pattern_1, pattern_2, PATTERN_SIZE, PATTERN_SIZE, 1);
    ret = compute_warping_distance(PATTERN_SIZE, PATTERN_SIZE);

    ASSERT_EQ(ret, 1400);

}



TEST_F(DTWdistanceTest, compute_distance_matrix_same_pattern_2_channel)
{
    compute_distance_matrix(pattern_1, pattern_1, PATTERN_SIZE/2, PATTERN_SIZE/2, 2);

    for (int i=0; i<PATTERN_SIZE/2; i++)
    {
        for (int j=0; j<PATTERN_SIZE/2; j++)
        {
            ASSERT_EQ(get_distance_matrix_value(i, j), expected_distance_1[i][j]);
        }
    }

}


TEST_F(DTWdistanceTest, compute_distance_matrix_different_pattern_2_channel)
{
    compute_distance_matrix(pattern_1, pattern_2, PATTERN_SIZE/2, PATTERN_SIZE/2, 2);

    for (int i=0; i<PATTERN_SIZE/2; i++)
    {
        for (int j=0; j<PATTERN_SIZE/2; j++)
        {
            ASSERT_EQ(get_distance_matrix_value(i, j), expected_distance_2_channel_pattern_2[i][j]);
        }
    }

}




TEST_F(DTWdistanceTest, compute_warping_distance_different_pattern_2_channel)
{
    int ret =0;
    compute_distance_matrix(pattern_1, pattern_2, PATTERN_SIZE/2, PATTERN_SIZE/2, 2);
    ret = compute_warping_distance(PATTERN_SIZE/2, PATTERN_SIZE/2);

    ASSERT_EQ(ret, 1400);

}

