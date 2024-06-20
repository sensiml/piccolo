
Feature Generators
==================
 
Let's look at an example of how we generate a new feature in the feature vector.
 
The function signature for feature generators issues
 
.. code-block:: C
 
    int function_name(kb_model_t * kb_model, int *cols_to_use, int num_cols, FLOAT* params, int num_params, FLOAT *pFV);
 
 
where the parameter definitions are
 
* kb_model_t: is kb_model for the model we are computing the feature generator on.
* num_cols defines the number of columns we are going to compute the features on
* cols_to_use: defines the index of cols that should be used to compute the sum
* params: defines the param that should be used, in this case this feature generator doesn’t use params
* num_params: defines the number of params that should be used
* pFV: This is a pointer to the feature vector array where the feature vector should be stored
 
Feature generators always add the features they generate to pFV and return the number of feature vectors that they added.
 
Let's look at an example of a simple feature generator such as fg_stats_sum.c Below is the code for creating a sum feature generator
 
.. code-block:: C
 
    #include "kbutils.h"
 
    int fg_stats_sum(kb_model_t * kb_model, int *cols_to_use, int num_cols, FLOAT* params, int num_params, FLOAT *pFV)
    {
        int icol;
 
        for(icol=0; icol < num_cols; icol++)
        {
            pFV[icol] = utils_buffer_sum(kb_model->pringb + cols_to_use[icol], kb_model->sg_index, kb_model->sg_length);
        }
        return num_cols;
    }
 
 
The utils_buffer_sum function is what is referred to internally as a buffer function. These functions perform common tasks that are used by many functions. They typically take a pointer to the ring buffer and instructions about where to start and how many samples to process
 
 
Util functions
```````````````
 
This function is the one referenced in the previous feature generator. There is a lot of room for improving the efficiency of these types of functions.  First let's look at how they perform currently.
 
.. code-block:: C
 
    int utils_buffer-sum(ringb * pringb, int base_index, int num_rows)
    {
        int sum = 0;
        int irow;
 
        for (irow = base_index; irow < num_rows+base_index; irow++)
        {
            sum +=  get_axis_data(pringb, irow);
        }
 
        return sum;
    }lu
 
The get_axis_data function is part of the API for the Ring buffer, see rb.h. It takes a pointer to the ring buffer and the index that we want to extract.  This is the typical way that we access the ring buffer. The ring buffer can also be directly accessed, which can improve performance. Another option is to copy data to the data_buffer from the ring buffer, so you can operate on a contiguous array.
