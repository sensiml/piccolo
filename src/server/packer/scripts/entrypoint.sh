#!/usr/bin/env bash

cd /home/sml-app/install/server

if [ $# -eq 2 ]
then
  echo "downloading env file $2"
  python -c "import boto3; s3 = boto3.client('s3'); s3.download_file('sml-config','$2/config/env.sml','/home/sml-app/.env.sml')"
fi

URI=`echo $ECS_AGENT_URI | awk -F/ '{print $NF}' | awk -F- '{print $1}'`

case "$1" in
  worker)
  STEP_NAME=steps:$URI
  echo "WORKER $STEP_NAME: STARTING"


  celery --app=server.celery:app worker --loglevel=INFO -O fair --without-mingle --without-gossip --max-tasks-per-child 50 --concurrency 1 -Q pipeline_steps -n $STEP_NAME
   ;;
   webserver)
   echo "WEBSERVER $STEP_NAME: STARTING"
    python manage.py runserver 0.0.0.0:8000 --noreload
   ;;
   pipeline)
   echo "PIPELINE $STEP_NAME: STARTING"
   sudo chown sml-app:sml-app /var/run/docker.sock
   PIPELINE_NAME=pipeline:$URI
   celery --app=server.celery:app worker --pool=gevent --loglevel=INFO -O fair --without-mingle --without-gossip  --concurrency 10 -Q pipelines,knowledgepack -n $PIPELINE_NAME
   ;;
  *)
    # The command is something like bash, not an airflow subcommand. Just run it in the right environment.
    echo "NO MATCH"
    echo $1
    exec "$@"
    ;;
esac