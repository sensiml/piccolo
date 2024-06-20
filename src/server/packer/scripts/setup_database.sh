#!/bin/bash

verify() {
	if [ $? -ne 0 ]; then exit 1; fi
}

echo "BEGIN; TRUNCATE \"logger_usagelog\" ,\"logger_log\",  \"library_pipelineseed\", \"library_functioncost\" CASCADE; COMMIT; \q" | python manage.py dbshell
verify
printf '\n####\n for custom config add --settings=server.settings_{environment}'
printf '\n####\n Migrating DataModels to Database\n###\n'
python manage.py migrate
verify
printf '\n####\n loading default roles to Database\n###\n'
python manage.py clear_v2_platforms
verify
python manage.py loaddata default architectures processors compilers platforms_v2 client_oauth application applicationapikeys loglevel
verify
printf '\n####\n loading default roles to Database\n###\n'
python manage.py load_functions
verify
printf '\n####\nRunning Unit Test\n###\n'
python manage.py load_functions
verify
