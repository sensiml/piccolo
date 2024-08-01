#!/bin/bash

verify() {
	if [ $? -ne 0 ]; then exit 1; fi
}
echo "####### STARTING SETUP PICCOLO AI ########"

echo "USER EXECUTING SCRIPT IS $USER"

whoami


if [[ "$NO_SETUP" == "1" ]]; then
  echo "NO_SETUP is set to 1. Exiting script."
  exit 1  # Exit with a non-zero status to indicate failure
fi

if [ -z ${HOMEDIR+x} ]; then 
	echo "HOMEDIR not set, "
	exit
else
	echo "Using HOMEDIR=$HOMEDIR"
fi

ls -lht $HOMEDIR

#copy the plugins
if [ -z ${PLUGIN_DIR+x} ]; then 
	echo "PLUGIN_DIR not set, skipping"
else
	echo "Using PLUGIN_DIR= $PLUGIN_DIR"
	cp -r $s/* $HOMEDIR/server
	verify
fi


echo "build the classifer library used by the server"
pushd $HOMEDIR/embedded_ml_sdk
chmod +x scripts/setup_classifiers.sh
./scripts/setup_classifiers.sh
verify

echo "build the python shared library for c code"
pushd $HOMEDIR/embedded_ml_sdk/pywrapper
make -j
verify
popd

echo "setup the server database and load fixtures"
pushd $HOMEDIR/server
chmod +x scripts/setup_database.sh
./scripts/setup_database.sh
verify
popd
