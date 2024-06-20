.. meta::
   :title: Knowledge Packs / Model Firmware - Adding Unit Tests with GoogleTest
   :description: How to add unit tests using the GoogleTest framework 

Adding Unit Tests with GoogleTest
=================================

You can create unit tests using the GoogleTest framework and CMake for Knowledge Packs downloaded as the **Source** format.

**Recommended**

* Recommended Platform: Ubuntu
* Packages: gtest and cmake


Install GoogleTest and CMake
````````````````````````````
.. code:: bash
    
    apt-get install libgtest-dev
    apt-get install cmake

Build the GoogleTest Library
````````````````````````````
.. code:: bash
 
    cd /usr/src/gtest
    cmake CMakeLists.txt
    make
    cp *.a /usr/lib

Reference for simple test if you would like to try: https://www.eriksmistad.no/getting-started-with-google-test-on-ubuntu/

Building and Running Unit Tests
```````````````````````````````

Re-run cmake and rebuild everything

.. code:: bash

    ./build.sh

Rebuild only with your modifications

.. code:: bash

    ./update.sh


How to Clean
`````````````

.. code:: bash

    ./clean.sh

The executable is built in the folder

.. code:: bash

    /sensiml_sdk/utest/out/kbgtest

Additional Notes
````````````````

1. build.sh will build and run all tests once
2. clean.sh will delete out
3. You can run the test multiple times with ``--gtest_repeat=N``
4. You can capture test output with ``--gtest_output="xml:filename.xml"``
5. You can run specific tests with ``--gtest_filter=MEAN_CALCULATION_TEST.*``

Find more info about using GoogleTest: https://www.ibm.com/developerworks/aix/library/au-googletestingframework.html

Adding New Tests
`````````````````
You can add new tests by updating the SENSIML_SDK and KB_UTEST variables in the CMakeLists.txt file

1. SENSIML_SDK - update with new .c files
2. KB_UTEST - update with corresponding unit tests new test_*.cpp files
