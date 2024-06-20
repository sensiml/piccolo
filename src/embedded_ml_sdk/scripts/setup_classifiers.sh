#!/bin/bash


verify() {
	if [ $? -ne 0 ]; then exit 1; fi
}


if [ -z ${HOMEDIR+x} ]; then 
	echo "HOMEDIR not set, "
	exit
else
	echo "Using HOMEDIR=$HOMEDIR"
fi

echo "USER EXECUTING SCRIPT IS $USER"

LIB_INSTALL_PATH=$HOMEDIR/lib
rm -rf $LIB_INSTALL_PATH/*
mkdir -p $LIB_INSTALL_PATH



build_classifier_libs() {
printf '\n####\n Building PME\n###\n'
pushd $HOMEDIR/embedded_ml_sdk/classifiers/pme
make clean
make setup && make && make install INSTALL_PATH=$LIB_INSTALL_PATH; verify; make clean
popd

printf '\n####\n Building Booosted tree Ensemble\n###\n'
pushd $HOMEDIR/embedded_ml_sdk/classifiers/boosted_tree_ensemble
make clean
make && make install INSTALL_PATH=$LIB_INSTALL_PATH; verify; make clean
popd

printf '\n####\n Building tree Ensemble\n###\n'
pushd $HOMEDIR/embedded_ml_sdk/classifiers/tree_ensemble
make clean
make && make install INSTALL_PATH=$LIB_INSTALL_PATH; verify; make clean
popd


printf '\n####\n Building Linear Regression Classifier\n###\n'
pushd $HOMEDIR/embedded_ml_sdk/classifiers/linear_regression
ls
make clean
make  && make install INSTALL_PATH=$LIB_INSTALL_PATH; verify; make clean
popd

printf '\n####\n Building Bonsai Classifier\n###\n'
pushd $HOMEDIR/embedded_ml_sdk/classifiers/bonsai
make clean
make setup && make && make install INSTALL_PATH=$LIB_INSTALL_PATH; verify; make clean
popd


}


build_classifier_libs

printf "### INSTALLED CLASSIFIERS ####"
echo $LIB_INSTALL_PATH
printf "\nlibrary of Classifiers Installed\n"
ls -lht $LIB_INSTALL_PATH

