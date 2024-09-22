#!/bin/bash
check_return_code() {
        #Check the return code of most recent calls.
        rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
}

export http_proxy=''
export https_proxy=''

# ECS DOCKER

if test "$#" -eq 4; then
        awsaccess=$1
        awssec=$2
        kp_id=$3
        bucket_name=$4
        build_script_name="build.sh"
else
        awsaccess=$AWS_S3_ACCESS
        awssec=$AWS_S3_SEC
        kp_id=$KP_UUID
        bucket_name=$BUCKET_NAME
        build_script_name=$BUILD_SCRIPT_NAME
fi

ls

echo "LOCAL BUILD  $kp_id"
echo $bucket_name
echo $kp_id
echo $build_script_name


if [ -d /codegen_files ]; then
        cp /codegen_files/build_nnom.sh /$build_script_name
        dos2unix /$build_script_name
        chmod +x /$build_script_name
        ./$build_script_name "cat /codegen_files/$kp_id/execute.json"
        check_return_code
        chown -R $user:$user /codegen_files
else
        cp /data/datamanager/codegen/$kp_id/build_nnom.sh /$build_script_name
        dos2unix /$build_script_name
        chmod +x /$build_script_name
        cd /
        ./$build_script_name "cat /data/datamanager/codegen/$kp_id/execute.json"
        check_return_code
        #chown -R $user:$user /codegen_files
fi


