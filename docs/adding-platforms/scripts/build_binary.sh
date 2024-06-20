#!/bin/bash

check_return_code() {
        #Check the return code of most recent calls.
        rc=$?; if [[ $rc != 0 ]]; then exit $rc; fi
}
# These are passed in by SensiML servers. Do not modify!
inputs=$1

mount_point=`$1 | jq -r '.["mount_directory"]'`
project=`$1 | jq -r '.["application"]'`
kp_id=`$1 | jq -r '.["uuid"]'`
user=`$1 | jq -r '.["user_id"]'`
debug=`$1 | jq -r '.["debug_flag"]'`
version=`$1 | jq -r '.["version"]'`
platform=`$1 | jq -r '.["platform"]'`
build_tensorflow=n

if [ "$BUCKET_NAME" = "NO S3" ]; then
        rename_output=$outfile
else
        rename_output="codegen-compiled-output"
fi

echo "Building Binary"

mkdir -p $SML_APP_LIB_DIR

cp $SML_KP_OUTPUT_DIR/kb.a $SML_APP_LIB_DIR/libsensiml.a
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
pwd
#
# HERE YOU WILL ADD YOUR BUILD STEPS.
#
#
# make all -j

check_return_code

mkdir return_files
cd return_files

#
# HERE YOU WILL ADD ALL FILES YOU WISH TO BE RETURNED WITH THE BINARY.
# SensiML typically returns bin/hex file, map, and other informational files.
# If all output files are in SML_APP_OUTPUT_BIN_DIR, no action is required.
#

echo $outfile

outfile=kp_"$kp_id"_"$platform"_"$lib_bin"_"$version"_"$debug".zip
cp -RT "$SML_APP_OUTPUT_BIN_DIR" .
cp $SML_KP_DIR/model.json .
zip -r $outfile ./
cp ./$outfile $mount_point/$outfile


exit $?
