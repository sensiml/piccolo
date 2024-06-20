//
//      test_ma_symmetric.cpp
//
//      Tests of the ma_symmetric routines, which has been
//      optimized by breaking it into two parts.  These are named
//      ma_symmetric_mm() and ma_symmetric_sum().
//
//      The target source is located in ../src/ma_symmetric.c.
//
//      Generally, we set up a test using some reasonable/standard
//      set of parameters to the function.  The test is then done,
//      and is compared to the "known good" results.  These were
//      generally obtained from the use of the original function.
//


#include "gtest/gtest.h"
//#include "kbalgorithms.h"
#include "kb_typedefs.h"	// int16_t and FLOAT
#include "kbutils.h"		//
#include "rb.h"
#include "testdata_512.h"	// #cols = 1, #rows = 512, int16_t testdata[nR][nC]
#include <stdio.h>


#define	LONG_TEST 	1

#define	CLOSE_ENOUGH	0.100	//
#define TABLE_SIZE	8	//
#define RB_SIZE         32

//      The ring buffer initialization stuff is intended to emulate
//      the input from a 12-bit A/D converter.  That is why we use hex constants.

static int table[TABLE_SIZE] =
    { 0x244, 0x561, 0xC76, 0x165, 0xA21, 0x020, 0xE40, 0x741 };

static ringb rb[1];
static int16_t buff[RB_SIZE + 4];

static FLOAT pFV[2];		// 0 and 1


static void init_rb()
//
//      This initializes and loads the ring buffer into a known state.
//      The data set is arbitrary.
//
{
    int i;

    rb_init(rb, buff, RB_SIZE);

    for (i = 0; i < TABLE_SIZE; i++) {
	rb_add(rb, table[i]);
    }
}




#if 0

//      The function under test:

int MA_Symmetric(ringb * pringb, int base_index, int nFrameLen,
		 int nWinSize, int nColToUse, int nSampleRate, int isAC,
		 int nFlagUseSampleRate, int nABSBeforSum,
		 int nABSAfterSum, int nFGName, FLOAT * pFV)
#endif


TEST(MA_SYMMETRIC_MM_TEST, window_1_test)
{
//
//      This tests one of the min/max functions.
//
//    case global_p2p_high_frequency_name:
//        *pFV = max - min;
//    case global_p2p_low_frequency_name:
//        *pFV = max - min;
//    case max_p2p_half_high_frequency_name:
//        *pFV = max - min;
//
//      window size = 4
//
    int ret;

    init_rb();
    ret = MA_Symmetric(rb, 0, 8,
		       1, 0, 1, 0,
		       0, 0, 0, global_p2p_high_frequency_name, pFV);

//  printf("===> %f\n",  *pFV);

    ASSERT_EQ(1, ret);
    ASSERT_NEAR(pFV[0], 1097.0, CLOSE_ENOUGH);
}



TEST(MA_SYMMETRIC_MM_TEST, window_2_test)
{
//
//      window size = 5
//
    int ret;

    // not_found_test, expect to get false

    ret = MA_Symmetric(rb, 0, 8,
		       2, 0, 1, 0,
		       0, 0, 0, global_p2p_low_frequency_name, pFV);

    ASSERT_EQ(1, ret);
    ASSERT_NEAR(pFV[0], 454.19995, CLOSE_ENOUGH);
}



TEST(MA_SYMMETRIC_MM_TEST, window_3_test)
{
//
//      window size = 6
//
    int ret;

    // found_test, expect to get true

    ret = MA_Symmetric(rb, 0, 8,
		       3, 0, 1, 0,
		       0, 0, 0, max_p2p_half_high_frequency_name, pFV);

    ASSERT_EQ(1, ret);
    ASSERT_NEAR(pFV[0], 182.428, CLOSE_ENOUGH);
}



#if LONG_TEST

TEST(MA_SYMMETRIC_SUM_TEST, window_1_test)
{
//
//    case absolute_area_high_frequency_name:
//        *pFV = sum_fv;
//    case absolute_area_low_frequency_name:
//        *pFV = sum_fv;
//    case total_area_low_frequency_name:
//        *pFV = fabs(sum_fv);
//    case total_area_high_frequency_name:
//        *pFV = sum_fv;
//
//      window size = 4
//

    int ret;

    ret = MA_Symmetric(rb, 0, 8,
		       1, 0, 1, 0,
		       0, 0, 0, absolute_area_high_frequency_name, pFV);

    ASSERT_NE(0, ret);
    ASSERT_NEAR(pFV[0], 10334.33, CLOSE_ENOUGH);
}



TEST(MA_SYMMETRIC_SUM_TEST, window_2_test)
{
//
//    case absolute_area_high_frequency_name:
//        *pFV = sum_fv;
//    case absolute_area_low_frequency_name:
//        *pFV = sum_fv;
//    case total_area_low_frequency_name:
//        *pFV = fabs(sum_fv);
//    case total_area_high_frequency_name:
//        *pFV = sum_fv;
//
//      window size = 5
//

    int ret;

    ret = MA_Symmetric(rb, 0, 8,
		       2, 0, 1, 0,
		       0, 0, 0, absolute_area_low_frequency_name, pFV);

    ASSERT_NE(0, ret);
    ASSERT_NEAR(pFV[0], 6790.600, CLOSE_ENOUGH);
}






TEST(MA_SYMMETRIC_SUM_TEST, window_3_test)
{
//
//    case absolute_area_high_frequency_name:
//        *pFV = sum_fv;
//    case absolute_area_low_frequency_name:
//        *pFV = sum_fv;
//    case total_area_low_frequency_name:
//        *pFV = fabs(sum_fv);
//    case total_area_high_frequency_name:
//        *pFV = sum_fv;
//
//      window size = 6
//

    int ret;

    ret = MA_Symmetric(rb, 0, 8,
		       3, 0, 1, 0,
		       0, 0, 0, total_area_low_frequency_name, pFV);

    ASSERT_NE(0, ret);
    ASSERT_NEAR(pFV[0],  3547.285, CLOSE_ENOUGH);
}




#endif
