#include "kb.h"
#include "kb_output.h"

char str_buffer[2048];

void sml_output_results(int model_index, int model_result)
{
    kb_sprint_model_result(model_index, str_buffer, false, false, false);
    printf("%s", str_buffer)
};

int32_t sml_recognition_run(int16_t *data, int num_sensors)
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
    // FILL_RUN_MODEL_CUSTOM
#endif
    return ret;
}

void setup()
{
    /// Initialize the model
    kb_model_init();
}

void loop()
{
    /// FILL the data buffer from your sensor and pass it to sml_recognition_run
    int16_t sensor_data[6];

    sml_recognition_run(sensor_data, 6);
}
