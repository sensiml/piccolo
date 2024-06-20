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

from django.conf import settings
from abc import abstractmethod


class DockerBase(object):
    """Override these functions in any new docker type class to work with docker runner"""

    use_fargate = False
    compile_tensorflow = False

    def get_task_cpu(self):
        if self.compile_tensorflow:
            return settings.AWS_DOCKER_CONTAINER_CPU_TENSORFLOW

        return settings.AWS_DOCKER_CONTAINER_CPU

    def get_task_ram(self):
        if self.compile_tensorflow:
            return settings.AWS_DOCKER_CONTAINER_RAM_TENSORFLOW

        return settings.AWS_DOCKER_CONTAINER_RAM

    def _clean_name(self, name):
        """sanitizes the container name so it is compatible with ecs"""
        return (
            name.replace(".", "-")
            .replace(" ", "-")
            .replace("---", "-")
            .replace("(", "")
            .replace(")", "")
        )

    def log_filter(self, log_stream):
        """
        Parses the log results that will be returned to the user.

        Only logs between LOG START/LOG STOP will be returend
        """

        file_data = ""
        recording = False
        for log in log_stream:
            log = log.rstrip()
            if log == "LOG STOP":
                recording = False
            if recording:
                file_data += log + "\n"
            if log == "LOG START":
                recording = True

        return file_data

    @abstractmethod
    def _get_build_prefix(self):
        """This is the prefix for the folder that will be generated"""

    @abstractmethod
    def _get_container_name(self, uuid=None):
        """This is the container name that will be used by docker runner"""

    @abstractmethod
    def _process_container_results(self, debug_flag):
        """describes how to process the results returned from the container"""

    @abstractmethod
    def parse_build_log_for_errors(self, filename):
        """parses the build logs that are generated and returns errors"""

    @abstractmethod
    def get_container_timeout_setting(self):
        """returns the timeout for this particular container"""

    @abstractmethod
    def get_execution_params(self, build_type, application):
        """generates the execution parameters that will be used by the docker container."""
