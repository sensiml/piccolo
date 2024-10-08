#!/bin/bash
#Usage: build_kp_bin.sh <mount dir> <KP UUID> <user num> <board> <project> <lib_or_binary> <production_or_debug>
#                         $mount      $kp_id     $user     $board   $project       $lib_bin          $debug
#copy the generated files from the instance to the kbalgo folder
# $mount == the mount directory for this container.


check_return_code() {
        #Check the return code of most recent calls.
        rc=$?;
        echo "LOG STOP";
        if [ $1 -ne 0 ]
        then
            echo "SKIP CHECKING RETURN CODE"
        elif [ $rc -ne 0 ];
        then
            echo "EXITING with $rc"
            exit $rc;
        fi
}
inputs=$1


mount_point=`$1 | jq -r '.["mount_directory"]'`
project=`$1 | jq -r '.["project"]'`
application=`$1 | jq -r '.["application"]'`
kp_id=`$1 | jq -r '.["uuid"]'`
user=`$1 | jq -r '.["user_id"]'`
board=`$1 | jq -r '.["board_variant"]'`
lib_bin=`$1 | jq -r '.["build_type"]'`
debug=`$1 | jq -r '.["debug_flag"]'`
version=`$1 | jq -r '.["version"]'`
awsaccess=`$1 | jq -r '.["aws_access"]'`
awssec=`$1 | jq -r '.["aws_sec"]'`
platform=`$1 | jq -r '.["platform"]'`
profile=`$1 | jq -r '.["profile_data"]'`
target=`$1 | jq -r '.["target"]'`
sample_rate=`$1 | jq -r '.["sample_rate"]'`
extra_build_flags=`$1 | jq -r '.["extra_build_flags"]'`
build_tensorflow=n
#new stuff to handle dynamic name change
library_name=`$1 | jq -r '.["library_name"]'`
output_directory_name=`$1 | jq -r '.["directory_name"]'`
sensor_plugin_name=`$1 | jq -r '.["sensor_plugin_name"]'`
accel_range=`$1 | jq -r '.["accelerometer_sensor_range"]'`
gyro_range=`$1 | jq -r '.["gyroscope_sensor_range"]'`


export http_proxy=''
export https_proxy=''

skip_check=1
check_code=0
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

export mount_point=$mount_point
export project=$project
export application=$application
export kp_id=$kp_id
export user=$user
export board=$board
export lib_bin=$lib_bin
export debug=$debug
export version=$version
export profile=$profile
export target=$target
export sample_rate=$sample_rate
export extra_build_flags=$extra_build_flags
export library_name=$library_name
export output_directory_name=$output_directory_name
export platform=$platform
export sensor_plugin_name=$sensor_plugin_name
export gyro_range=$gyro_range
export accel_range=$accel_range

bucket_name=$BUCKET_NAME

if [ $debug == "d" ]; then
    SML_DEBUG_STRING="NO_DEBUGGING_NOW"
else
    SML_DEBUG_STRING="DEBUG"
fi


EXTRA_LIBS_DIR=/build
SML_KP_DIR=$EXTRA_LIBS_DIR/libsensiml
SML_KP_OUTPUT_DIR=$SML_KP_DIR/_build
TF_LITE_DIR=$EXTRA_LIBS_DIR/tflite-micro
SML_APP_BASE_DIR=/build/
SML_APP_PROJECT_BASE_DIR=$SML_APP_BASE_DIR/$application/
PACKAGE_LIB_FILE=/package_library.sh

export EXTRA_LIBS_DIR=$EXTRA_LIBS_DIR
export SML_KP_DIR=$SML_KP_DIR
export TF_LITE_DIR=$TF_LITE_DIR
export SML_APP_BASE_DIR=$SML_APP_BASE_DIR
export SML_APP_PROJECT_BASE_DIR=$SML_APP_PROJECT_BASE_DIR
export SML_KP_OUTPUT_DIR=$SML_KP_OUTPUT_DIR
export TARGET_ARCH=$target

echo SML_KP_OUTPUT_DIR $SML_KP_OUTPUT_DIR
echo EXTRA_LIBS_DIR $EXTRA_LIBS_DIR
echo SML_KP_DIR $SML_KP_DIR
echo TF_LITE_DIR $TF_LITE_DIR
echo SML_APP_BASE_DIR $SML_APP_BASE_DIR
echo SML_APP_PROJECT_BASE_DIR $SML_APP_PROJECT_BASE_DIR

#Add the transcode library
if [ -f $mount_point/${kp_id}.zip ]; then
    unzip -o $mount_point/${kp_id}.zip -d $mount_point
fi

cp $mount_point/$application/scripts/build_binary.sh .
cp $mount_point/$application/scripts/config_sensor_files.sh .
cp $mount_point/$application/scripts/package_library.sh .
rm -r $mount_point/$application/scripts
chmod +x ./build_binary.sh
chmod +x ./package_library.sh
chmod +x ./config_sensor_files.sh


cp -r $mount_point/libsensiml $EXTRA_LIBS_DIR
cp -r $mount_point/tflite-micro $EXTRA_LIBS_DIR
cp -R $mount_point/$application $SML_APP_BASE_DIR

outfile=kp_"$kp_id"_"$platform"_"$lib_bin"_"$version"_"$debug".zip
export outfile=$outfile

if [ "$BUCKET_NAME" = "NO S3" ]; then
        echo "NO S3 ####"
        rename_output="codegen-compiled-output"
else
        rename_output="codegen-compiled-output"
fi

if [ -f "/root/esp/esp-idf/export.sh" ]; then
    source /root/esp/esp-idf/export.sh
fi


echo "*****KB DIRECTORY*****"
cd $SML_KP_DIR
ls -alh



config_sensors(){

      if [[ -f "./config_sensor_files.sh" ]]; then
         echo "LOG START"
        ./config_sensor_files.sh "cat $mount_point/execute.json"
        check_return_code $check_code
    fi
}

build_tensorflow(){
    if [ -d $TF_LITE_DIR ]; then
        pushd $TF_LITE_DIR
        echo "BUILDING LIBTENSORFLOW_MICROLITE LIBRARY"
        echo $GNU_INSTALL_ROOT

        make_params=(TARGET_TOOLCHAIN_ROOT=$GNU_INSTALL_ROOT/bin/)


        # Join the array elements into a single string with space-separated values
        make_string="${make_params[*]}"

        make lib -j 6 ${make_string}
        check_return_code $1
        cp libtensorflow-microlite.a $SML_KP_DIR
        cp tensorflow/lite/micro/micro_api.h $SML_KP_DIR
        rm -r obj
        popd
    fi

}

build_lib(){
    echo "LOG START"

    pushd $SML_KP_DIR
    mkdir -p $SML_KP_OUTPUT_DIR

    build_tensorflow $1

    mv nnom/* .
    cat weights.h nnom_middleware.c > nnom_combined.c
    mv  nnom_combined.c nnom_middleware.c
    rm weights.h

    LIB_TENSORFLOW_FILE=libtensorflow-microlite.a
    if [ -f "$LIB_TENSORFLOW_FILE" ]; then
	    build_tensorflow=y
        export build_tensorflow=$build_tensorflow
    fi

     make_params=(BUILD_TENSORFLOW=$build_tensorflow )

     if [ -n "$extra_build_flags" ]; then
        make_params+=("SML_FLAGS=$extra_build_flags")
     fi

    # Join the array elements into a single string with space-separated values
    make_string="${make_params[*]}"

    make -j  ${make_string}

    # for source we want to skip checking if this built correctly or not and just return
    check_return_code $1
    popd
}

run_lib(){
    build_lib

    pushd $SML_KP_DIR

    ldflags="-l$output_directory_name -lm"
    if [ -f "libtensorflow-microlite.a" ]; then
        build_tensorflow=y
        ldflags="-lm -l$output_directory_name -ltensorflow-microlite"
    fi

    echo "LD FLAGS #######"
    echo $ldflags

    cp ./_build/$library_name.a .
    cp ./_build/$library_name.dll .

    cp ../application/main.c .
    ls
    g++ main.c -o a.out -L./ -I$library_name $ldflags
    ./a.out > recognize.txt
    check_return_code
    popd
}

copy_output(){
    echo $outfile
    echo $mount_point/$outfile
    mv "$mount_point/$outfile" $mount_point/$rename_output
    chown $user:$user $mount_point/$rename_output
    echo "$outfile" > $mount_point/output_binary_name
    chown $user:$user $mount_point/output_binary_name

    if [ "$BUCKET_NAME" = "NO S3" ]; then
        echo "Done"
    else
        aws s3 cp $mount_point/codegen-compiled-output s3://$bucket_name/$kp_id/codegen-compiled-output
        aws s3 cp $mount_point/output_binary_name s3://$bucket_name/$kp_id/output_binary_name
    fi
}


if [ "$lib_bin" = "bin" ]; then

    build_lib $check_code
    config_sensors
    cd /

    echo "LOG START"
    /build_binary.sh
    check_return_code $check_code
elif [ $lib_bin = "recognize" ]; then
    mkdir -p $SML_KP_OUTPUT_DIR
    outfile="recognize.txt"
    run_lib
    mv $SML_KP_DIR/$outfile $mount_point/$outfile
else

    mkdir -p $SML_KP_OUTPUT_DIR
    mkdir -p $output_directory_name

    if [ "$lib_bin" = "source" ]; then
        build_lib $skip_check
    else
        build_lib $check_code
    fi

    mkdir knowledgepack
    cd knowledgepack

    if [ "$project" = "arduino" ]; then
        echo "LOG START"
        pwd

        mkdir -p $SML_APP_PROJECT_BASE_DIR/src/lib
        mkdir -p $SML_APP_PROJECT_BASE_DIR/src/$target
        cp $SML_KP_OUTPUT_DIR/$library_name.a $SML_APP_PROJECT_BASE_DIR/src/$target/$library_name.a
        cp $SML_KP_DIR/libtensorflow-microlite.a $SML_APP_PROJECT_BASE_DIR/src/$target/libtensorflow-microlite.a        
        cp /build/tflite-micro/libsensiml/model.tflite $SML_APP_PROJECT_BASE_DIR/src/lib/model.tflite


        cp $SML_KP_DIR/kb.h $SML_APP_PROJECT_BASE_DIR/src
        cp $SML_KP_DIR/kb_defines.h  $SML_APP_PROJECT_BASE_DIR/src
        cp $SML_KP_DIR/kb_output.h  $SML_APP_PROJECT_BASE_DIR/src
        cp $SML_KP_DIR/kb_typedefs.h  $SML_APP_PROJECT_BASE_DIR/src
        cp $SML_KP_DIR/testdata.h $SML_APP_PROJECT_BASE_DIR/src
        cp $SML_KP_DIR/model.json $SML_APP_PROJECT_BASE_DIR
        cp $SML_KP_DIR/model_json.h $SML_APP_PROJECT_BASE_DIR/src

        if [ "$lib_bin" = "source" ]; then
            cp $SML_KP_DIR/*.c $SML_APP_PROJECT_BASE_DIR/src/
            cp $SML_KP_DIR/*.h $SML_APP_PROJECT_BASE_DIR/src/
            cp $SML_KP_DIR/Makefile $SML_APP_PROJECT_BASE_DIR/src/
            cp -r $TF_LITE_DIR .
        fi


        mv $SML_APP_PROJECT_BASE_DIR/* .

        cd ..

        # This code copies the README.md to the docker image
        # so we won't be stuck with the one in the template project
        # Change was made specifically for MicroChip builds but
        # Could apply to anyone :)
        if [ -f "$mount_point/README.md" ]; then
            cp $mount_point/README.md knowledgepack
        fi       

        zip -r knowledgepack.zip knowledgepack
        zip -r $outfile knowledgepack.zip
        ls -al
        mv "$outfile" $mount_point/$outfile
        ls -al
    else
        echo "LOG START"
        pwd
        mkdir -p $output_directory_name
        mkdir -p $output_directory_name/inc
        mkdir -p $output_directory_name/lib
        cp $SML_KP_OUTPUT_DIR/$library_name.a $output_directory_name/lib/
        cp $SML_KP_OUTPUT_DIR/$library_name.dll $output_directory_name/lib/       


        cp $SML_KP_DIR/libtensorflow-microlite.a $output_directory_name/lib/
        cp /build/tflite-micro/libsensiml/model.tflite $output_directory_name/model.tflite
        cp $SML_KP_DIR/kb.h $output_directory_name/inc

        cp $SML_KP_DIR/kb_defines.h  $output_directory_name/inc
        cp $SML_KP_DIR/kb_debug.h  $output_directory_name/inc
        cp $SML_KP_DIR/kb_output.h  $output_directory_name/inc
        cp $SML_KP_DIR/kb_typedefs.h  $output_directory_name/inc
        cp $SML_KP_DIR/testdata.h $output_directory_name/inc
        cp $SML_KP_DIR/model.json .
        cp $SML_KP_DIR/model_json.h $output_directory_name/inc



        if [ "$lib_bin" = "source" ]; then
            mkdir $output_directory_name/src/
            cp $SML_KP_DIR/*.c $output_directory_name/src/
            cp $SML_KP_DIR/*.h $output_directory_name/src/
            cp $SML_KP_DIR/Makefile $output_directory_name/src/
            rm -r $TF_LITE_DIR/libsensiml
            cp -r $TF_LITE_DIR .
            
        fi

        cp -r $mount_point/$application application
        cp $SML_APP_CONFIG_FILE application/
        cd ..        

        # backwards compatibility with DCL
        echo "CHECK IF DLL EXISTS"
        ls
        if [ -f "$SML_KP_OUTPUT_DIR/$library_name.dll" ]; then
            mkdir knowledgepack/$library_name
            cp $SML_KP_OUTPUT_DIR/$library_name.dll knowledgepack/$library_name/$library_name.dll            
            cp $SML_KP_DIR/model.json knowledgepack/$library_name/model.json
        fi                

        # This code copies the README.md to the docker image
        # so we won't be stuck with the one in the template project
        # Change was made specifically for MicroChip builds but
        # Could apply to anyone :)
        if [ -f "$mount_point/README.md" ]; then
            cp $mount_point/README.md knowledgepack
        fi

        if [ -f "/package_library.sh" ]; then
            /package_library.sh "$outfile"
        else
            zip -r $outfile knowledgepack
        fi
        
        ls -al
        mv "$outfile" $mount_point/$outfile
        ls -al
    fi
fi

copy_output



ls -al $mount_point
exit $?

#We don't check this return value because it fails to set up some things, but still builds in the container.

