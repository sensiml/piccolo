#include "sensor_stream.h"
#include "kb.h"
// FILL_USE_TEST_DATA

#ifdef SML_USE_TEST_DATA
#include "testdata.h"
int td_index = 0;
#endif // SML_USE_TEST_DATA

// Reference to sml_output_results which is found in main.cpp
void sml_output_results(uint16_t model, uint16_t classification);
void sml_recognition_run(signed short *data, int num_sensors)
{

    int ret;

#ifdef SML_USE_TEST_DATA
    ret = kb_run_model((int16_t *)&testdata[td_index++], TD_NUMCOLS, 0);
    if (td_index >= TD_NUMROWS)
    {
        td_index = 0;
    }
    if (ret >= 0)
    {
        sml_output_results(0, ret);
        kb_reset_model(0);
    }
#else

#if ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG
    // FILL_RUN_MODEL_MOTION
#endif // ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG

#if ENABLE_AUDIO
    // FILL_RUN_MODEL_AUDIO
#endif // ENABLE_AUDIO

#if !(ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG) && !(ENABLE_AUDIO)
    // FILL_RUN_MODEL_CUSTOM
#endif // ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG
#endif // SML_USE_TEST_DATA
}
