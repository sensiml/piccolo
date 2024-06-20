#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h" // int16_t
#include "rb.h"
#include "kb_common.h" // kb_model_t
#include "kb_utest_init.h"

#define NUM_ROWS 10
#define NUM_INPUT_COLS 3

#define ALL_POSITIVE 0
#define ALL_NEGATIVE 1
#define ALL_ONE 2

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

class SGFilterPeakRatioEnergyThresholdTest : public testing::Test
{
protected:
    virtual void SetUp()
    {

        num_cols = NUM_INPUT_COLS;
        num_rows = NUM_ROWS;
        sg_index = 0;
        sg_length = num_rows;

        init_kb_model(&kb_model, &rb[0], sg_index, sg_length, rb_inputs, num_cols, num_rows);

        params.size = 5;
        params.data[0] = 100;  // continuous activation threshold
        params.data[1] = 0;    // lowest activation threshold
        params.data[2] = 9999; // minimum acceptable peak to average
        params.data[3] = 0;    // backoff
        params.data[4] = 0;    // delay
        ret = 0;
    }
};

TEST_F(SGFilterPeakRatioEnergyThresholdTest, kb_model_NULL_param_test)
{
    // kb_model is NULL
    ret = sg_filter_peak_ratio_energy_threshold(NULL, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, num_cols_zero_param_test)
{
    cols_to_use.size = 0; // test, expect 0 as return value
    cols_to_use.size = 0;
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, cols_to_use_NULL_param_test)
{
    // cols_to_use = NULL test, expect 0 as return value
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, NULL, &params);
    ASSERT_EQ(-1, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, no_delay_no_backoff)
{

    params.data[0] = 100;       // continuous activation threshold
    params.data[1] = 0;         // lowest activation threshold
    params.data[2] = 9999;      // minimum acceptable peak to average
    params.data[3] = (float)0.; // backoff
    params.data[4] = (float)0.; // delay
    num_cols = 1;

    cols_to_use.data[0] = ALL_POSITIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = ALL_NEGATIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, no_delay_only_backoff)
{
    params.data[0] = 100;       // continuous activation threshold
    params.data[1] = 0;         // lowest activation threshold
    params.data[2] = 9999;      // minimum acceptable peak to average
    params.data[3] = (float)1.; // backoff
    params.data[4] = (float)0.; // delay
    num_cols = 1;

    cols_to_use.data[0] = ALL_POSITIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = ALL_NEGATIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, delay_and_backoff)
{
    params.data[0] = 100;       // continuous activation threshold
    params.data[1] = 0;         // lowest activation threshold
    params.data[2] = 9999;      // minimum acceptable peak to average
    params.data[3] = (float)1.; // backoff
    params.data[4] = (float)1.; // delay
    num_cols = 1;

    cols_to_use.data[0] = ALL_POSITIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_POSITIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}
TEST_F(SGFilterPeakRatioEnergyThresholdTest, no_threshold_trigger)
{
    params.data[0] = 100;       // continuous activation threshold
    params.data[1] = 0;         // lowest activation threshold
    params.data[2] = 9999;      // minimum acceptable peak to average
    params.data[3] = (float)1.; // backoff
    params.data[4] = (float)1.; // delay
    num_cols = 1;

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, only_delay_no_backoff)
{
    params.data[0] = 100;       // continuous activation threshold
    params.data[1] = 0;         // lowest activation threshold
    params.data[2] = 9999;      // minimum acceptable peak to average
    params.data[3] = (float)0.; // backoff
    params.data[4] = (float)1.; // delay
    num_cols = 1;

    cols_to_use.data[0] = ALL_POSITIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    cols_to_use.data[0] = ALL_POSITIVE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(1, ret);

    cols_to_use.data[0] = ALL_ONE;

    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);

    ASSERT_EQ(0, ret);
}

TEST_F(SGFilterPeakRatioEnergyThresholdTest, test_peak_threshold)
{

    params.data[0] = 9999;       // continuous activation threshold
    params.data[1] = 0;          // lowest activation threshold
    params.data[2] = (float)0.5; // minimum acceptable peak to average
    params.data[3] = (float)0.;  // backoff
    params.data[4] = (float)0.;  // delay
    num_cols = 1;

    // pass minimum threshold, pass ratio
    cols_to_use.data[0] = ALL_ONE;
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(1, ret);

    // pass minimum threshold, NOT pass ratio
    cols_to_use.data[0] = ALL_ONE;
    params.data[2] = (float)2; // minimum acceptable peak to average
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(0, ret);

    // NOT pass minimum threshold, NOT pass ratio
    cols_to_use.data[0] = ALL_ONE;
    params.data[1] = 5;        // lowest activation threshold
    params.data[2] = (float)2; // minimum acceptable peak to average
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(0, ret);

    // NOT pass minimum threshold, pass ratio - positive signals
    cols_to_use.data[0] = ALL_POSITIVE;
    params.data[1] = 3000;     // lowest activation threshold
    params.data[2] = (float)2; // minimum acceptable peak to average
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(0, ret);

    // NOT pass minimum threshold, pass ratio - negative signal
    cols_to_use.data[0] = ALL_NEGATIVE;
    params.data[1] = 3000;     // lowest activation threshold
    params.data[2] = (float)2; // minimum acceptable peak to average
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(0, ret);

    // pass minimum threshold, NOT pass ratio
    cols_to_use.data[0] = ALL_NEGATIVE;
    params.data[1] = 1000;     // lowest activation threshold
    params.data[2] = (float)3; // minimum acceptable peak to average
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(0, ret);

    //  pass minimum threshold,  pass ratio
    cols_to_use.data[0] = ALL_POSITIVE;
    params.data[1] = 1999;       // lowest activation threshold
    params.data[2] = (float)2.7; // minimum acceptable peak to average
    ret = sg_filter_peak_ratio_energy_threshold(&kb_model, &cols_to_use, &params);
    ASSERT_EQ(1, ret);
}
