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

/// This function is used to initalize the blank state of feature generators. See test_fg_stats_maximum.cpp for an example
//  of how it can be used


#define MAX_COLS 6
#define RB_SIZE 512  // since
#define MAX_FEATURE_VECTOR 128
#define MAX_PARAMS 10

static int16_t buff[MAX_COLS][RB_SIZE]; //The data buffer the ring buffer uses
static ringb rb[MAX_COLS]; // ring buffers
static kb_model_t kb_model; // model struct for storing ring buffer and segment info

static int16_t columns[MAX_COLS] = {0 ,1, 2, 3, 4, 5};  //
static int16_data_t cols_to_use = {.data=columns,
                                   .size=MAX_COLS};

static float params_arr[MAX_PARAMS]; // holds function parameter inputs
static float_data_t params = {.data=params_arr,
                              .size=MAX_PARAMS};
static float pFV[MAX_FEATURE_VECTOR]; // holds the feature vectors
static feature_bank_t feature_bank = {.bank_size=MAX_FEATURE_VECTOR,
                                    .filled_flag=false,
                                    .num_banks=1,
                                    .pFeatures=pFV};
static data_buffers_t data_buffer = {.data = rb,
                                .size = MAX_COLS};

static int sg_index; // start of segment in ring buffer
static int sg_length; // length of segment in ring buffer
static int num_rows; // number of rows in column in input data
static int num_cols; // number of column in input data
static int ret; // return value from data frame

static void init_rb(int16_t * rb_inputs, int num_cols, int num_rows) {
    int i,j;    
    memset(buff, 0, sizeof(int16_t) * MAX_COLS * RB_SIZE);
    memset(sortedData, 0, sizeof(int16_t) * RB_SIZE);
    for (i=0; i<num_cols; i++) {
        rb_init(&rb[i], buff[i], RB_SIZE);
        for (j=0; j<num_rows; j++) {
            rb_add(&rb[i], rb_inputs[i*num_rows+j]);
            //printf("%d, ", rb_inputs[i*num_rows+j]);
        }
        //printf("\n");
    }
}


static void init_kb_model(kb_model_t *kb_model, ringb *rb, int sg_index, int sg_length, int16_t * rb_inputs,  int num_cols, int num_rows) {
    memset(pFV, 0.0f, sizeof(FLOAT) * MAX_FEATURE_VECTOR);
    memset(params_arr, 0.0f, sizeof(FLOAT) * 10);

    init_rb(rb_inputs, num_cols, num_rows);
    kb_model->pdata_buffer = &data_buffer;    
    kb_model->sg_index = sg_index;
    kb_model->sg_length = sg_length;
    kb_model->pfeature_bank = &feature_bank;
    cols_to_use.size=num_cols;

}

/*
static void reset_vars()
{
    int i;

    memset(buff, 0, sizeof(short) * MAX_COLS * RB_SIZE);
    memset(pFV, 0, sizeof(FLOAT) * MAX_FEATURE_VECTOR);
    memset(params_arr, 0, sizeof(FLOAT) * MAX_PARAMS);

    cols_to_use.size = 0;
    params.size=0;

    for (i = 0; i < MAX_COLS; i++)
    {
        cols_to_use.data[i] = i;
    }

    kb_model.sg_index = 0;
    kb_model.sg_length = 0;
}
*/