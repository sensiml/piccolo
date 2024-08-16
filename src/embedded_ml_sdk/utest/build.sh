#!/bin/bash

check_return_code() {
        #Check the return code of most recent calls.
        rc=$?;
        echo "LOG STOP";
        if [[ $rc != 0 ]]; then exit $rc; fi
}

if [ -e out ]
then
    echo "Removing Old Out directory"
    echo "rm -rf out"
    rm -rf out
fi
mkdir out
cd out
echo "LOG START"
cmake .. -DCMAKE_CXX_COMPILER=g++ -DCMAKE_C_COMPILER=gcc
check_return_code
echo "LOG START"
make -j
check_return_code
#make VERBOSE=1
echo "LOG START"

# if need, try 'make VERBOSE=1'
