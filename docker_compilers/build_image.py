#!/usr/bin/env python
import docker
from docker.errors import BuildError
import json
import os, subprocess
import argparse
from icecream import ic
from shutil import copyfile
import boto3
import base64


def get_docker_client(profile_name):

    docker_client = docker.from_env()
    session = boto3.Session(profile_name=profile_name)
    client = session.client("ecr", region_name="us-west-2")

    token = client.get_authorization_token()
    username, password = (
        base64.b64decode(token["authorizationData"][0]["authorizationToken"])
        .decode()
        .split(":")
    )
    registry = token["authorizationData"][0]["proxyEndpoint"]

    docker_client.login(username, password, registry=registry)

    return docker_client


def _copy_run_build(docker_path):
    run_build_path = os.path.join(docker_path, "run_build.sh")
    if not os.path.exists(run_build_path):
        copyfile("./sensiml_base/run_build.sh", run_build_path)
        subprocess.check_call(["chmod", "+x", run_build_path])
        return True

    return False


def get_repositor_list(registryId, profile_name):

    session = boto3.Session(profile_name=profile_name)
    client = session.client("ecr", region_name="us-west-2")

    response = client.describe_repositories(registryId=registryId)

    return [x["repositoryName"] for x in response["repositories"]]


def create_repository(registryId, repositoryName, profile_name):

    session = boto3.Session(profile_name=profile_name)
    client = session.client("ecr", region_name="us-west-2")

    response = client.create_repository(
        registryId=registryId,
        repositoryName=repositoryName,
        imageTagMutability="MUTABLE",
        imageScanningConfiguration={"scanOnPush": True},
        encryptionConfiguration={
            "encryptionType": "AES256",
        },
    )

    return response


def _get_input_args():
    parser = argparse.ArgumentParser(
        description="Builds all images in the repository. To build a single image use the --in_dir option."
    )

    parser.add_argument(
        "--in_dir",
        "-i",
        dest="in_dir",
        required=False,
        help="Choose directory to build from",
        default="",
    )

    parser.add_argument("--tag", dest="tag", required=False, help="Image tag")

    parser.add_argument(
        "--push_image",
        "-p",
        action="store_true",
        dest="push_image",
        required=False,
        help="Push Images Directly to repository",
        default=False,
    )

    parser.add_argument(
        "--build_image",
        "-b",
        action="store_true",
        dest="build_image",
        required=False,
        help="Build image to local repo",
        default=False,
    )

    parser.add_argument(
        "--tag_image",
        "-t",
        action="store_true",
        dest="tag_image",
        required=False,
        help="Tag image to local repo",
        default=False,
    )

    parser.add_argument(
        "--profile_name",
        dest="profile_name",
        required=False,
        help="Set the profile name to use when connecting to AWS",
        default="default",
    )
    parser.add_argument(
        "--registry_id",
        dest="registry_id",
        required=False,
        help="Set the registry ID to use when pushing to AWS ECR",
        default="",
    )

    return parser.parse_args()


def make_image(image_path, repository, tag, **build_args):

    if not tag:
        raise Exception("Tag must be specified", image_path, repository, tag)

    run_build_copied = _copy_run_build(image_path)
    dc = docker.from_env()

    ic(build_args)

    tag_name = f"{repository}:{tag}"
    print(f"Building {tag_name}")
    print("At dir", image_path)

    print(build_args)
    try:
        img = dc.images.build(
            path=image_path,
            dockerfile=os.path.join(image_path, "Dockerfile"),
            tag=tag_name,
            buildargs=build_args,
            rm=True,
            quiet=False,
        )
        print(img)
    except Exception as e:
        if run_build_copied:
            os.remove(os.path.join(image_path, "run_build.sh"))
        if hasattr(e, "build_log"):
            ic(e.build_log)
        raise e

    if run_build_copied:
        os.remove(os.path.join(image_path, "run_build.sh"))

    return img


def main(in_dir, build_image, tag_image, push_image, registryId, profile_name=None):

    build_dir = os.path.abspath(in_dir)
    version = os.path.basename(in_dir)

    print("BUILD_DIR", build_dir)
    print("VERSION", version)

    if os.path.exists(f"{build_dir}/arguments.json"):
        build_list = json.load(open(f"{build_dir}/arguments.json", "r"))

        for image in build_list:
            ic(image)

            if image["repository"].split("/")[0] == "sensiml":
                registry = "sensiml"
            else:
                registry = (
                    f"{registryId}.dkr.ecr.us-west-2.amazonaws.com"
                    if registryId
                    else ""
                )

            image_tag = version if not image["tag"] else f'{image["tag"]}-{version}'

            if build_image:
                make_image(
                    build_dir,
                    image["repository"],
                    image_tag,
                    **image["build_args"],
                )

            if tag_image:

                if not registryId:
                    raise Exception("Registry must be suppplied to tag image")

                dc = get_docker_client(profile_name)

                df_image = dc.images.get(f"{image['repository']}:{image_tag}")

                df_image.tag(f"{registry}/{image['repository']}", tag=image_tag)

            if push_image:

                dc = get_docker_client(profile_name)

                if not registryId:
                    raise Exception("Registry must be suppplied to push image")

                if registry == "sensiml":
                    for line in dc.api.push(
                        repository=f"{image['repository']}", tag=image_tag, stream=True
                    ):
                        print(str(line))
                else:
                    repository_list = get_repositor_list(registryId, profile_name)
                    if image["repository"] not in repository_list:
                        create_repository(registryId, image["repository"], profile_name)
                    print(
                        "Pushing image", f"{registry}/{image['repository']}:{image_tag}"
                    )
                    for line in dc.api.push(
                        repository=f"{registry}/{image['repository']}",
                        tag=image_tag,
                        stream=True,
                    ):
                        print(str(line))


if __name__ == "__main__":

    input_args = _get_input_args()

    if input_args.in_dir:
        main(
            input_args.in_dir,
            input_args.build_image,
            input_args.tag_image,
            input_args.push_image,
            registryId=input_args.registry_id,
            profile_name=input_args.profile_name,
        )

    else:
        for dirName, subdirList, fileList in os.walk("./"):
            if "arguments.json" in fileList:
                print("Found directory: %s" % dirName)
                try:
                    main(
                        dirName,
                        input_args.build_image,
                        input_args.tag_image,
                        input_args.push_image,
                        registryId=input_args.registry_id,
                        profile_name=input_args.profile_name,
                    )
                except Exception as e:
                    print(e)
