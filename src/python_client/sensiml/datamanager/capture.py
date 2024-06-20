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

from __future__ import annotations
import datetime
import logging
import os.path
import time


from requests import Response
from typing import Optional, TYPE_CHECKING
import sensiml.base.utility as utility
from sensiml.base.exceptions import CaptureUploadFailureError
from sensiml.datamanager.label_relationship import SegmentSet
from sensiml.datamanager.metadata_relationship import MetadataRelationshipSet
from sensiml.datamanager.capture_video import CaptureVideoSet

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project
    from sensiml.datamanager.capture import Capture

EXCEPTION_STATES = frozenset(["FAILURE", "RETRY", "REVOKED"])

# Custom ready states because sync or nonexistent task state is set to NONE
READY_STATES = frozenset(["FAILURE", "REVOKED", "SUCCESS", None])

# Custom unready states because celery's PENDING state is unreliable
UNREADY_STATES = frozenset(["STARTED", "RECEIVED", "RETRY", "SENT"])


logger = logging.getLogger(__name__)


class CaptureTaskFailedError(Exception):
    """Raised if Capture task failed"""


class Capture(object):
    """Base class for a Capture."""

    def __init__(
        self,
        connection: Connection,
        project: Project,
        filename: str = "",
        path: str = "",
        uuid: str = "",
        capture_configuration_uuid: Optional[str] = None,
        capture_info: Optional[dict] = None,
        created_at: Optional[str] = None,
        **kwargs,
    ):
        """Initialize a Capture instance."""
        self._connection = connection
        self._project = project
        self._filename = filename
        self._created_at = created_at
        self._path = path
        self._uuid = uuid
        self._capture_info = capture_info if capture_info else {}
        self._metadata = MetadataRelationshipSet(
            self._connection, self._project, self, initialize_set=False
        )
        self._capture_videos = CaptureVideoSet(
            self._connection, self._project, self, initialize_set=False
        )
        self._segements = SegmentSet(
            self._connection, self._project, self, initialize_set=False
        )

    @property
    def filetype(self) -> str:
        if ".csv" in self._filename[-4:]:
            return ".csv"
        elif ".wav" in self._filename[-4:]:
            return ".wav"
        raise Exception("Unknown file type.")

    @property
    def uuid(self) -> str:
        """Auto generated unique identifier for the Capture object"""
        return self._uuid

    @property
    def filename(self) -> str:
        return self._filename

    @filename.setter
    def filename(self, value: str):
        self._filename = value

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @created_at.setter
    def created_at(self, value: str):
        if value:
            self._created_at = datetime.datetime.strptime(
                value[:-6], "%Y-%m-%dT%H:%M:%S.%f"
            )

    @property
    def path(self) -> str:
        """The local or server path to the Capture file data"""
        return self._path

    @path.setter
    def path(self, value: str):
        self._path = value

    @property
    def metadataset(self) -> MetadataRelationshipSet:
        return self._metadata

    @property
    def segmentset(self) -> SegmentSet:
        return self._segmentset

    @property
    def capture_info(self) -> dict:
        """Info about capture"""
        return self._capture_info

    @property
    def capture_videos(self) -> CaptureVideoSet:
        return self._capture_videos

    @capture_info.setter
    def capture_info(self, value: dict):
        self._capture_info = {}
        if value.get("CalculatedSampleRate", None) is not None:
            self._capture_info["calculated_sample_rate"] = value.get(
                "CalculatedSampleRate"
            )
        if value.get("SampleRate", None) is not None:
            self._capture_info["set_sample_rate"] = value.get("SampleRate", None)
        if value.get("capture_configuration_uuid", None) is not None:
            self._capture_info["capture_configuration_uuid"] = value.get(
                "capture_configuration_uuid", None
            )

        if not self._capture_info:
            self._capture_info = {}

    @property
    def ready(self) -> bool:
        """Returns if Capture (Capture) is ready or not

        Returns:
            Boolean: True if task is ready or False if task is pending. Raises Exception if task failed.
        """
        url = f"project/{self._project.uuid}/capture/{self.uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if (
            not response_data["task_state"]
            or response_data["task_state"] in READY_STATES
        ):
            return True

        if response_data["task_state"] in EXCEPTION_STATES:
            logger.error(response_data["task_result"])
            raise CaptureTaskFailedError()

        return False

    def await_ready(self, sleep: int = 3, retries: int = 0) -> bool:
        """Blocks until Capture (Capture) is ready or failed

        Args:
            sleep (int): Number of seconds to sleep between polling
            retries (int): Number of times to retry before unblocking and returning False.
                           Use 0 for infinite.

        Returns:
            None or raises CaptureUploadFailureError if upload failed.
        """
        try_ = 0
        url = f"project/{self._project.uuid}/capture/{self.uuid}/"

        while retries == 0 or try_ <= retries:
            try_ += 1
            response = self._connection.request("get", url)
            response_data, err = utility.check_server_response(response)
            # Uses custom UNREADY_STATES because we do NOT want to sleep forever on "PENDING"
            if response_data["task_state"] in UNREADY_STATES:
                time.sleep(sleep)
            elif (
                not response_data["task_state"]
                or response_data["task_state"] in READY_STATES
            ):
                return True
            else:
                raise CaptureUploadFailureError(response_data["task_result"])

    def insert(self, asynchronous: bool = False) -> Response:
        """Calls the REST API to insert a new Capture."""
        url = f"project/{self._project.uuid}/capture/"
        capture_info = {"name": self.filename, "asynchronous": asynchronous}
        if self.capture_info is not None:
            capture_info.update(self._capture_info)
        response = self._connection.file_request(url, self.path, capture_info, "rb")
        response_data, err = utility.check_server_response(response)
        if err is False:
            self._uuid = response_data["uuid"]
            self._capture_info.update(response_data)

        return response

    def update(self) -> Response:
        """Calls the REST API to update the capture."""
        url = f"project/{self._project.uuid}/capture/{self._uuid}/"

        capture_info = {"name": self.filename}
        if self._capture_info is not None:
            capture_info.update(self._capture_info)
        if self.path:
            response = self._connection.file_request(
                url, self.path, capture_info, "rb", "patch"
            )
        else:
            response = self._connection.request(url, "post", capture_info)
        utility.check_server_response(response)

        return response

    def delete(self) -> Response:
        """Calls the REST API to delete the capture from the server."""
        url = f"project/{self._project.uuid}/capture/{self._uuid}/"
        response = self._connection.request("delete", url)
        utility.check_server_response(response)

        return response

    def refresh(self) -> Response:
        """Calls the REST API and self populates properties from the server."""
        url = f"project/{self._project.uuid}/capture/{self._uuid}/"
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.filename = response_data["name"]

        return response

    def download(self, outdir: str = None) -> Response:
        """Downloads the capture file from the server."""
        url = f"project/{self._project.uuid}/capture/{self._uuid}/file/"
        response = self._connection.request("get", url)

        if outdir is None:
            outdir = "./"

        if self.filetype == ".csv":
            with open(os.path.join(outdir, self._filename), "w") as out:
                out.write(response.text)
                print(f"Capture saved to {os.path.join(outdir, self._filename)}")

        elif self.filetype == ".wav":
            with open(os.path.join(outdir, self._filename), "wb") as out:
                out.write(response.content)
                print(f"Capture saved to {os.path.join(outdir, self._filename)}")

        else:
            raise Exception("Unknown file type")

        return response

    @classmethod
    def initialize_from_dict(cls, capture_dict: dict) -> Capture:
        """Reads a dictionary or properties and populates a single capture.

        Args:
            capture_dict (dict): contains the capture's 'name' property

        Returns:
            capture object
        """
        assert isinstance(capture_dict, dict)
        new_dict = capture_dict.copy()
        new_dict["filename"] = str(
            new_dict.get(
                "filename",  # capture object attribute
                new_dict.pop("name", ""),  # API object key
            )
        )
        return Capture(**new_dict)

    # methods to make this instance hashable and comparable
    def __hash__(self):
        return hash(self._uuid)

    def __eq__(self, other):
        return (self._uuid,) == (other._uuid,)

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        return (self._uuid,) < (other._uuid,)

    def __gt__(self, other):
        return (self._uuid,) > (other._uuid,)

    def __le__(self, other):
        return (self < other) or (self == other)

    def __ge__(self, other):
        return (self > other) or (self == other)


class BackgroundCapture(object):
    """Base class for a Capture."""

    def __init__(
        self,
        connection: Connection,
        filename: str = "",
        path: str = "",
        uuid: str = "",
        capture_configuration_uuid: Optional[str] = None,
        capture_info: Optional[dict] = None,
        created_at: Optional[str] = None,
        **kwargs,
    ):
        """Initialize a BackgroundCapture instance."""

        self._connection = connection
        self._filename = filename
        self._created_at = created_at
        self._path = path
        self._uuid = uuid
        self._capture_info = capture_info

        for k, v in kwargs.items():
            setattr(self, "_" + k, v)

    @property
    def filetype(self) -> str:
        if ".csv" in self._filename[-4:]:
            return ".csv"
        elif ".wav" in self._filename[-4:]:
            return ".wav"
        raise Exception("Unknown file type.")

    def download(self, outdir: str = None) -> Response:
        """Downloads the capture file from the server.

        Args:
            outdir (str, '.'): output directory

        """
        url = f"background-capture/{self._uuid}/file/"
        response = self._connection.request("get", url)

        if outdir is None:
            outdir = "./"

        if response.status_code != 200:
            print(f"Background Capture not found ! \n uuid : {self._uuid}")
            print(response)
            return response

        if self.filetype == ".csv":
            with open(os.path.join(outdir, self._filename), "w") as out:
                out.write(response.text)
                print(
                    f"Background Capture saved as {os.path.join(outdir, self._filename)}"
                )

        elif self.filetype == ".wav":
            with open(os.path.join(outdir, self._filename), "wb") as out:
                out.write(response.content)
                print(f"Capture saved to {os.path.join(outdir, self._filename)}")

        return response
