verify() {
	if [ $? -ne 0 ]; then exit 1; fi
}


export DJANGO_ENV='sml'

working_dir=/home/sml-app/sensiml-latest/
HOMEDIR=/home/sml-app
install_root=$HOMEDIR/install
server_root=$HOMEDIR/install/server
embedded_ml_sdk=$HOMEDIR/install/embedded_ml_sdk
kbkernel_root=$HOMEDIR/install/lib
server_artifact=server.zip
embedded_ml_sdk_artifact=embedded_ml_sdk.zip

### unpack transcoded c source files
unpack_embedded_ml_sdk() {
	echo "Unpacking embedded_ml_sdk into ${install_root}"
	cd ${working_dir}
	unzip ${working_dir}/${embedded_ml_sdk_artifact}
	mv ${working_dir}/embedded_ml_sdk  ${install_root}
}


### unpack transcoded c source files
unpack_server() {
	echo "Unpacking server into ${server_root}"
	cd ${working_dir}
	unzip ${working_dir}/${server_artifact}
        ls
        ls server/
	mv ${working_dir}/server  ${install_root}
}

### unpack transcoded c source files
compile_pywrappper() {
	echo "Making pywrapper library at ${install_root}"
	cd ${embedded_ml_sdk}/pywrapper
	make -j
}

install_server(){
    compile_classifiers
    cd ${server_root}
    #python manage.py initialize_directories; verify
    #python manage.py collectstatic --noinput; verify
}


compile_decision_tree() {
        cd ${embedded_ml_sdk}/classifiers/tree_ensemble
        make -j
        cp libclassifiers.so ${install_root}/lib/
}



compile_tinn() {
        cd ${embedded_ml_sdk}/classifiers/tinn
        make -j
        cp libtinn.so ${install_root}/lib/
}


compile_boosted_tree_ensemble() {
        cd ${embedded_ml_sdk}/classifiers/boosted_tree_ensemble
        make -j
        cp libgbtclassifiers.so ${install_root}/lib/
}


compile_pme() {
        cd ${embedded_ml_sdk}/classifiers/pme
        make setup SENSIML_SDK_PATH=${embedded_ml_sdk}/
	make SENSIML_SDK_PATH=${embedded_ml_sdk}/ -j
        cp libpmeclassifier.so ${install_root}/lib/

}

compile_bonsai() {
        cd ${embedded_ml_sdk}/classifiers/bonsai
        make setup
        make -j
        cp libbonsaiclassifier.so ${install_root}/lib/

}


compile_linear_regression() {
        cd ${embedded_ml_sdk}/classifiers/linear_regression
        make setup
        make -j
        cp liblinregression.so ${install_root}/lib/

}



compile_classifiers() {
	compile_decision_tree
	compile_tinn
	compile_boosted_tree_ensemble
	compile_pme
	compile_bonsai
        compile_linear_regression
}

mkdir $install_root
mkdir $server_root
mkdir $kbkernel_root
mkdir $working_dir

cd ${working_dir}
whoami
mv /home/sml-app/artifacts.zip .
unzip artifacts.zip

unpack_embedded_ml_sdk
unpack_server
install_server
compile_pywrappper
cd /home/sml-app
chown -R sml-app:sml-app *
chown sml-app:sml-app .env.sml
chown sml-app:sml-app ./setup_database.sh
