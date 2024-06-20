#!/bin/bash

verify() {
	if [ $? -ne 0 ]; then exit 1; fi
}
cd $HOMEDIR/server

python manage.py initialize_directories
python manage.py collectstatic --noinput


echo "CREATE EXTENSION IF NOT EXISTS tablefunc;\q" | python manage.py dbshell
python manage.py migrate --noinput; verify


echo "BEGIN; TRUNCATE  \"logger_usagelog\" ,\"logger_log\", \"library_functioncost\" CASCADE; COMMIT; \q" | python manage.py dbshell
python manage.py clear_v2_platforms; verify
python manage.py load_codegen_support; verify

echo "Loading standard fixtures"
python manage.py loaddata default client_oauth application applicationapikeys loglevel  architectures processors compilers platforms_v2; verify

python manage.py load_functions; verify
python manage.py loaddata function_costs; verify
python manage.py create_foundation_models; verify