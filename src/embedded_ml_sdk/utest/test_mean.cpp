#include "gtest/gtest.h"
//#include "kbalgorithms.h"
#include "kb_typedefs.h"  // int16_t and FLOAT
#include "kbutils.h"      // mean()
#include "rb.h"
#include "testdata_512.h" // #cols = 1, #rows = 512, int16_t testdata[nR][nC]
#include <stdio.h>

#define RB_SIZE NUM_ROWS

static int16_t buff[NUM_COLS][NUM_ROWS];
static ringb   rb[NUM_COLS];

static void init_rb() {
    int i, j;

    for (i=0; i<NUM_COLS; i++) {
        rb_init(&rb[i], buff[i], RB_SIZE);

        for (j=0; j<NUM_ROWS; j++) {
            rb_add(&rb[i], testdata[i][j]);
        }
    }
}

TEST(MEAN_PARAMS_TEST, rb_ptr_NULL_test) {
    FLOAT ret;
    int   base_index = 0;
    int   length = 0;

    // *rb = NULL test, expect to get 0
    ret = mean(NULL, base_index, length);
    ASSERT_EQ(0, ret);
}

TEST(MEAN_PARAMS_TEST, data_len_zero_test) {
    FLOAT ret;
    int   base_index = 0;
    int   length = 0;

    // len = 0 test, expect to get 0
    ret = mean(&rb[0], base_index, length);
    ASSERT_EQ(0, ret);
}

TEST(MEAN_CALCULATION_TEST, mean_of_10_data_test) {
    init_rb();

    FLOAT ret;
    int   base_index = 0;
    int   length = 10;
    const FLOAT error_rate = 0.0001; // 0.01%
    const FLOAT exp = 3204.300049;

    // test mean of the first 10 vals of testdata[]
    ret = mean(&rb[0], base_index, length);
    ASSERT_NEAR(exp, ret, error_rate);
}

TEST(MEAN_CALCULATION_TEST, mean_of_100_data_test) {
    init_rb();

    FLOAT ret;
    int   base_index = 0;
    int   length = 100;
    const FLOAT error_rate = 0.0001; // 0.01%
    const FLOAT exp = 2000;

    // test mean of the first 100 vals of testdata[]
    ret = mean(&rb[0], base_index, length);
    ASSERT_NEAR(exp, ret, error_rate);
}

TEST(MEAN_CALCULATION_TEST, mean_of_512_data_test) {
    init_rb();

    FLOAT ret;
    int   base_index = 0;
    int   length = 512;
    const FLOAT error_rate = 0.0001; // 0.01%
    const FLOAT exp = 2076.371094;

    // test mean of all 512 of testdata[]
    ret = mean(&rb[0], base_index, length);
    ASSERT_NEAR(exp, ret, error_rate);
}
