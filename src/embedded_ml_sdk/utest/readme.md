Info by: Thawee Techathamnukool
Data: May 08, 2017

What:
====
Unit test using google-test framework and cmake for sensiml_sdk

Needed SW:
=========
Platform: Ubuntu
Needed SW: gtest and cmake


How to get gtest and cmake:
==========================
sudo apt-get install libgtest-dev
sudo apt-get install cmake


How to build gtest lib:
======================
You need to build gtest as well
cd /usr/src/gtest
sudo cmake CMakeLists.txt
sudo make
sudo cp *.a /usr/lib


Now you are good to go.

Reference for simple test if you would like to try: https://www.eriksmistad.no/getting-started-with-google-test-on-ubuntu/


How to build and run this unit test:
./build.sh - to re-run cmake and rebuild everything

How to re-build only with your modification and run the unit test:
./update.sh - to re-compile on the file you just modified

How to clean:
./clean.sh


Where is the executable:
/sensiml_sdk/utest/out/kbgtest

Note: 
1. build.sh will build and run all tests once.
2. clean.sh will delete out/
3. You can run test multiple time with --gtest_repeat=N
4. Need to capture test output? --gtest_output="xml:filename.xml"
5. To run some tests? --gtest_filter=MEAN_CALCULATION_TEST.*

More info about using gtest: https://www.ibm.com/developerworks/aix/library/au-googletestingframework.html


Specific setting of our CMakeLists.txt
======================================
- C compiler is set to gcc : -DCMAKE_C_COMPILER=gcc when calling cmake
- C++ compiler is set to g+ : -DCMAKE_CXX_COMPILER=g++ when calling cmake
- This unit test build is created with
  -DLINUX
  -DDEBUG
  -Wall
  -Werror
  -g
  -UTEST - add gtest specific information to our c code
- Linked with -m and -pthread

- Files to be compiles are set under SENSIML_SDK and SENSIML_SDK_UTEST
