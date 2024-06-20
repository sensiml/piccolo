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
from sensiml.datamanager.base import BaseSet
from sensiml.datamanager.labelvalue import LabelValue

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from sensiml.connection import Connection
    from sensiml.datamanager.project import Project
    from sensiml.datamanager.metadata import Metadata

logger = logging.getLogger(__name__)


class MetadataValue(LabelValue):
    """Base class for a label object."""

    def __init__(self, connection: Connection, project: Project, metadata: Metadata):
        """Initialize a metadata object.

        Args:
            connection
            project
            label
        """

        if not metadata._metadata:
            raise ValueError("Must be metadata not label")

        self._uuid = ""
        self._value = ""
        self._last_modified = ""
        self._created_at = ""
        self._connection = connection
        self._project = project
        self._label = metadata


class MetadataValueSet(BaseSet):
    def __init__(
        self,
        connection: Connection,
        project: Project,
        metadata: Metadata,
        initialize_set: bool = True,
    ):
        """Initialize a metadata object.

        Args:
            connection
            project
        """
        self._connection = connection
        self._project = project
        self._metadata = metadata
        self._set = None
        self._objclass = MetadataValue
        self._attr_key = "value"

        if initialize_set:
            self.refresh()

    @property
    def metadata_values(self):
        return self.objs

    @property
    def get_set_url(self) -> str:
        return f"project/{self._project.uuid}/{self._metadata._label_or_metadata}/{self._metadata.uuid}/labelvalue/"

    def _new_obj_from_dict(self, data: dict) -> MetadataValue:
        """Creates a new label from data in the dictionary.

        Args:
            data (dict): contains label_value properties value, uuid

        Returns:
            label object

        """

        obj = self._objclass(self._connection, self._project, self._metadata)
        obj.initialize_from_dict(data)
        return obj

    def __str__(self) -> str:
        s = ""
        if self._set:
            metadata = self._set[0]._label
            s = "METADATA\n"
            s += "\tname: " + str(metadata.name) + " uuid: " + str(metadata.uuid) + "\n"
            s += "METADATA VALUES\n"
            for mdv in self._set:
                s += "\tvalue: " + str(mdv.value) + " uuid:" + str(mdv.uuid) + "\n"

        return s
