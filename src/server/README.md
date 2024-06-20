# SensiML Server


SensiML Server is a backend for client software that enables sensor data processing, feature selection, and
Burlington model building and testing.


## Installation steps for server

2. Install Postgres >=9.5,

    create a datbase piccolodb
    create and give access to piccoloadmin with pw piccoloadmin3

    # to recreate db
    sudo su - postgres
    dropdb piccolodb
    createdb piccolodb --owner=piccoloadmin

3. Install redis

    apt-get install redis-server redis-cli

3. To install server, create a new file at `server/local_settings.py` and add any configuration needed to reflect your
system. This will load settings.py first and then your settings. be careful of overwriting any settings in settings.py file.

    python manage.py migrate --settings=server.local_settings
    python manage.py datamanager.yml develop.yml --settings=server.local_settings
    python manage.py load_functions --settings=server.local_settings

4. Then start the server using the *runserver* command for `manage.py`

    python manage.py runserver

5. celery workers also need to be running for the server to work properly

    celery --app=server.celery:app worker --loglevel=INFO -B -O fair --without-mingle --without-gossip  --concurrency 1 -Q celery,pipelines -n pipelines
    celery --app=server.celery:app worker --loglevel=INFO -B -O fair --without-mingle --without-gossip  --concurrency 1 -Q pipeline_steps -n steps
    celery --app=server.celery:app worker --loglevel=INFO -B -O fair --without-mingle --without-gossip  --concurrency 1 -Q file_upload,file_upload_large,knowledgepack -n uploader_and_kp

6. create the directory

    server/datamanager/kbcodegen

7. To Monitor workers using celery
    celery  --broker=redis://localhost:6379 flower --port=5551

    celery flower --conf=celeryconfig.py --port=5551

    celery --broker=redis://ec.dev.sensiml.internal flower
    celery --broker=redis://ec.prod.sensiml.internal  flower

8. To debug celery workers

        from celery.contrib import rdb
        rdb.set_trace()

    then you can connect to the pdb session using

        telnet localhost XXXX

    where XXXX is the number the celery worker prints out in the log

## Development Guidelines

   1. branches should be created with a brefix of feature/<branch-name> or bug/<bug-name>
   2. code should be formatted using black (pip install black)
   3. new code to the server should have basic unit tests written in the test folder of the code
   4. longer more complex code should also have functional tests in /func_test/pytest
   5. code should go through review with at least one reviewer familiar with code as well as the unit tests passing
   6. after code is deployed to dev, the functinal tests will run, if you break a functional test make that a priority to fix it

## Testing

Tests are normal Python modules which begin with the prefix `test_`. Django automatically discovers these modules with
the *py.test* command:
    pip install pytest-html
    pip install pytest-cov

     py.test --rlocal=True --html=report.html --server=dev.sensiml.cloud


## UWSGI Set up
To run server using uwsgi through nginx for development environment

```
pip install uwsgi
# Make changes to uwsgi_server.conf if not using default directories
cp uwsgi_server.conf /etc/nginx/sites-available
ln -s /etc/nginx/sites-available/uswgi_server.conf /etc/ngninx/sites-enabled
uwsgi --socket server.sock --module server.wsgi --chmod-socket=666
```
