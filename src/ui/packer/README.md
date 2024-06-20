# copy a version of the artifiacts to sml-artifact.zip

# run the packer script

> packer build sensiml-server.json

# This generates a new sensiml/server-image docker image

# run docker compose to start server

export SENSIML_DATA_DIR=./
docker compose up


# See Jenkinsfile for setting variables for packer script