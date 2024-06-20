## First Cloning The Repo

When you first clone the repo you will need to also clone the submodules (unless you are using some other sml_server repo)

git submodule update --init --recursive

To pull the latest submodule code you can run the following

git submodule update --recursive --remote

## Building The Docs

1. Install the requirements.txt

   - pip install -r requirements.txt

2. Add environment variable "SENSIML_SERVER_DEPLOY_HOME" which should have the path the your sensiml code

3. Building HTML Documentation

   - cd sml_docs
   - rm -rf _build && sphinx-build -W -b html source _build
   - python parse_function_names.py

4. AutotBuild docs to monitor while editing

   sphinx-autobuild source _build/html

4. Building PDF Documentation

   - sphinx-build -b latex source _build_pdf/ && cd _build_pdf/
   - in SensiMLAnalyticSuite.txt update the document class to have open any to remove blank pages
     \documentclass[letterpaper,10pt,english,openany]{sphinxmanual}
   - make && cd ..


## Building HTML Documentation with Docker

for this envirement your should have builded `sml_server_sensiml.cloud` container first

- check if your `sml_server_sensiml` container name the same as in Dockerfile
- add environment variables to `./docker.env` file or the docker environment
   - `SML_SERVER_DATADIR=./data`
   - `SML_SERVER_DIR=/src/server `
- run
   - with env file `docker-compose --env-file docker.env up`
   - or `docker-compose up`

## Architecture Guidelines

A top level folder that contains the entire index of the site. This contains a basic overview

Within each folder such as the data_management one shown above, there will be an index.rst that has the table of contents (toc) which points to the overivew.rst first and then any other modules after that.

All images for each module should be stored within their own img folder

STYLE GUIDELINES

1.  The three levels should be

        ===============
        MAJOR TITLE
        ===============

        SUBTITLE
        ------------

        SUBSECTION
        `````````````

        ** SUB SUB SECTION **

2.  Section headers should try to be 1 line if possible, but not more than 2.

## Cheat Sheet

### doc links

   :doc:`TEXT <../../relative-path>`

### html links

   `TEXT <https://url>`\_

### code formatting

   .. highlight:: python

   .. code-block:: language
         
         some text

   .. imagecarousel:: path1.png,text description,path2.png,text description,etc...

###  Convert .docx file to .rst 

``` bash
   pandoc --extract-media _static/img/path-to-folder --wrap=none -f docx <file-name>.docx  -t rst -o <file-name>.rst
```


## Include portion of file

.. include:: /<path-to-rst>

# Note in blue

.. note:: 
