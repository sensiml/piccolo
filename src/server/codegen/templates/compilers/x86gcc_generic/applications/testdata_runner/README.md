# Compiling the simple test data app

This application requires testdata.h to be populated in order to run. If you haven't specified any, it won't work.

To compile a binary of this application with GCC, run:

```bash

    gcc main.c -o a.out -L../libsensiml -lsensiml -lm -I../libsensiml

To compile a shared library of this application with GCC, run

```bash

    ar -x libsensiml.a
    gcc -shared -o libsensiml.so *.o

# Compiling model with libtensorflow-microlite

```bash

    cd application
    g++ main.c -o a.out -L../libsensiml -lsensiml -ltensorflow-microlite -lm -I../libsensiml
    ./a.out

# Linking to your own application

1. Copy `libsensiml` folder to your desired location
2. Add an include path to your Makefile/IDE project

## Running in your application

1. Add `#include "kb.h"` to the file you wish to use the library in.
2. Before running any other code for the model, call `kb_model_init();`
3. To add sensor data a sample at a time, call `kb_run_model(<samples>, 0, <model_number>);`


