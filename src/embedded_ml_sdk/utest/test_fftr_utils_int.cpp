
#include <stdio.h>

#include "gtest/gtest.h"
#include "fftr_utils.h"
#include "fft_testdata_1.h"
#include "fft_testdata_2.h"
#include "fft_expRes_int_noScaling_FULL_test.h"
#include "fft_expRes_int_noScaling_HALF_test.h"

// local constants:
#define MAX_ALLOWED_FLOAT_DIFF 0.001f

// local buffer:
static int16_t fft_testdata[NUM_FFTR];

// local utilities:
static void loadTestData(const float *pSrc, int len)
{
    int16_t *pDest = fft_testdata;

    while (len--)
    {
        *pDest++ = (int16_t)*pSrc++;
    }
}

static float getMaxDifference(const float *pExp)
{
    int16_t *pRes = fft_testdata;

    float maxDiff = 0.0f;
    float diff;
    int cnt = NUM_FFTR;

    while (cnt--)
    {
        diff = ((float)*pRes++ - *pExp++);
        if (diff < 0.0f)
        {
            diff *= -1.0;
        }
        if (diff > maxDiff)
        {
            maxDiff = diff;
        }
    }
    return maxDiff;
}

// ##################### PARAM TESTS ######################

TEST(FFTR_PARAMS_TEST, input_data_NULL_test)
{
    struct compx_int16_t *pRet;

    pRet = fftr(NULL, NUM_FFTR);
    ASSERT_EQ(NULL, pRet);
}

TEST(FFTR_PARAMS_TEST, len_TOO_LARGE_test)
{
    struct compx_int16_t *pRet;

    pRet = fftr(fft_testdata, NUM_FFTR + 1);
    ASSERT_TRUE(pRet != NULL);
}

TEST(FFTR_PARAMS_TEST, len_TOO_SMALL_test)
{
    struct compx_int16_t *pRet;

    pRet = fftr(fft_testdata, 1);
    ASSERT_EQ(NULL, pRet);
}

//  WE are going to allow even input, as it gets zeroed out anyway
//TEST(FFTR_PARAMS_TEST, len_NOT_EVEN_test) {
//    struct compx_int16_t *pRet;

//    pRet = fftr(fft_testdata, NUM_FFTR-1);
//    ASSERT_EQ(NULL, pRet);
//}

// ##################### CALC TESTS ######################

TEST(FFTR_CALC_TEST, noScaling_FULL_test)
{
    struct compx_int16_t *pRet;

    loadTestData(fft_testdata_1, NUM_FFTR);
    pRet = fftr(fft_testdata, NUM_FFTR);
    ASSERT_TRUE(pRet != NULL);

    float maxDiff = getMaxDifference(fft_expRes_int_noScaling_FULL_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
}

TEST(FFTR_CALC_TEST, noScaling_HALF_test)
{
    struct compx_int16_t *pRet;

    loadTestData(fft_testdata_1, NUM_FFTR / 2);
    pRet = fftr(fft_testdata, NUM_FFTR / 2);
    ASSERT_TRUE(pRet != NULL);

    float maxDiff = getMaxDifference(fft_expRes_int_noScaling_HALF_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
}
