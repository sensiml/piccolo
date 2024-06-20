#include "sensor_config.h"
#include "kb.h"



void sml_recognition_run(signed short *data, int num_sensors)
{

    int ret;
#if ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG
    // FILL_RUN_MODEL_MOTION
#endif //ENABLE_ACCEL || ENABLE_GYRO || ENABLE_MAG


#if ENABLE_AUDIO
    // FILL_RUN_MODEL_AUDIO
#endif //ENABLE_AUDIO

}
