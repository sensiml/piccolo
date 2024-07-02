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
            bind = [f"{settings.LOCAL_DOCKER_SERVER_DATA_VOLUMNE_NAME}:/data"]
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
        else:
            raise ExitCodeNonZeroException(container_returns)

        return return_path

    def get_build_log_path(self):
        return "{0}/{1}_build.log".format(self.root_dir, self._get_build_prefix())


class DockerRunnerECS(DockerBase):
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
        self.mount_directory = "/codegen_files/"

        if os.name == "posix":
            self.user_id = getpwnam(getpass.getuser()).pw_uid
        else:
            # windows doesn't really care.
            self.user_id = 1000

        self._ecs = boto3.client(
            "ecs",
            region_name=settings.AWS_DOCKER_RUNNER_REGION,
            aws_access_key_id=settings.AWS_DOCKER_RUNNER_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_DOCKER_RUNNER_SECRET_KEY,
        )
        # Need S3 to run via docker on ecs.
        self._datastore = get_datastore(
            bucket=settings.AWS_CODEGEN_BUCKET_NAME,
            aws_access=settings.AWS_DOCKER_RUNNER_ACCESS_KEY,
            aws_secret=settings.AWS_DOCKER_RUNNER_SECRET_KEY,
        )

        self._cloud_logs = boto3.client(
            "logs",
            region_name=settings.AWS_DOCKER_RUNNER_REGION,
            aws_access_key_id=settings.AWS_DOCKER_RUNNER_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_DOCKER_RUNNER_SECRET_KEY,
        )

        logger.debug(
            {
                "message": " Successfully connected to ECS Docker Runner",
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

    def retrieve_remote_knowledgepack(self):

        self._datastore.get(
            key="{}/output_binary_name".format(self.uuid),
            file_path=os.path.join(self.root_dir, "output_binary_name"),
        )
        self._datastore.get(
            key="{}/codegen-compiled-output".format(self.uuid),
            file_path=os.path.join(self.root_dir, "codegen-compiled-output"),
        )

    @abstractmethod
    def _get_logstream_prefix(self):
        """get the logstream prefix for this caller"""

    @abstractmethod
    def _handle_ecs_build_failures(self):
        """this should handle parsing build failures and returning information about why it failed"""

    @abstractmethod
    def get_ecs_timeout_settings(self):
        """container timeout for ECS"""

    def _get_task_family(self, fargate=False):
        return self.platform.get_ecs_task_family(fargate=fargate)

    def get_build_log_path(self):
        return "{0}/{1}_build.log".format(self.root_dir, self._get_build_prefix())

    def _ecs_get_task_arn(self, fargate=False):
        task_family = self._get_task_family(fargate=fargate)

        if task_family is None:
            logger.errorlog(
                {
                    "message": "Failed to get task family",
                    "log_type": "KPID",
                    "UUID": self.uuid,
                    "task_id": self.task_id,
                }
            )
            raise CompilationErrorException("Failed to generate Knowledge Pack")
        try:
            task_defs = self._ecs.list_task_definitions(familyPrefix=str(task_family))
            if len(task_defs["taskDefinitionArns"]) == 0:
                logger.errorlog(
                    {
                        "message": f"Task definition doesn't exist. Contact SensiML support with platform {self.platform.name} and version {self.platform.version}",
                        "log_type": "KPID",
                        "UUID": self.uuid,
                        "task_id": self.task_id,
                    }
                )
                raise CompilationErrorException("Failed to generate Knowledge Pack")

            # the last item in the list returned is the most recent definition if there are multiple
            return task_defs["taskDefinitionArns"][-1]
        except ClientError as client_error:
            logger.errorlog(
                {
                    "message": str(client_error),
                    "log_type": "KPID",
                    "UUID": self.uuid,
                    "task_id": self.task_id,
                }
            )
            raise CompilationErrorException("Failed to generate Knowledge pack")

    def build_code_bin(self, build_type, application):
        """
        Builds the image using ECS container on AWS. In order to get the logs, an IAM user also needs
        CloudWatchEventsReadOnlyAccess AND CloudWatchLogsReadOnlyAccess in addition to the existing
        permissions found in containerServicePowerUser
        """

        logger.debug(
            {"message": "Building with ecs", "log_type": "KPID", "UUID": self.uuid}
        )

        execution_params = self.get_execution_params(build_type, application)

        self._datastore.zip_and_save_folder(self.root_dir, uuid=self.uuid)
        self._datastore.save_folder(
            self.root_dir,
            uuid=self.uuid,
            include_files=["build.sh", "build_tensorflow.sh", "execute.json"],
        )

        env_vars = [
            {"name": "KP_UUID", "value": execution_params["uuid"]},
            {"name": "BUCKET_NAME", "value": execution_params["bucket_name"]},
            {
                "name": "BUILD_SCRIPT_NAME",
                "value": execution_params.get("build_script_name", "build.sh"),
            },
        ]

        if execution_params.get("aws_access"):
            env_vars.extend(
                [
                    {"name": "AWS_S3_ACCESS", "value": execution_params["aws_access"]},
                    {"name": "AWS_S3_SEC", "value": execution_params["aws_sec"]},
                ]
            )
        else:
            env_vars.extend(
                [
                    {"name": "AWS_S3_ACCESS", "value": "IAM_PROFILE"},
                    {"name": "AWS_S3_SEC", "value": "IAM_PROFILE"},
                ]
            )

        env_vars.extend(self.platform.get_application_environment())
        container_task_override = [
            {
                "name": self._get_container_name(),
                "cpu": self.get_task_cpu(),
                "memory": self.get_task_ram(),
                "environment": env_vars,
            }
        ]

        logger.debug(
            {
                "message": "Container Task Override",
                "data": container_task_override,
                "log_type": "KPID",
                "UUID": self.uuid,
            }
        )

        retry = 10
        while retry:
            if settings.AWS_DOCKER_TASK_USE_FARGATE and self.platform.name not in [
                "Windows x86_64",
                "x86 GCC Generic",
            ]:
                task_definition_arn = self._ecs_get_task_arn(
                    fargate=settings.AWS_DOCKER_TASK_USE_FARGATE
                )
                cluster_name = settings.AWS_DOCKER_RUNNER_FARGATE_CLUSTER_NAME
                task_values = self._ecs.run_task(
                    cluster=cluster_name,
                    launchType="FARGATE",
                    taskDefinition=task_definition_arn,
                    networkConfiguration={
                        "awsvpcConfiguration": {
                            "subnets": [
                                settings.AWS_DOCKER_RUNNER_TASK_SUBNETS
                            ],  # Replace 'your_subnet_id' with the subnet ID where the task should run
                            "securityGroups": [
                                settings.AWS_DOCKER_RUNNER_TASK_SECURITY_GROUP
                            ],
                            "assignPublicIp": "ENABLED",
                        }
                    },
                    overrides={
                        "cpu": str(self.get_task_cpu()),
                        "memory": str(self.get_task_ram()),
                        "containerOverrides": container_task_override,
                    },
                )
            else:
                task_definition_arn = self._ecs_get_task_arn(fargate=False)
                cluster_name = settings.AWS_DOCKER_RUNNER_CLUSTER_NAME
                task_values = self._ecs.run_task(
                    cluster=cluster_name,
                    taskDefinition=task_definition_arn,
                    overrides={
                        "cpu": str(self.get_task_cpu()),
                        "memory": str(self.get_task_ram()),
                        "containerOverrides": container_task_override,
                    },
                )

            logger.debug(
                {"message": task_values, "log_type": "KPID", "UUID": self.uuid}
            )
            if task_values.get("tasks", None) is None or len(task_values["tasks"]) == 0:
                failures = task_values.get("failures", "")
                if failures[0]["reason"] == "RESOURCE:CPU":
                    retry -= 1
                    if retry == 0:
                        raise CompilationErrorException(
                            "Resources unavailable, try again in a few minutes."
                        )
                    time.sleep(20)
                    continue

                logger.error(
                    {
                        "message": failures,
                        "log_type": "KPID",
                        "UUID": self.uuid,
                        "task_id": self.task_id,
                    }
                )
                raise CompilationErrorException("Knowledge Pack failed to compile.")

            break

        task_arn = task_values["tasks"][0]["taskArn"]
        ecs_task_id = task_arn.split("/")[-1]

        waiter = self._ecs.get_waiter("tasks_stopped")
        self.obj.logs = "{prefix_name}/{container_name}/{ecs_task_id}".format(
            prefix_name=self._get_logstream_prefix(),
            container_name=self._get_container_name(),
            ecs_task_id=ecs_task_id,
        )
        self.obj.save(update_fields=["logs"])

        try:
            waiter.wait(
                cluster=cluster_name,
                tasks=[ecs_task_id],
                WaiterConfig=self.get_ecs_timeout_settings(),
            )
        except WaiterError:
            self._ecs.stop_task(cluster=cluster_name, task=ecs_task_id)
            raise Exception("Execution time limit exceeded.")

        task_description = self._ecs.describe_tasks(
            cluster=cluster_name, tasks=[ecs_task_id]
        )

        exit_code = task_description["tasks"][0]["containers"][0].get("exitCode", 1)

        if exit_code != 0:
            self._datastore.remove_folder(str(self.uuid))
            self._handle_ecs_build_failures()
            raise ExitCodeNonZeroException(exit_code)

        try:
            self.retrieve_remote_knowledgepack()
        except:
            logger.error(
                {
                    "message": "Compiled output not found!",
                    "log_type": "KPID",
                    "UUID": self.uuid,
                    "task_id": self.task_id,
                }
            )
            self._handle_ecs_build_failures()
        finally:
            self._datastore.remove_folder(str(self.uuid))

        return self._process_container_results(debug_flag=self.debug_flag)


def get_docker_runner(docker_type: str):

    if settings.CODEGEN_USE_ECS_FOR_DOCKER:
        DockerRunnerBaseMixin = DockerRunnerECS
    else:
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
