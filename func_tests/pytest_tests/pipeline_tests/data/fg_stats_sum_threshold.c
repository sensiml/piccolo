#include "kbalgorithms.h"

int32_t utils_threshold_sum(ringb *pringb, int base_index, int num_rows, int threshold)
{
    int32_t sum = 0.0;
    int irow;
    int16_t value = 0;

    sum = 0;

    for (irow = base_index; irow < num_rows + base_index; irow++)
    {
        value = get_axis_data(pringb, irow);
        if (value < threshold)
        {
            sum += value; // 16-bit elements, added to 32-bit accumulator
        }
    }

    return sum;
}

int fg_stats_sum_threshold(kb_model_t *kb_model, int16_data_t *cols_to_use, float_data_t *params, FLOAT *pFV)
{
    int icol;
    int threshold = (int)params->data[0];

    for (icol = 0; icol < cols_to_use->size; icol++)
    {
        pFV[icol] = (float)utils_threshold_sum(kb_model->pdata_buffer->data +cols_to_use->data[icol], kb_model->sg_index, kb_model->sg_length, threshold);
    }
    return cols_to_use->size;
}