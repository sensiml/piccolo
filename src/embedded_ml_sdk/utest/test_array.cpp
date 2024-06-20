//
//	test_array.cpp
//
//	Tests of the selection_contains() and selection_index() routines,
//	located in ../src/array_contains.c.
//


#include "gtest/gtest.h"
//#include "kbalgorithms.h"
#include "kb_typedefs.h"  // int16_t and FLOAT
#include "kbutils.h"      // 
#include "rb.h"
#include "testdata_512.h" // #cols = 1, #rows = 512, int16_t testdata[nR][nC]
#include <stdio.h>


#define	LONG_TEST 	1

#define TABLE_SIZE	8			// 
static int table[TABLE_SIZE]		= { 0x44, 0x61, 0x76, 0x65, 0x21, 0x20, 0x40, 0x41};


#if 0

int selection_index(int feature, int num_feature_selection,
                    int *feature_selection)
#endif



TEST(ARRAY_BOOL_TEST, NULL_table_test) {
    bool ret;
    int   base_index = 0;

    // selection = NULL test, expect to get 0
    ret = selection_contains(0, base_index, NULL);
    ASSERT_EQ(true, ret);
}

TEST(ARRAY_BOOL_TEST, not_found_test) {
    bool ret;

    // not_found_test, expect to get false

    ret = selection_contains((int) 'C', TABLE_SIZE, table);
    ASSERT_EQ(false, ret);
}

TEST(ARRAY_BOOL_TEST, found_test) {
    bool ret;

    // found_test, expect to get true

    ret = selection_contains((int) 'A', TABLE_SIZE, table);
    ASSERT_EQ(true, ret);
}



#if LONG_TEST
TEST(ARRAY_FIND_TEST, fail_to_find_test) {

    int ret;

    ret = selection_index((int) 'Q', TABLE_SIZE, table); 
    ASSERT_EQ(-1, ret);
}

TEST(ARRAY_FIND_TEST, found_at_zero_test) {

    int ret;

    ret = selection_index((int) 'D', TABLE_SIZE, table); 
    ASSERT_EQ(0, ret);
}

TEST(ARRAY_FIND_TEST, not_at_zero_test) {

    int ret;

    ret = selection_index((int) 'v', TABLE_SIZE, table); 
    ASSERT_NE(0, ret);
}
#endif
