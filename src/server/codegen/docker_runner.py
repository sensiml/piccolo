"""
Copyright 2017-2024 SensiML Corporation

This file is part of SensiML™ Piccolo AI™.

SensiML Piccolo AI is free software: you can redistribute it and/or
modify it under the terms of the GNU Affero General Public License
as published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

SensiML Piccolo AI is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>.
"""

import getpass
import json
import logging
import os
import time
from abc import abstractmethod
import boto3
import docker
from botocore.exceptions import ClientError, WaiterError
from codegen.docker_base import DockerBase
from datamanager import exceptions
from datamanager.models import KnowledgePack
from datamanager.datastore import get_datastore
from django.conf import settings
from requests.exceptions import ConnectionError, ReadTimeout
from codegen.docker_libtensorflow import DockerRunnerLibTensorflowMixin
from codegen.docker_libsensiml import DockerRunnerSensiMLMixin
from codegen.docker_errors import (
    CompilationErrorException,
    ExitCodeNonZeroException,
)

try:
    from pwd import getpwnam
except ImportError:

    def getpwnam(*args, **kwargs):
        class pw:
            pw_uid = 501

        return pw


from logger.log_handler import LogHandler

logger = LogHandler(logging.getLogger(__name__))


class DockerRunnerLocal(DockerBase):
    def __init__(
        self, root_dir, uuid, task_id, debug, platform, device_config, obj=None
    ):
        self.obj = obj if obj else KnowledgePack.objects.get(uuid=uuid)
        self.uuid = str(uuid)
        self.task_id = str(task_id)
        self.root_dir = root_dir
        self.debug_flag = "d" if debug else "p"
        self.device_config = device_config
        self.platform = platform
        if settings.INSIDE_LOCAL_DOCKER:
            self.mount_directory = f"/data/datamanager/codegen/{self.uuid}/"
        else:
            self.mount_directory = "/codegen_files/"

        if os.name == "posix":
            self.user_id = getpwnam(getpass.getuser()).pw_uid
        else:
            # windows doesn't really care.
            self.user_id = 1000

    def _delete_existing_container(self, client, container_name):
        existing_containers = client.api.containers(all=True)

        for container in existing_containers:
            if str(container["Names"][0]).strip(
                "\\/"
            ) == container_name and "Up" not in str(container["Status"]):
                client.api.remove_container(resource_id=container.get("Id"))

    def build_code_bin(self, build_type, application):

        execution_params = self.get_execution_params(build_type, application)

        logger.debug(
            {
                "message": "&&&&&&&&& BUILDING LOCALLY &&&&&&&&&&&&",
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        return_path = ""

        client = docker.from_env()

        container_name = self._get_container_name(uuid=self.uuid)
        docker_name = self.platform.get_docker_image()

        # Just delete Existing container
        self._delete_existing_container(client, container_name)

        logger.debug(
            {
                "message": json.dumps(execution_params),
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        if settings.INSIDE_LOCAL_DOCKER:
            bind = [f"{settings.LOCAL_DOCKER_SERVER_DATA_VOLUME_NAME}:/data"]
        else:
            bind = {
                self.root_dir: {
                    "bind": self.mount_directory,
                    "mode": "rw",
                }
            }

        container_host_cfg = client.api.create_host_config(
            binds=bind, cpu_quota=settings.AWS_DOCKER_CONTAINER_CPU_LIMIT
        )

        logger.debug(
            {
                "message": {
                    "name": container_name,
                    "image": docker_name,
                    "host_config": container_host_cfg,
                },
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        env_vars = [
            {"name": "AWS_S3_ACCESS", "value": "LOCAL"},
            {"name": "AWS_S3_SEC", "value": "MOUNT"},
            {"name": "KP_UUID", "value": execution_params["uuid"]},
            {"name": "BUCKET_NAME", "value": "NO S3"},
            {
                "name": "BUILD_SCRIPT_NAME",
                "value": execution_params.get("build_script_name", "build.sh"),
            },
        ]

        env_vars.extend(self.platform.get_application_environment())
        env_list = list()
        for e in env_vars:
            env_list.append("{}={}".format(e["name"], e["value"]))

        # https://docker-py.readthedocs.io/en/stable/api.html
        container_to_run = client.api.create_container(
            name=container_name,
            image=docker_name,
            entrypoint="/bin/bash",
            command="/run_build.sh",
            # volumes=[self.mount_directory],
            host_config=container_host_cfg,
            environment=env_list,
        )

        logger.debug(
            {
                "message": container_to_run,
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        client.api.start(container=container_to_run.get("Id"))

        # Wait for the container to exit. Will
        try:
            container_returns = client.api.wait(
                container=container_to_run.get("Id"),
                timeout=self.get_container_timeout_setting(),
            )
        except (ReadTimeout, ConnectionError):
            client.api.kill(container=container_to_run.get("Id"))
            raise Exception("Running unit test reach execution limit.")

        with open(
            os.path.join(
                self.root_dir, "{}_build.log".format(self._get_build_prefix())
            ),
            "wb",
        ) as buildlog:
            buildlog.write(
                client.api.logs(container=container_to_run.get("Id"), tail="all")
            )

        self.parse_build_log_for_errors(
            "{0}/{1}_build.log".format(self.root_dir, self._get_build_prefix())
        )

        if container_returns["StatusCode"] == 0:
            try:
                return_path = self._process_container_results(self.debug_flag)
            except:
                raise exceptions.KnowledgePackGenerationError(
                    "Failed to generate output!"
                )
            finally:
                # Remove container on success. Maybe just do it anyway.
                client.api.remove_container(resource_id=container_to_run.get("Id"))
        elif container_returns["StatusCode"] == 127 and settings.INSIDE_LOCAL_DOCKER:
            raise ExitCodeNonZeroException(
                f"Model data has missing some files. Please, check the data volume name."
            )
        else:
            raise ExitCodeNonZeroException(container_returns)

        return return_path

    def get_build_log_path(self):
        return "{0}/{1}_build.log".format(self.root_dir, self._get_build_prefix())


def get_docker_runner(docker_type: str):

    DockerRunnerBaseMixin = DockerRunnerLocal

    if docker_type == "tensorflow":

        class DockerRunner(DockerRunnerLibTensorflowMixin, DockerRunnerBaseMixin):
            pass

    elif docker_type == "sensiml":

        class DockerRunner(DockerRunnerSensiMLMixin, DockerRunnerBaseMixin):
            pass

    else:
        raise ValueError("Invalid docker_type")

    return DockerRunner
