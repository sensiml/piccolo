
#include "fg_mfcc_test_vectors.h"
#include "fg_mfcc_ground_truth.h"
#include "gtest/gtest.h"
#include "kbalgorithms.h"
#include "kb_typedefs.h"  // int16_t
#include "rb.h"
#include "kb_common.h"    // kb_model_t
#include "kb_utest_init.h"


#define NUM_ROWS 512
#define NUM_INPUT_COLS 1


/*
Generated data
sample_rate = 16000
number_bins=512
Fres=sample_rate/number_bins

x = np.arange(number_bins)/sample_rate
f=7800
f2=1000
f3=2000
f5= 300
frequencies = [1000,2000,3000,4000,5000,6000,7000]
y = np.zeros(512)
for f in frequencies:
    y+=(np.sin(2*np.pi*x*f)*1000).astype(int)
",".join(["{}".format(x) for x in y.astype(int).tolist()])
*/
static int16_t data[NUM_ROWS] = {0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024,0,5024,0,1496,0,668,0,196,0,-196,0,-668,0,-1496,0,-5024};
static float expected_outputs_nbins_16[16] = {34.413029, 261.124451, 753.245178, 259.472137, 755.474182, 253.716339, 757.474182, 255.472137, 755.000000, 256.002014, 753.031982, 255.002014, 757.000000, 259.236053, 757.433105, 25.276249};
static float expected_outputs_nbins_32[32] = {24.934320, 9.478709, 5.650282, 255.474167, 751.245178, 2.000000, 2.000000, 257.472137, 753.238098, 2.236068, 2.236068, 251.480270, 752.002014, 5.472136, 3.236068, 252.236069, 753.000000, 2.000000, 3.000000, 253.002014, 752.031982, 1.000000, 1.000000, 254.002014, 755.000000, 2.000000, 2.000000, 257.236053, 753.018921, 4.414214, 8.478708, 16.797539};




class FGPowerSpectrumTest : public testing::Test {
    protected:

    virtual void SetUp(){

    num_cols = NUM_INPUT_COLS;
    num_rows = NUM_ROWS;
    params.size =0;
    sg_index = 0;
    sg_length = num_rows;

    init_kb_model(&kb_model, &rb[0], sg_index, sg_length, data, num_cols, num_rows);
    params.data[0] = 16; //num_bins
    params.data[1] = 0; //hanning window
    cols_to_use.size=1;
    params.size=2;
    ret=0;

    }

};


TEST_F(FGPowerSpectrumTest, compute_power_spectrum_16) {
    int i;

    cols_to_use.data[0] = 0;
    params.data[0]=16.;

    ret = fg_frequency_power_spectrum(&kb_model, &cols_to_use, &params, pFV);

    for (i=0; i<16;i++)
    {
        EXPECT_NEAR(expected_outputs_nbins_16[i], pFV[i], .001);
    }

    ASSERT_EQ(ret, 16);

};


TEST_F(FGPowerSpectrumTest, compute_power_spectrum_32) {
    int i;

    cols_to_use.data[0] = 0;
    params.data[0]=32.;
    params.data[1]=0.;
    params.size=2;

    ret = fg_frequency_power_spectrum(&kb_model, &cols_to_use, &params, pFV);

    for (i=0; i<32;i++)
    {
        EXPECT_NEAR(expected_outputs_nbins_32[i], pFV[i], .001);
    }

    ASSERT_EQ(ret, 32);

};
#if 0
//This Test is used to profile different methods to replayce get_axis_data() function
TEST_F(FGPowerSpectrumTest, test_profiling_3)
{
    int i;


    for(i=0; i< 2000; i++)
    {
        cols_to_use.data[0] = 0;
        params.data[0]=32.;
        params.data[1]=0.;

        ret = fg_frequency_power_spectrum(&kb_model, cols_to_use , 1,
                &params, pFV);
    }
#if 0
    for (i=0; i<32;i++)
    {
        EXPECT_NEAR(expected_outputs_nbins_32[i], pFV[i], .001);
    }

    ASSERT_EQ(ret, 32);
#endif
};
#endif