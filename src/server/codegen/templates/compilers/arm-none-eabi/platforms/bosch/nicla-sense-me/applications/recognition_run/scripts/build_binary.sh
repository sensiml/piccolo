#!/bin/bash
#Usage: build_kp_bin.sh <mount dir> <KP UUID> <user num> <board> <project> <lib_or_binary> <production_or_debug>
#                         $mount      $kp_id     $user     $board   $project       $lib_bin          $debug
#copy the generated files from the instance to the kbalgo folder
# $mount == the mount directory for this container.

check_return_code() {
        #Check the return code of most recent calls.
        rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
}

inputs=$1


mount_point=`$1 | jq -r '.["mount_directory"]'`
project=`$1 | jq -r '.["application"]'`
kp_id=`$1 | jq -r '.["uuid"]'`
user=`$1 | jq -r '.["user_id"]'`
board=`$1 | jq -r '.["board_variant"]'`
lib_bin=`$1 | jq -r '.["build_type"]'`
debug=`$1 | jq -r '.["debug_flag"]'`
version=`$1 | jq -r '.["version"]'`
platform=`$1 | jq -r '.["platform"]'`
profile=`$1 | jq -r '.["profile_data"]'`
target=`$1 | jq -r '.["target"]'`

build_env="nano33ble"

if [ -e $SML_KP_DIR/libtensorflow-microlite.a ]; then
  build_env="nano33ble_with_tensorflow"
fi

if [ "$BUCKET_NAME" = "NO S3" ]; then
        rename_output=$outfile
else
        rename_output="codegen-compiled-output"
fi

echo "Building Binary"

mkdir -p $SML_APP_LIB_DIR

cp $SML_KP_OUTPUT_DIR/libsensiml.a $SML_APP_LIB_DIR/libsensiml.a
cp $SML_KP_DIR/libtensorflow-microlite.a $SML_APP_LIB_DIR/
cp $SML_KP_DIR/kb.h $SML_APP_LIB_DIR

cp $SML_KP_DIR/kb_defines.h  $SML_APP_LIB_DIR
cp $SML_KP_DIR/model_json.h  $SML_APP_LIB_DIR
cp $SML_KP_DIR/kb_debug.h  $SML_APP_LIB_DIR
cp $SML_KP_DIR/kb_typedefs.h  $SML_APP_LIB_DIR
cp $SML_KP_DIR/testdata.h $SML_APP_LIB_DIR
cp $SML_KP_DIR/model.json $mount_point/

pushd $SML_APP_BUILD_DIR
cp $mount_point/$project/* $SML_APP_DIR
pio run -j 4 -e $build_env

check_return_code

mkdir return_files
cd return_files

echo $outfile

outfile=kp_"$kp_id"_"$platform"_"$lib_bin"_"$version"_"$debug".zip
cp -RT "$SML_APP_OUTPUT_BIN_DIR" .
cp $SML_KP_DIR/model.json .
zip -r $outfile ./
cp ./$outfile $mount_point/$outfile


exit $?

#We don't check this return value because it fails to set up some things, but still builds in the container.

