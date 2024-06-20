//
//      test_stat_moment.cpp
//
//      Tests of the selection_contains() and selection_index() routines,
//      located in ../src/stat_moment.cpp
//


#include "gtest/gtest.h"
//#include "kbalgorithms.h"
#include "kb_typedefs.h"	// int16_t and FLOAT
#include "kbutils.h"		//
#include "rb.h"
#include "testdata_512.h"	// #cols = 1, #rows = 512, int16_t testdata[nR][nC]
#include <stdio.h>


#define	LONG_TEST 	1

#define	CLOSE_ENOUGH	0.00100	// I suppose that's close enough. . .
#define RB_SIZE 	32
#define TABLE_SIZE	8	//

//	These are test data which are intended to simulate 12-bit A/D Converter input.
//	As such, they are shown in 3-digit hexadecimal format.

static int table[TABLE_SIZE] =
    { 0x244, 0x561, 0xC76, 0x165, 0xA21, 0x020, 0xE40, 0x741 };

static ringb rb[1];
static int16_t buff[RB_SIZE + 4];


static void init_rb()
//
//	Initialize the ring buffer and load some data.
//
{
    int i;

    rb_init(rb, buff, RB_SIZE);

    for (i = 0; i < TABLE_SIZE; i++) {
	rb_add(rb, table[i]);
    }
}


//      
//      FLOAT stat_moment(ringb * rb, int base_index, int len, int moment)
//      



TEST(STAT_MOMENT_TEST, null_table_test)
//
//      Pass in a table of length 0.  See what happens.
//
{
    FLOAT ret;

    init_rb();

    // moment = 2, length = 0
    ret = stat_moment(rb, 0, 0, 2);
    ASSERT_EQ(0.0, ret);
}


TEST(STAT_MOMENT_TEST, one_point_test)
//
//	One data point, the moment equals 2.
//
{
    FLOAT ret;

    init_rb();

    // moment = 2, length = 1
    ret = stat_moment(rb, 0, 1, 2);
    ASSERT_EQ(0.0, ret);
}



TEST(STAT_MOMENT_TEST, one_cubed_test)
//
//	One data point, the moment equals 3.
{
    FLOAT ret;

    init_rb();

    // moment = 3, length = 0
    ret = stat_moment(rb, 0, 1, 3);
    ASSERT_EQ(0.0, ret);
}



#if LONG_TEST
TEST(STAT_MOMENT_TEST, generic_square_test)
//
//	Finds the second moment, using our standard test setup.
//
{
    FLOAT ret;

    init_rb();

    // moment = 2, length = 8
    ret = stat_moment(rb, 0, 8, 2);

    ASSERT_NEAR(1.59767e+06, ret, CLOSE_ENOUGH*ret);
}

TEST(STAT_MOMENT_TEST, generic_cube_test)
//
//	Finds the third moment, using our standard test setup.
//
{
    FLOAT ret;

    init_rb();

    // moment = 3, length = 8
    ret = stat_moment(rb, 0, 8, 3);

    ASSERT_NEAR(343923136, ret, CLOSE_ENOUGH*ret);
}



TEST(STAT_MOMENT_TEST, generic_fourth_test)
//
//	Finds the fourth moment, using our standard test setup.
//
{
    FLOAT ret;

    init_rb();

    // moment = 4, length = 8
    ret = stat_moment(rb, 0, 8, 4);

    ASSERT_NEAR(4061914988544, ret, CLOSE_ENOUGH*ret);
}
#endif
