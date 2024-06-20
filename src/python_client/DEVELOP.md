
* Follow the link to the installer
* Run command:

        pip install sensiml-[build-number]-py2-none-any.whl

## For Developers

### Install from codebase

    pip install setup.py -U

### Test the sensiml client

    py.test --django -ra

### Create a Python wheel for distribution
* Update the version information in setup.py
* From the current working directory, run

        python setup.py bdist_wheel

The wheel file should be in the `dist/` subdirectory.


# to release a new version

update versions
    sensiml/__init__.py
    setup.py

python setup.py publish

# to release a new dev version

python setup.py test

# to install the dev version

pip install --index-url https://test.pypi.org/simple/  sensiml


# To re-build and run the knowledgepack x86

mkdir _build
make -j && mv _build/libsensiml.a . && cd ../testdata_runner/ && gcc main.c -o a.out -L../libsensiml -lsensiml -lm -I../libsensiml && ./a.out && cd ../libsensiml