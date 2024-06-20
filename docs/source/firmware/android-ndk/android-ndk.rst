.. meta::
    :title: Firmware - Android NDK Integration
    :description: Guide for integrating Android NDK Knowledge Packs.

==============================
Android Native Development Kit
==============================

.. figure:: img/android-developers.png
   :align: center

In order to use SensiML Knowledge Packs with Android, the application must be configured to use the `Android NDK <https://developer.android.com/ndk>`_.

You can `Create or import a native project <https://developer.android.com/ndk/guides#native-project>`_ to do this. For this guide, we will show you how to integrate the library version of a Knowledge Pack or the Source Code version of a Knowledge Pack. 


Using A Library Download
------------------------

When you download a model, you will get a zip file with a structure that looks similar to this:

::

    knowledgepack-libs
       ├── model.json
       ├── include
           ├── kb.h
           ├── kb_defines.h
           ├── kb_typedefs.h
           └── kb_debug.h
       ├── src
            ├── arm64-v8a
                └── libsensiml.so
            ├── armeabi-v7a
                └── libsensiml.so
            ├── x86
                └── libsensiml.so
            ├── x86_64
                └── libsensiml.so
    knowledgepack_project
            └── recognition_run
                ├── sml_recognition_run.cpp
                ├── CMakeLists.txt
                └── README.md

**Copy the Library Files**

You can add the knowledgepack-libs folder to your application folder, for instance ``app/knowledgepack-libs``

**Copy and rename the wrapper functions**

Copy the ``knowledgepack_project/recognition_run/sml_recognition_run.cpp`` file to the ``app/src/main/cpp`` directory. This file may need changes, as it is set up in such a way that it will be exported to an activity named **KnowledgePackActivity**. If your application does not have a **KnowledgePackActivity**, rename the JNIExport calls:

.. code-block :: C

    extern "C"
    JNIEXPORT jboolean JNICALL
    Java_com_sensiml_knowledgepackrunner_KnowledgePackActivity_usingTestData(JNIEnv *env,
                                                                        jobject call_object){
    #ifdef USE_TEST_RAW_SAMPLES
        return true;
    #else
        return false;
    #endif
    }

    // RENAMED VERSION HERE:

    extern "C"
    JNIEXPORT jboolean JNICALL
    Java_com_sensiml_knowledgepackrunner_YOURRECOGNITIONACTIVITY_usingTestData(JNIEnv *env,
                                                                        jobject call_object){
    #ifdef USE_TEST_RAW_SAMPLES
        return true;
    #else
        return false;
    #endif
    }

This will need to be done for all of the calls.

**Update CMakeLists.txt**

The Android NDK uses CMake to compile and link native code to java. When you generate a SensiML Knowledge Pack for Android NDK we will automatically generate a CMakeLists.txt file in your knowledgepack_project\recognition_run directory that you can use to compile in your application.

If you already have a CMakeLists.txt file that you are using in your project then you will need to add the following relevant content to your file:

.. code-block ::

    set(kp_lib_DIR ${CMAKE_SOURCE_DIR}/../../../knowledgepack-libs)
    set(kp_inc_DIR ${kp_lib_DIR}/include)
    # Creates and names a library, sets it as either STATIC
    # or SHARED, and provides the relative paths to its source code.
    # You can define multiple libraries, and CMake builds them for you.
    # Gradle automatically packages shared libraries with your APK.

    add_library(
            sensiml
            SHARED
            IMPORTED
    )
    set_target_properties(sensiml
            PROPERTIES IMPORTED_LOCATION
            ${kp_lib_DIR}/src/${CMAKE_ANDROID_ARCH_ABI}/libsensiml.so)
    include_directories(${kp_inc_DIR})

    # Searches for a specified prebuilt library and stores the path as a
    # variable. Because CMake includes system libraries in the search path by
    # default, you only need to specify the name of the public NDK library
    # you want to add. CMake verifies that the library exists before
    # completing its build.

    add_library( # Sets the name of the library.
            knowledgepack-wrapper

            # Sets the library as a shared library.
            SHARED

            # Provides a relative path to your source file(s).
            sensiml_recognition_run.cpp)

    target_include_directories(knowledgepack-wrapper
            PRIVATE
            ${kp_inc_DIR})

    target_link_libraries( # Specifies the target library.

            # YOUR OTHER LIBRARIES GO HERE
            knowledgepack-wrapper
            android
            sensiml

            # Links the target library to the log library
            # included in the NDK.
            log)





Using Source Code Download
--------------------------

When using the source code download option, you will also get the precompiled libraries, as well as the model source. The above steps for ``sml_recognition_run.cpp`` still apply. You will now see a directory structure like this:

::

    knowledgepack-libs
       ├── model.json
       ├── include
           ├── kb.h
           ├── kb_defines.h
           ├── kb_typedefs.h
           └── kb_debug.h
       ├── src
            ├── arm64-v8a
                └── libsensiml.so
            ├── armeabi-v7a
                └── libsensiml.so
            ├── x86
                └── libsensiml.so
            ├── x86_64
                └── libsensiml.so
    knowledgepack_project
            └── recognition_run
                ├── sml_recognition_run.cpp
                ├── CMakeLists.txt
                └── README.md
    libsensiml
        └── cpp
            ├── model source files
            └── model header files

Copy the `libsensiml/cpp` folder to the directory of your choice. Here, we will use ``MAIN_DIR/libsensiml/cpp``

**Update CMakeLists.txt**

The Android NDK uses CMake to compile and link native code to java. When you generate a SensiML Knowledge Pack for Android NDK we will automatically generate a CMakeLists.txt file in your knowledgepack_project\recognition_run directory that you can use to compile in your application.

If you already have a CMakeLists.txt file that you are using in your project then you will need to add the following relevant content to your file:

The ``CMakeLists.txt`` file changes slightly from that of the library version. Instead of pulling in pre-compiled ``.so`` files, the source code will directly be built first.

.. code-block ::


    set(KNOWLEDGEPACK_MODEL_SOURCE_DIR ${CMAKE_SOURCE_DIR}/../../../libsensiml/cpp)
    file(GLOB KNOWLEDGEPACK_SRCS ${KNOWLEDGEPACK_MODEL_SOURCE_DIR}/ *.c)
    # Creates and names a library, sets it as either STATIC
    # or SHARED, and provides the relative paths to its source code.
    # You can define multiple libraries, and CMake builds them for you.
    # Gradle automatically packages shared libraries with your APK.

    add_library(
            sensiml
            SHARED
            ${KNOWLEDGEPACK_SRCS}
    )
    find_library( # Sets the name of the path variable.
              log-lib

              # Specifies the name of the NDK library that
              # you want CMake to locate.
              log )
    include_directories(${KNOWLEDGEPACK_MODEL_SOURCE_DIR})

    # Searches for a specified prebuilt library and stores the path as a
    # variable. Because CMake includes system libraries in the search path by
    # default, you only need to specify the name of the public NDK library
    # you want to add. CMake verifies that the library exists before
    # completing its build.

    add_library( # Sets the name of the library.
            knowledgepack-wrapper

            # Sets the library as a shared library.
            SHARED

            # Provides a relative path to your source file(s).
            sensiml_recognition_run.cpp)

    target_include_directories(knowledgepack-wrapper
            PRIVATE
            ${kp_inc_DIR})

    target_link_libraries( # Specifies the target library.

            # YOUR OTHER LIBRARIES GO HERE
            knowledgepack-wrapper
            android
            sensiml

            # Links the target library to the log library
            # included in the NDK.
            log)


Integrating the Knowledge Pack in your Application
--------------------------------------------------

``README.md`` Is provided in the ```knowledgepack_project/recognition_run``` folder of a download. This file contains integration instructions for Kotlin and Java langagues, ensuring that the NDK library components and expected calls to the SensiML models will be set up properly.


Initializing the Models
-----------------------

The models will need to be initialized just once. The ``initSensiMLKnowledgePackModels()`` call will do that. This call should be placed in the Activity creation where data will be processed.


