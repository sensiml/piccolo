#include "gtest/gtest.h"
//#include "kbalgorithms.h"
#include "kb_typedefs.h"  // int16_t and FLOAT
#include "kbutils.h"      // sum()
#include "rb.h"
#include "testdata_512.h" // #cols = 1, #rows = 512, int16_t testdata[nR][nC]
#include <stdio.h>

#define RB_SIZE NUM_ROWS
#define	LONG_TEST 1

static ringb   rb[NUM_COLS];

#if LONG_TEST
static int16_t buff[NUM_COLS][NUM_ROWS];

static void init_rb() {
    int i, j;

    for (i=0; i<NUM_COLS; i++) {
        rb_init(&rb[i], buff[i], RB_SIZE);

        for (j=0; j<NUM_ROWS; j++) {
            rb_add(&rb[i], testdata[i][j]);
        }
    }
}
#endif
TEST(SUM_PARAMS_TEST, data_len_zero_test) {
    FLOAT ret;
    int   base_index = 0;
    int   length = 0;

    // len = 0 test, expect to get 0
    ret = sum(&rb[0], base_index, length);
    ASSERT_EQ(0, ret);
}

#if LONG_TEST
TEST(SUM_CALCULATION_TEST, sum_of_10_data_test) {
    init_rb();

    FLOAT ret;
    int   base_index = 0;
    int   length = 10;
    const FLOAT error_rate = 0.0001; // 0.01%
    const FLOAT exp = 32043.0;

    // test sum of the first 10 vals of testdata[]
    ret = sum(&rb[0], base_index, length);
    ASSERT_NEAR(exp, ret, error_rate);
}

TEST(SUM_CALCULATION_TEST, sum_of_100_data_test) {
    init_rb();

    FLOAT ret;
    int   base_index = 0;
    int   length = 100;
    const FLOAT error_rate = 0.0001; // 0.01%
    const FLOAT exp = 200000;

    // test sum of the first 100 vals of testdata[]
    ret = sum(&rb[0], base_index, length);
    ASSERT_NEAR(exp, ret, error_rate);
}

TEST(SUM_CALCULATION_TEST, sum_of_512_data_test) {
    init_rb();

    FLOAT ret;
    int   base_index = 0;
    int   length = 512;
    const FLOAT error_rate = 0.0001; // 0.01%
    const FLOAT exp = 1063102.0;

    // test sum of all 512 of testdata[]
    ret = sum(&rb[0], base_index, length);
    ASSERT_NEAR(exp, ret, error_rate);
}
#endif
