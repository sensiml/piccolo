#include "gtest/gtest.h"

#ifndef GLOBAL_DATA_STRUCTURES
#define SORTED_DATA_LENGTH 16384
int16_t sortedData[SORTED_DATA_LENGTH]; // some functions extern this variable
int sorted_data_len = SORTED_DATA_LENGTH;
int feature_selection[128];
#define GLOBAL_DATA_STRUCTURES
#endif

//extern uint8_t kb_log_level;
int main(int argc, char *argv[])
{
    //    kb_log_level = 0;
    //    kb_log_level++;
    testing::InitGoogleTest(&argc, argv);
    return RUN_ALL_TESTS();
}
