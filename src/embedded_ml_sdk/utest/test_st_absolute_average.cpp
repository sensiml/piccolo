
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"
#include "kb_common.h"
#include "st_streaming_init.h"
#include <stdio.h>


#define NUM_ROWS 10
#define NUM_INPUT_COLS 2
#define NUM_ST_OUTPUTS 1


// Specific to fg_transpose_signal
#define CUTOFF 3

static int16_t st_inputs[NUM_INPUT_COLS * NUM_ROWS] =  {
    3, -4, 5, -4, 3, -3, 4, -5, 4, -3,
    3, -5, 7, -6, 1, -1, 3, -5, 7, -6
};


static int16_t input_data[NUM_ST_OUTPUTS];


static int expected_num_ret_values = 1;
static int16_t expected_outputs[10] = {
    3, 4, 3, 4, 3, 4, 6, 1, 4, 6
};


class STAbsAverageTest : public testing::Test {

    protected:

    virtual void SetUp(){
        cols_to_use.data[0]=0;
        cols_to_use.data[1]=1;
        cols_to_use.size = NUM_INPUT_COLS;

        ret=0;

        for (int i=0; i< NUM_ST_OUTPUTS; i++){
            input_data[i] = 0;
        }
    }
};



TEST_F(STAbsAverageTest, generate_abs_average_test) {
    for (int i=0; i<NUM_ROWS; i++)
    {
        ret = st_sensor_abs_average(&st_inputs[i*2], &cols_to_use, input_data);
        ASSERT_EQ(expected_num_ret_values, ret);
        ASSERT_EQ(expected_outputs[i], input_data[0]);
    }

};
