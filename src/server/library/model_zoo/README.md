## To Add a new foundation Model

1. create a file with your model name ie. (mfcc23x49_w480_d320_dscnn_v02.py)
2. This file should have train, load, upload functions

   - Train - Description of training process for this model
   - Load - Load model into local model zoo
   - upload - Upload model to foundation model store

3. Train your model and save it using the "load" function into the local model store
4. Commit the locally created model store to the repo (using git lfs)
5. Add your model to the create_foundation_models.py file so it is loaded as part of the server setup scripts
6. Profile your model using the model_profile.py function and add its information to the upload

## To add Auxiliary Data Files for a foundation model

1. Add the .csv to library/model_zoo/auxilary_data
2. Add the name of the file to "auxiliary_datafile" key in the model info
