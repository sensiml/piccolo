#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_INPUT_COLS 3

#define TRIGGER_POSITIVE 0
#define TRIGGER_NEGATIVE 1
#define NO_TRIGGER 2

static int16_t rb_inputs[NUM_INPUT_COLS * NUM_ROWS] = {

    // all positive
    0,
    100,
    1000,
    2000,
    1000,
    100,
    0,
    100,
    1000,
    2000,

    // all negative
    0,
    -100,
    -1000,
    -2000,
    -1000,
    -100,
    0,
    -100,
    -1000,
    -2000,

    // all 1
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,

};

class SGFilterEnergyThresholdTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);

        params.size =3;
        params.data[0] = 100; // threshold
        params.data[1] = 0;   // comparison >
        params.data[2] = 0;   // delay
        ret = 0;
    }
};

TEST_F(SGFilterEnergyThresholdTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = sg_filter_energy_threshold(NULL, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterEnergyThresholdTest, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterEnergyThresholdTest, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = sg_filter_energy_threshold(&kb_model, NULL, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterEnergyThresholdTest, no_delay_no_backoff)
{
    params.data[0] = (float)100.; // threshold
    params.data[1] = (float)0.;   // backoff
    params.data[2] = (float)0.;   // delay
    num_cols = 1;

    cols_to_use.data[0] = TRIGGER_POSITIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = TRIGGER_NEGATIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterEnergyThresholdTest, no_delay_only_backoff)
{
    params.data[0] = (float)100.; // threshold
    params.data[1] = (float)1.;   // backoff
    params.data[2] = (float)0.;   // delay
    num_cols = 1;

    cols_to_use.data[0] = TRIGGER_POSITIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = TRIGGER_NEGATIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterEnergyThresholdTest, delay_and_backoff)
{
    params.data[0] = (float)100.; // threshold
    params.data[1] = (float)1.;   // backoff
    params.data[2] = (float)1.;   // delay
    num_cols = 1;

    cols_to_use.data[0] = TRIGGER_POSITIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = TRIGGER_POSITIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}
TEST_F(SGFilterEnergyThresholdTest, no_threshold_trigger)
{
    params.data[0] = (float)100.; // threshold
    params.data[1] = (float)1.;   // backoff
    params.data[2] = (float)1.;   // delay
    num_cols = 1;

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterEnergyThresholdTest, only_delay_no_backoff)
{
    params.data[0] = (float)100.; // threshold
    params.data[1] = (float)0.;   // backoff
    params.data[2] = (float)1.;   // delay
    num_cols = 1;

    cols_to_use.data[0] = TRIGGER_POSITIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = TRIGGER_POSITIVE;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = NO_TRIGGER;

    ret = sg_filter_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}