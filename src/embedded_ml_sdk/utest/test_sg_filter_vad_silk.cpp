

#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"
#include "vad_testdata.h" //this has one speech utterance only

static void reset_rb(int16_t * rb_inputs, int num_cols, int num_rows)
{
    memset(buff, 0, sizeof(int16_t) * MAX_COLS * RB_SIZE);
    int i,j;

    for (i=0; i<num_cols; i++) {
        rb_reset(&rb[i]);
        for (j=0; j<num_rows; j++) {
            rb_add(&rb[i], rb_inputs[i*num_rows+j]);
        }
    }

}
#define NUM_ROWS 480 //=30ms of data
#define NUM_INPUT_COLS 1

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = { 0 };

class SGFilterVadSILKTest : public testing::Test
{
protected:
    virtual void SetUp()
    {
        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        params.size =0;
        sg_index = 0;
        sg_length = num_rows;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);
        params.data[0] = 0;
        params.data[1] = 0;
        params.size =0;
        ret = 0;

        //init the vad segment
        sg_filter_vad_silk_init();
    }
};

TEST_F(SGFilterVadSILKTest, kb_model_NULL_param_test)
{
    sg_filter_vad_silk_init();

    // kb_model is NULL
    ret = sg_filter_vad_silk(NULL, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterVadSILKTest, num_cols_zero_param_test)
{
    sg_filter_vad_silk_init();

    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = sg_filter_vad_silk(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterVadSILKTest, cols_to_use_NULL_param_test)
{
    sg_filter_vad_silk_init();

    // cols_to_use = NULL test, expect 0 as return value
    ret = sg_filter_vad_silk(&kb_model, NULL, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterVadSILKTest, params_NULL_param_test)
{
    sg_filter_vad_silk_init();

    // pFV = NULL test, expect 0 as return value
    ret = sg_filter_vad_silk(&kb_model, &cols_to_use, NULL);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterVadSILKTest, wrong_num_params_param_test)
{
    sg_filter_vad_silk_init();

    // pFV = NULL test, expect 0 as return value
    ret = sg_filter_vad_silk(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

// Note: this has to detect no speech 
TEST_F(SGFilterVadSILKTest, return_value_of_each_cols_test)
{
    int16_t all_zeros[NUM_INPUT_COLS*NUM_ROWS] = { 0};
    reset_rb(all_zeros, NUM_INPUT_COLS, NUM_ROWS);

    sg_filter_vad_silk_init();

    params.data[0] = 9;   //threshold 
    params.data[1] = 15;  //buffer size
    params.size =2;
    ret = sg_filter_vad_silk(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

// Note: this has to detect speech 
TEST_F(SGFilterVadSILKTest, return_value_of_speech_detect)
{
    int count = 0;
    int speech_detect = 0;
    int vad_file_size = sizeof(vad_testdata)/sizeof(short);

    sg_filter_vad_silk_init();

    params.data[0] = 9; // threshold
    params.data[1] = 15; // buffer size
    params.size =2;
    

    while(speech_detect == 0)
    {
        reset_rb((int16_t *)&vad_testdata[count][0], NUM_INPUT_COLS, NUM_ROWS);
        speech_detect = sg_filter_vad_silk(&kb_model, &cols_to_use, &params);
        count += NUM_INPUT_COLS;
        if(count > vad_file_size )
            break;
    }

    ASSERT_EQ(1, speech_detect);
}

