#!/bin/bash
#Usage: run_build.sh $json

check_return_code() {
        #Check the return code of most recent calls.
        rc=$?;
        echo "LOG STOP";
        if [[ $rc != 0 ]]; then exit $rc; fi
}
inputs=$1
export TENSORFLOW_ROOT=/tflite-micro/

cat /codegen_files/execute.json

mount_point=`$1 | jq -r '.["mount_directory"]'`
project=`$1 | jq -r '.["application"]'`
kp_id=`$1 | jq -r '.["uuid"]'`
user=`$1 | jq -r '.["user_id"]'`
board=`$1 | jq -r '.["board"]'`
lib_bin=`$1 | jq -r '.["build_type"]'`
debug=`$1 | jq -r '.["debug_flag"]'`
version=`$1 | jq -r '.["version"]'`
awsaccess=`$1 | jq -r '.["aws_access"]'`
awssec=`$1 | jq -r '.["aws_sec"]'`
bucket_name=`$1 | jq -r '.["bucket_name"]'`
platform=`$1 | jq -r '.["platform"]'`
profile=`$1 | jq -r '.["profile_data"]'`
target=`$1 | jq -r '.["target"]'`
application=`$1 | jq -r '.["application"]'`
tags=`$1 | jq -r '.["tags"]'`
model_binary=`$1 | jq -r '.["model_binary"]'`
PLATFORM_FLAGS_2=`$1 | jq -r '.["platform_flags_2"]'`
optimized_kernel_dir=`$1 | jq -r '.["hardware_accelerator"]'`
toolchain=`$1 | jq -r '.["toolchain"]'`

export http_proxy=''
export https_proxy=''

# COPY FROM S3
echo $mount_point
echo $project
echo $kp_id
echo $user
echo $board
echo $lib_bin
echo $debug
echo $version
echo $profile
echo $target
echo $platform
echo $toolchain
echo $optimized_kernel_dir

if [[ $debug == "d" ]]; then
    SML_DEBUG_STRING="NO_DEBUGGING_NOW"
else
    SML_DEBUG_STRING="DEBUG"
fi

echo "$mount_point"

build_type=release


output_library_name="nnom.a"


generate_code(){

    echo """
import os
import sys

from tensorflow.keras.models import load_model
from nnom import generate_model
import pandas as pd

root_dir=sys.argv[1]
model_path=os.path.join(root_dir,'model')
x_test = pd.read_csv(os.path.join(root_dir, 'test.csv'))

model = load_model(model_path)

print(model)
input_shape=model.layers[0].input_shape 
reshape_to = [-1]+[x for x in input_shape[1:]]

features = x_test[[x for x in x_test.columns if 'gen_' in x]].values

# Reshape to match the model's input shape (excluding the batch dimension)
reshaped_features = features.reshape(reshape_to) 

generate_model(model, reshaped_features, name=os.path.join(root_dir, 'weights.h'))
""" > generate_model.py

    python generate_model.py /build/nnom/

}

ls
echo "CODEGEN FILES"
ls $mount_point

mkdir /build/nnom
cp -r $mount_point/* /build/nnom/
ls /build/nnom/
generate_code 
outfile=nnom_"$kp_id".zip

echo "NNOM BUILD DIR"
ls
cd /build/
mkdir libsensiml
mkdir libsensiml/nnom
cp -r /nnom/inc/* libsensiml/nnom/
cp /nnom/port/* libsensiml/nnom/
cp /nnom/src/core/* libsensiml/nnom/
cp -r /nnom/src/layers/*.c libsensiml/nnom/
mkdir libsensiml/nnom/layers
cp -r /nnom/src/layers/*.h libsensiml/nnom/layers/

cp /nnom/src/backends/* libsensiml/nnom/
cp nnom/weights.h libsensiml/nnom/
cp nnom/model.h5 libsensiml/


zip -r nnom.zip libsensiml
mv nnom.zip $mount_point/nnom.zip

chown $user:$user $mount_point/nnom.zip

if [ -z $bucket_name ]; then
echo "Done"
else
aws s3 cp $mount_point/nnom.zip s3://$bucket_name/$kp_id/nnom.zip
fi

ls -al $mount_point
exit $?

#We don't check this return value because it fails to set up some things, but still builds in the container.