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
import logging
import json
import os

from typing import Optional, TYPE_CHECKING
import sensiml.base.utility as utility
from sensiml.datamanager.base import Base, BaseSet
from requests import Response

if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project
    from sensiml.datamanager.capture import Capture

logger = logging.getLogger(__name__)


class CaptureVideo(Base):
    _fields = [
        "uuid",
        "name",
        "file_size",
        "keypoints",
        "video",
        "created_at",
        "last_modified",
    ]

    _read_only_fields = [
        "uuid",
        "name",
        "file_size",
        "video",
        "created_at",
        "last_modified",
    ]

    def __init__(self, connection: Connection, project: Project, capture: Capture):
        """Initialize a capture video object.
        Args:
            connection
            project
            capture
        """
        self._connection = connection
        self._project = project
        self._capture = capture

        self._uuid = ""
        self._name = ""
        self._video = ""
        self._keypoints = {}

    @property
    def detail_url(self):
        """Overwrite this property in the subclass for its base url"""
        return f"project/{self._project.uuid}/capture/{self._capture.uuid}/video/{self.uuid}/"

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def video(self):
        return self._video

    @video.setter
    def video(self, value):
        self._video = value

    @property
    def keypoints(self):
        return self._keypoints

    @keypoints.setter
    def keypoints(self, value):
        self._keypoints = value

    def insert(self) -> Response:
        """Calls the REST API and inserts a video object onto the server using the local object's properties."""
        url = f"project/{self._project.uuid}/capture/{self._capture.uuid}/video/"

        data = {"keypoints": json.dumps(self.keypoints)}
        response = self._connection.file_request(url, self.video, data, "rb")

        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response

    def download(self, outdir: Optional[str] = None) -> Response:
        """Downloads the capture video file from the server.

        Args:
            outdir (str, '.'): output directory

        """
        url = f"project/{self._project.uuid}/capture/{self._capture.uuid}/video/{self.uuid}/video/"

        if outdir is None:
            outdir = "./"

        response = self._connection.request("get", url)

        with open(os.path.join(outdir, self._name), "wb") as out:
            out.write(response.content)
            print(f"Capture video saved to {os.path.join(outdir, self._name)}")

        return response


class CaptureVideoSet(BaseSet):
    def __init__(
        self,
        connection: Connection,
        project: Project,
        capture: Capture,
        initialize_set: bool = True,
    ):
        """
        Args:
            connection
            project
            capture
        """
        self._connection = connection
        self._project = project
        self._capture = capture
        self._set = None
        self._objclass = CaptureVideo
        self._attr_key = "value"

        if initialize_set:
            self.refresh()

    @property
    def get_set_url(self) -> str:
        # Query the server and get the json
        return f"/project/{self._project.uuid}/capture/{self._capture.uuid}/video/"

    @property
    def capture_videos(self):
        return self.objs

    def _new_obj_from_dict(self, data) -> CaptureVideo:
        obj = CaptureVideo(self._connection, self._project, self._capture)
        obj.initialize_from_dict(data)

        return obj

    def get_capture_video_by_name(self, name) -> CaptureVideo:
        return next((x for x in self.capture_videos if x.uuid == name), None)

    def get_capture_video_by_uuid(self, uuid) -> CaptureVideo:
        return next((x for x in self.capture_videos if x.uuid == uuid), None)

    def new_capture_video(self, data) -> CaptureVideo:
        """Initialize new capture video instance

        Args:
            data (dict): { keypoints: {}, video: "path" }

        """
        obj = CaptureVideo(self._connection, self._project, self._capture)
        if data:
            obj.initialize_from_dict(data)
        return obj
