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

import sensiml.base.utility as utility
from sensiml.datamanager.base import Base, BaseSet
from sensiml.datamanager.label import Label
from sensiml.datamanager.labelvalue import LabelValue
from sensiml.datamanager.segmenter import Segmenter
from requests import Response

from typing import TYPE_CHECKING, Optional, Union


if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project
    from sensiml.datamanager.capture import Capture


logger = logging.getLogger(__name__)


class Segment(Base):
    """Base class for a label object."""

    _fields = [
        "uuid",
        "sample_start",
        "sample_end",
        "segmenter",
        "label",
        "label_value",
    ]

    _field_map = {
        "sample_start": "capture_sample_sequence_start",
        "sample_end": "capture_sample_sequence_end",
    }

    def __init__(
        self,
        connection: Connection,
        project: Project,
        capture: Capture,
        segmenter: Optional[Segmenter] = None,
        label: Optional[Label] = None,
        label_value: Optional[LabelValue] = None,
    ):
        """Initialize a metadata object.

        Args:
            connection
            project
            capture
        """
        super().__init__(connection)

        self._uuid = ""
        self._sample_start = 0
        self._sample_end = 0
        self._connection = connection
        self._project = project
        self._capture = capture
        self._segmenter = segmenter
        self._label = label
        self._label_value = label_value

    @property
    def uuid(self) -> str:
        """Auto generated unique identifier for the metadata object"""
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def sample_start(self) -> int:
        """The index of the first sample of the label"""
        return self._sample_start

    @sample_start.setter
    def sample_start(self, value: int):
        self._sample_start = value

    @property
    def sample_end(self) -> int:
        """The index of the last sample of the label"""
        return self._sample_end

    @sample_end.setter
    def sample_end(self, value: int):
        self._sample_end = value

    @property
    def segmenter(self) -> str:
        """The index of the last sample of the label"""
        if isinstance(self._segmenter, Segmenter):
            return self._segmenter.uuid

        return self._segmenter

    @segmenter.setter
    def segmenter(self, value: Union[Segmenter, str]):
        self._segmenter = value

    @property
    def label(self) -> str:
        if isinstance(self._label, Label):
            return self._label.uuid
        else:
            return self._label

    @label.setter
    def label(self, value: Union[Label, str]):
        self._label = value

    @property
    def label_value(self) -> str:
        if isinstance(self._label_value, LabelValue):
            return self._label_value.uuid
        else:
            return self._label_value

    @label_value.setter
    def label_value(self, value: Union[LabelValue, str]):
        self._label_value = value

    def insert(self) -> Response:
        """Calls the REST API and inserts a metadata object onto the server using the local object's properties."""
        url = f"project/{self._project.uuid}/capture/{self._capture.uuid}/label-relationship/"

        data = self._to_representation()

        response = self._connection.request("post", url, data)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.uuid = response_data[0]["uuid"]

        return response

    def update(self) -> Response:
        """Calls the REST API and updates the object on the server."""
        self._capture.await_ready()
        url = "project/{0}/capture/{1}/label-relationship/{2}/".format(
            self._project.uuid, self._capture.uuid, self.uuid
        )
        data = self._to_representation()

        response = self._connection.request("put", url, data)
        utility.check_server_response(response)

        return response

    def delete(self) -> Response:
        """Calls the REST API and deletes the object from the server."""
        url = "project/{0}/capture/{1}/label-relationship/{2}/".format(
            self._project.uuid, self._capture.uuid, self.uuid
        )
        response = self._connection.request("delete", url)
        utility.check_server_response(response)

        return response

    def refresh(self) -> Response:
        """Calls the REST API and populates the local object's properties from the server."""
        url = "project/{0}/capture/{1}/label-relationship/{2}/".format(
            self._project.uuid, self._capture.uuid, self.uuid
        )
        response = self._connection.request("get", url)
        response_data, err = utility.check_server_response(response)
        if err is False:
            self.initialize_from_dict(response_data)

        return response


class SegmentSet(BaseSet):
    """Base class for a collection of segments"""

    def __init__(
        self,
        connection: Connection,
        project: Project,
        capture: Capture,
        initialize_set: bool = True,
    ):
        self._connection = connection
        self._project = project
        self._capture = capture
        self._set = None
        self._objclass = Segment

        if initialize_set:
            self.refresh()

    @property
    def get_set_url(self):
        return f"project/{self._project.uuid}/capture/{self._capture.uuid}/label-relationship/"

    @property
    def segments(self):
        return self.objs

    def _new_obj_from_dict(self, data: dict) -> Segment:
        """Creates a new label from data in the dictionary.

        Args:
            dict (dict): contains label properties uuid, name, type, value, capture_sample_sequence_start, and
            capture_sample_sequence_end

        Returns:
            label object

        """
        segment = self._objclass(self._connection, self._project, self._capture)
        segment.initialize_from_dict(data)
        return segment
