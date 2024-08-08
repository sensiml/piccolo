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

import json
import traceback

import requests
from django.conf import settings


class LogHandler:
    """
    Log Format
    1	Type	→ Debug, Info, Error
    2	Category	→ Pipileine, Knowledge Pack
    3	Key→ UUID
    4	Public→ Y/N
    5	Message
    """

    def __init__(self, logger, header=None):
        self._logger = logger
        self._header = header
        self.valid_categories = [
            "PID",
            "KPID",
            "ACCESS",
            "datamanager",
            "GID",
            "CID",
            "QID",
            "pipeline_utils",
            "manager",
            "autoscaling",
            "classifier",
        ]

    @property
    def header(self):
        """Header object to use for pipelin"""
        return self._header

    @header.setter
    def header(self, value):
        if not isinstance(value, dict):
            raise Exception("header must be a dict.")
        self._header = value

    def __merge(self, log_dict):

        if self._header != None:
            return json.dumps({**self._header, **self._encode_exception(log_dict)})

        log_dict = self._encode_exception(log_dict)

        try:
            return json.dumps(log_dict)
        except:
            return str(log_dict)

    def _encode_exception(self, log_dict):
        for k in log_dict:
            if isinstance(log_dict[k], Exception):
                e = log_dict[k]
                log_dict[k] = {
                    "error_message": str(e),
                    "traceback": "\n".join(traceback.format_tb(e.__traceback__)),
                }

        return log_dict

    def _validate_category(self, message):
        if not message.get("log_type", None):
            raise Exception("Invalid Category")

        if message["log_type"] not in self.valid_categories:
            raise Exception("Invalid Category")

    def _validate_uuid(self, message):

        if message["log_type"] in ["KPID", "PID"] and not (
            message.get("UUID") or message.get("sandbox_uuid")
        ):
            raise Exception("No UUID Provided")

    def userlog(
        self,
        message,
        public=True,
    ):
        message.update({"public": public, "level": "info"})
        self._validate_category(message)
        self._validate_uuid(message)
        self._logger.info(self.__merge(message))

    def errorlog(
        self,
        message,
        public=True,
    ):
        message.update({"public": public, "level": "error"})
        self._validate_category(message)
        self._validate_uuid(message)
        self._logger.error(self.__merge(message))

    def debug(self, message, public=False):
        message.update({"public": public, "level": "debug"})
        self._validate_category(message)
        self._validate_uuid(message)
        self._logger.debug(self.__merge(message))

    def info(self, message, public=False):
        message.update({"public": public, "level": "info"})
        self._validate_category(message)
        self._validate_uuid(message)
        self._logger.info(self.__merge(message))

    def warn(self, message, public=False):
        message.update({"public": public, "level": "warn"})
        self._validate_category(message)
        self._validate_uuid(message)
        self._logger.warn(self.__merge(message))

    def error(self, message, public=False):
        message.update({"public": public, "level": "error"})
        self._validate_category(message)
        self._validate_uuid(message)
        self._logger.error(self.__merge(message))

    def slack(self, message, public=False):
        message.update({"public": public, "level": "error"})
        self._validate_category(message)
        self._validate_uuid(message)

        formatted_text = f"```{json.dumps(message, indent = 2)}```"
        if settings.SLACK_WEBHOOK_API_URL:
            return requests.post(
                url=settings.SLACK_WEBHOOK_API_URL,
                json={"text": formatted_text},
                timeout=5,
            )

        return None

    def dev(self, message):
        self._logger.debug(message)
