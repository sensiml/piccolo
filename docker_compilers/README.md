This repository contains Dockerfiles to build our base images. The following instructions detail how to build the images


To build all images from scratch

1. delete all current local images and containers

	docker stop $(docker ps -aq)
	docker rm $(docker ps -aq)
	docker rmi $(docker images -a -q) -f

2. create the base images

	python build_image.py --in_dir=sensiml_base -b -t -p --registry_id=XXXXX --profile_name=XXXXX
	python build_image.py --in_dir=armgcc_base  -b -t -p --registry_id=XXXXX --profile_name=XXXXX

3. create the main images

	cd docker_files
	python build_image.py -b=True 

4. to tag and push images

	python build_image.py -t=True -p=True  --registry_id=XXXXX --profile_name=XXXXX


To build a single images

	cd docker_files
	python build_image.py --in_dir=<name_of_dir>  -b=True

To tag a single image

	python build_image.py --in_dir=<name_of_dir>  -t=True --registry_id=XXXXX --profile_name=XXXXX

To push files after build

	python build_image.py  -p=True --registry_id=XXXXX --profile_name=XXXXX



#### Folder archictecture

In order to verison our docker images to allow for images on dev and prod to be different. We have a version folder inside the named folder

This will create an image with the following {registryID}/{repository}:{tag}-{version}

