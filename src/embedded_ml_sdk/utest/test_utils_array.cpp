#include "gtest/gtest.h"
#include "kb_typedefs.h" // int16_t and FLOAT
#include "kbutils.h"     // utils_array
#include <stdio.h>

#define NUM_ROWS 10

static int16_t buff[NUM_ROWS];
static int i;

static int16_t input_data[NUM_ROWS] = {2000, 6060, 7225, 5086, 1905, 382, 1249, 2913, 3302, 1921};
static int16_t input_data_with_negative[NUM_ROWS] = {2000, 6060, -7225, 5086, 1905, 382, 1249, 2913, 3302, 1921};
static int16_t input_data_large[NUM_ROWS] = {32700, 6060, 7225, 5086, 1905, 382, 1249, 2913, 3302, 1921};
static int16_t input_data_zeros[NUM_ROWS] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static int16_t input_data_max[NUM_ROWS] = {32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767};
static int16_t input_data_min[NUM_ROWS] = {-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768};
static int16_t input_data_max_min[NUM_ROWS] = {-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768};

static int16_t autoscale_negative_output[10] = {9070, 27483, -32767, 23066, 8639, 1732, 5664, 13211, 14975, 8712};
static int16_t remove_mean_output[10] = {-1204, 2856, 4021, 1882, -1299, -2822, -1955, -291, 98, -1283};
static int16_t autoscale_output[10] = {9070, 27483, 32767, 23066, 8639, 1732, 5664, 13211, 14975, 8712};
static int16_t autoscale_data_large[10] = {32767, 6072, 7239, 5096, 1908, 382, 1251, 2918, 3308, 1924};

static int16_t autoscale_data_zeros[10] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static int16_t autoscale_data_max[10] = {32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767, 32767};
static int16_t autoscale_data_min[10] = {-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768};
static int16_t autoscale_data_max_min[10] = {-32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768, -32768};

void init_array(int16_t *testdata)
{
    memset(buff, 0, sizeof(int16_t) * NUM_ROWS);
    for (i = 0; i < NUM_ROWS; i++)
    {
        buff[i] = testdata[i];
    }
}

TEST(REMOVE_MEAN_INT_CALCULATION_TEST, remove_mean_of_data_test)
{
    init_array(input_data);

    int length = 10;

    // test removing the mean of the first 10 vals of testdata[]
    remove_mean_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(remove_mean_output[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_data_test)
{
    init_array(input_data);

    int length = 10;

    // test autoscale of the first 10 vals of testdata[]
    autoscale_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {

        ASSERT_EQ(autoscale_output[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_large_data_test)
{
    //autoscale factor should be 1, so no scaling should take place
    init_array(input_data_large);

    int length = 10;

    autoscale_data_int(buff, length);
    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(autoscale_data_large[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_negative_test)
{
    init_array(input_data_with_negative);

    int length = 10;

    // test autoscale of the first 10 vals of testdata[]
    autoscale_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(autoscale_negative_output[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_zeros)
{
    init_array(input_data_zeros);

    int length = 10;

    // test autoscale of the first 10 vals of testdata[]
    autoscale_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(autoscale_data_zeros[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_data_max)
{
    init_array(input_data_max);

    int length = 10;

    // test autoscale of the first 10 vals of testdata[]
    autoscale_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(autoscale_data_max[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_negative_min)
{
    init_array(input_data_min);

    int length = 10;

    // test autoscale of the first 10 vals of testdata[]
    autoscale_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(autoscale_data_min[i], buff[i]);
    }
}

TEST(AUTOSCALE_INT_CALCULATION_TEST, autoscale_negative_max_min)
{
    init_array(input_data_max_min);

    int length = 10;

    // test autoscale of the first 10 vals of testdata[]
    autoscale_data_int(buff, length);

    for (i = 0; i < NUM_ROWS; i++)
    {
        ASSERT_EQ(autoscale_data_max_min[i], buff[i]);
    }
}
