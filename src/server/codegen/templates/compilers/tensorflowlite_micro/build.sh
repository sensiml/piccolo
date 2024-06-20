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


output_library_name="libtensorflow-microlite.a"


generate_code(){
    cd ${TENSORFLOW_ROOT}/tensorflow/lite/micro/examples/model_runner/codegen/
    echo "LOG START"
    python codegen.py --model_json_path=$mount_point/execute.json
    check_return_code
    cd ${TENSORFLOW_ROOT}
    echo "LOG START"
    make  -f tensorflow/lite/micro/tools/make/Makefile  clean
    check_return_code
    echo $TENSORFLOW_ROOT
    ls
    echo "PLATFORM" $platform
    echo "TARGET ARCH" $target
    echo "LOG START"

    make_params=(TARGET_ARCH=$target
                TARGET=$platform
                BUILD_TYPE=$build_type
                SKIP_PIGWEED_DOWNLOAD=true
                SKIP_COMPILER_DOWNLOAD=true
                )

    if [ "$platform" = "mplab_xc32" ]; then
        make_params+=("TOOLCHAIN=xc32")
    fi

    if [ -n "$optimized_kernel_dir" ]; then
        make_params+=("OPTIMIZED_KERNEL_DIR=$optimized_kernel_dir")
    fi

    make_params+=(GECKO_SDK_PATH=../../../gecko_sdk/)

    # Join the array elements into a single string with space-separated values
    make_string="${make_params[*]}"

    echo ${make_string}

    make -j -f tensorflow/lite/micro/tools/make/Makefile generate_model_runner_make_project ${make_string}
    check_return_code
    echo "GEN PATH"
    ls ${TENSORFLOW_ROOT}/gen/
    cd ${TENSORFLOW_ROOT}/gen/"$platform"_"$target"_"$build_type"/prj/model_runner/make
    sed -i 's|tensorflow/lite/micro/tools/make/downloads/cmsis/|./|g' Makefile

    if [ ! -d "third_party/cmsis" ]; then
        mkdir "third_party/cmsis"
    else
        rm -r third_party/cmsis/CMSIS
        rm -r third_party/cmsis/Device
    fi
    
    cp -r ${TENSORFLOW_ROOT}tensorflow/lite/micro/tools/make/downloads/cmsis/CMSIS/ third_party/cmsis/CMSIS
    cp -r ${TENSORFLOW_ROOT}tensorflow/lite/micro/tools/make/downloads/cmsis/Device/ third_party/cmsis/Device
    if [ -v "$optimized_kernel_dir" ]; then
        python  ${TENSORFLOW_ROOT}/tensorflow/lite/micro/tools/make/ext_libs/makefile_modifier.py $optimized_kernel_dir
    fi
    # python ${TENSORFLOW_ROOT}/tensorflow/lite/micro/tools/optimize/remove_ops.py --prj_dir=${TENSORFLOW_ROOT}/gen/"$platform"_"$target"_"$build_type"/prj/model_runner/make
    cd ${TENSORFLOW_ROOT}
    bazel run tensorflow/lite/micro/tools/gen_micro_mutable_op_resolver:generate_micro_mutable_op_resolver_from_model -- --common_tflite_path=${TENSORFLOW_ROOT}/tensorflow/lite/micro/examples/model_runner/codegen/  --input_tflite_files=model.tflite --output_dir=${TENSORFLOW_ROOT}/gen/"$platform"_"$target"_"$build_type"/prj/model_runner/make/tensorflow/lite/micro/
    #bazel run tensorflow/lite/tools:strip_strings -- --input_tflite_file=${TENSORFLOW_ROOT}/tensorflow/lite/micro/examples/model_runner/codegen//model.tflite --output_tflite_file=${TENSORFLOW_ROOT}/tensorflow/lite/micro/examples/model_runner/codegen/model_stripped.tflite
    echo "LOG START"
}

build_lib(){
    cd ${TENSORFLOW_ROOT}/gen/"$platform"_"$target"_"$build_type"/prj/model_runner/make
    make lib -j
    check_return_code
}


generate_code

outfile=tensorflow_"$kp_id".zip

echo "TENSORFLOW BUILD DIR"
ls
cd ${TENSORFLOW_ROOT}/gen/"$platform"_"$target"_"$build_type"/prj/model_runner/
mv make tflite-micro
mkdir libsensiml
mkdir libsensiml/src
# cp tflite-micro/libtensorflow-microlite.a libsensiml
cp tflite-micro/tensorflow/lite/micro/micro_api.h libsensiml/
cp ${TENSORFLOW_ROOT}/tensorflow/lite/micro/examples/model_runner/codegen/model.tflite libsensiml/
cp ${TENSORFLOW_ROOT}/tensorflow/lite/micro/examples/model_runner/codegen/model_stripped.tflite libsensiml/

mv libsensiml tflite-micro/


zip -r tflite-micro.zip tflite-micro/*
mv tflite-micro.zip $mount_point/tflite-micro.zip

chown $user:$user $mount_point/tflite-micro.zip

if [ -z $bucket_name ]; then
echo "Done"
else
aws s3 cp $mount_point/tflite-micro.zip s3://$bucket_name/$kp_id/tflite-micro.zip
fi

ls -al $mount_point
exit $?

#We don't check this return value because it fails to set up some things, but still builds in the container.