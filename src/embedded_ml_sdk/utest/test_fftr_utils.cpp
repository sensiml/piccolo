
// NOTE: comment out the following line before committing!
#define GENERATE_EXPECTED_RESULTS

#include <stdio.h>

#include "gtest/gtest.h"
#include "fftr_utils.h"
#include "fft_testdata_1.h"
#include "fft_testdata_2.h"

#ifndef GENERATE_EXPECTED_RESULTS
#include "fft_expRes_noScaling_FULL_test.h"
#include "fft_expRes_noScaling_HALF_test.h"
#include "fft_expRes_scale_down_FULL_test.h"
#include "fft_expRes_scale_up_FULL_test.h"
#include "fft_expRes_remove_mean_scale_up_FULL_test.h"
#endif

// local constants:
#define MAX_ALLOWED_FLOAT_DIFF 0.001f

// local buffer:
static float fft_testdata[NUM_FFTR];

// local utilities:
static void loadTestData(const float *pSrc, int len)
{
    float *pDest = fft_testdata;

    while (len--)
    {
        *pDest++ = *pSrc++;
    }
}

#ifdef GENERATE_EXPECTED_RESULTS
#define STRBUF_LEN 128
static char strBuf[STRBUF_LEN];
static void dumpTestData(const char *tName)
{
    FILE *fp;
    float *pData = fft_testdata;
    char *fName = strBuf;
    float real, imag;
    int cnt = NUM_FFTR / 2;

    snprintf(strBuf, sizeof(strBuf), "fft_expRes_%s.h", tName);
    fp = fopen(fName, "w");
    ASSERT_TRUE(fp != NULL) << "Failed to write Expected Results to " << fName;
    if (fp)
    {
        fprintf(fp, "// Expected Results for fft_%s\n#\n", tName);
        fprintf(fp, "static const float fft_expRes_%s[%d] = \\\n{\n", tName, NUM_FFTR);
        while (cnt--)
        {
            real = *pData++;
            imag = *pData++;
            fprintf(fp, "    %.1f, %.1f,\n", real, imag);
        }
        fprintf(fp, "};\n");
        fclose(fp);
        printf("Expected Results written to %s.\n", fName);
    }
}
#else
static float getMaxDifference(const float *pExp)
{
    float *pRes = fft_testdata;

    float maxDiff = 0.0f;
    float diff;
    int cnt = NUM_FFTR;

    while (cnt--)
    {
        diff = (*pRes++ - *pExp++);
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
#endif

// ##################### PARAM TESTS ######################

TEST(FFTR_FL_PARAMS_TEST, input_data_NULL_test)
{
    struct compx *pRet;

    pRet = fftr_fl(NULL, NUM_FFTR);
    ASSERT_EQ(NULL, pRet);
}

TEST(FFTR_FL_PARAMS_TEST, len_TOO_LARGE_test)
{
    struct compx *pRet;

    pRet = fftr_fl(fft_testdata, NUM_FFTR + 1);
    ASSERT_TRUE(pRet != NULL);
}

TEST(FFTR_FL_PARAMS_TEST, len_TOO_SMALL_test)
{
    struct compx *pRet;

    pRet = fftr_fl(fft_testdata, 1);
    ASSERT_EQ(NULL, pRet);
}

TEST(FFTR_FL_PARAMS_TEST, len_NOT_EVEN_test)
{
    struct compx *pRet;

    pRet = fftr_fl(fft_testdata, NUM_FFTR - 1);
    ASSERT_TRUE(pRet != NULL);
}

// ##################### CALC TESTS ######################

TEST(FFTR_FL_CALC_TEST, noScaling_FULL_test)
{
    struct compx *pRet;

    loadTestData(fft_testdata_1, NUM_FFTR);
    pRet = fftr_fl(fft_testdata, NUM_FFTR);
    ASSERT_TRUE(pRet != NULL);

#ifdef GENERATE_EXPECTED_RESULTS
    dumpTestData("noScaling_FULL_test");
#else
    float maxDiff = getMaxDifference(fft_expRes_noScaling_FULL_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
#endif
}

TEST(FFTR_FL_CALC_TEST, noScaling_HALF_test)
{
    struct compx *pRet;

    loadTestData(fft_testdata_1, NUM_FFTR / 2);
    pRet = fftr_fl(fft_testdata, NUM_FFTR / 2);
    ASSERT_TRUE(pRet != NULL);

#ifdef GENERATE_EXPECTED_RESULTS
    dumpTestData("noScaling_HALF_test");
#else
    float maxDiff = getMaxDifference(fft_expRes_noScaling_HALF_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
#endif
}

TEST(FFTR_FL_CALC_TEST, scale_up_FULL_test)
{
    struct compx *pRet;

    loadTestData(fft_testdata_2, NUM_FFTR);
    pRet = fftr_fl_as(fft_testdata, NUM_FFTR);
    ASSERT_TRUE(pRet != NULL);

#ifdef GENERATE_EXPECTED_RESULTS
    dumpTestData("scale_up_FULL_test");
#else
    float maxDiff = getMaxDifference(fft_expRes_scale_up_FULL_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
#endif
}

TEST(FFTR_FL_CALC_TEST, scale_down_FULL_test)
{
    struct compx *pRet;
    float *pData = fft_testdata;
    int cnt = NUM_FFTR;

    loadTestData(fft_testdata_1, NUM_FFTR);
    while (cnt--)
    {
        *pData *= 1000.0f;
        pData++;
    }
    pRet = fftr_fl_as(fft_testdata, NUM_FFTR);
    ASSERT_TRUE(pRet != NULL);

#ifdef GENERATE_EXPECTED_RESULTS
    dumpTestData("scale_down_FULL_test");
#else
    float maxDiff = getMaxDifference(fft_expRes_scale_down_FULL_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
#endif
}

TEST(FFTR_FL_CALC_TEST, remove_mean_scale_up_FULL_test)
{
    struct compx *pRet;

    loadTestData(fft_testdata_2, NUM_FFTR);
    pRet = fftr_fl_rm_as(fft_testdata, NUM_FFTR);
    ASSERT_TRUE(pRet != NULL);

#ifdef GENERATE_EXPECTED_RESULTS
    dumpTestData("remove_mean_scale_up_FULL_test");
#else
    float maxDiff = getMaxDifference(fft_expRes_remove_mean_scale_up_FULL_test);
    ASSERT_PRED_FORMAT2(::testing::FloatLE, maxDiff, MAX_ALLOWED_FLOAT_DIFF);
#endif
}
