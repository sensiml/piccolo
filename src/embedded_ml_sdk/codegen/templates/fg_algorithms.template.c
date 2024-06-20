/*
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
*/




// author: c.knorowski
#include "rb.h"
#include "kb_typedefs.h"
#include "kb_common.h"
#include "kbalgorithms.h"

/* define size of sortedData - The extern sortedData is only declared but not defined */
#define RB_SIZE 32768 // max segment length
#define MAX_COLS 6    // matching setting in server/settings.py
#define MAX_PARAMS 10
static int16_t cols_to_use[MAX_COLS] = {0, 1, 2, 3, 4, 5};
static float params[MAX_PARAMS] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
static int16_data_t input_columns = {.data = cols_to_use,
                                     .size = MAX_COLS};
static float_data_t input_params = {.data = params,
                                    .size = MAX_PARAMS};

int16_t sortedData[RB_SIZE];
static int16_t buff[MAX_COLS][RB_SIZE]; // The data buffer the ring buffer uses
static int32_t sg_index;                // start of segment in ring buffer
static int32_t sg_length;               // length of segment in ring buffer
static int32_t num_rows;                // number of rows in column in input data
static int32_t num_cols;                // number of column in input data
static ring_buffer_t rb[MAX_COLS];      // ring buffers
static kb_model_t kb_model;             // model struct for storing ring buffer and segment info
static data_buffers_t data_buffer = {.data = rb,
                                     .size = MAX_COLS};

static void init_rb(int16_t *rb_inputs, int32_t num_cols, int32_t num_rows)
{
    int32_t i, j;
    memset(buff, 0, sizeof(int16_t) * MAX_COLS * RB_SIZE);
    memset(sortedData, 0, sizeof(int16_t) * RB_SIZE);
    for (i = 0; i < MAX_COLS; i++)
    {
        rb_init(&rb[i], buff[i], RB_SIZE);
        for (j = 0; j < num_rows; j++)
        {
            rb_add(&rb[i], rb_inputs[i * num_rows + j]);
        }
    }
}

static void init_kb_model(kb_model_t *kb_model, int16_t *rb_inputs, int32_t sg_length, int32_t num_cols, int32_t num_rows)
{

    init_rb(rb_inputs, num_cols, num_rows);
    kb_model->pdata_buffer = &data_buffer;
    kb_model->sg_index = 0;
    kb_model->sg_length = sg_length;
}
