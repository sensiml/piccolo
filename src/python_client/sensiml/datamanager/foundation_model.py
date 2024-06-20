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
from sensiml.datamanager.base import Base, BaseSet
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from sensiml.connection import Connection


class FoundationModel(Base):
    """Base class for a transform object"""

    _uuid = ""
    _name = None

    _fields = [
        "uuid",
        "name",
        "features_count",
        "model_size",
        "created_at",
        "knowledgepack_description",
        "last_modified",
    ]

    _read_only_fields = [
        "uuid",
        "name",
        "features_count",
        "model_size",
        "created_at",
        "knowledgepack_description",
        "last_modified",
    ]

    _field_map = {"transform_type": "type"}

    def __init__(self, connection: Connection, uuid: Optional[str] = None):
        self._connection = connection
        if uuid:
            self.uuid = uuid
            self.refresh()

    @property
    def base_url(self) -> str:
        return "foundation-model/"

    @property
    def detail_url(self) -> str:
        return f"foundation-model/{self.uuid}/"

    @property
    def uuid(self) -> str:
        return self._uuid

    @uuid.setter
    def uuid(self, value: str):
        self._uuid = value

    @property
    def name(self: str):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def knowledgepack_description(self) -> dict:
        return self._knowledgepack_description

    @knowledgepack_description.setter
    def knowledgepack_description(self, value: dict):
        self._knowledgepack_description = value


class FoundationModelSet(BaseSet):
    def __init__(self, connection: Connection, initialize_set: bool = True):
        """Initialize a custom transform set object.

        Args:
            connection
        """
        self._connection = connection
        self._set = None
        self._objclass = FoundationModel
        self._attr_key = "uuid"

        if initialize_set:
            self.refresh()

    @property
    def foundation_models(self):
        return self.objs

    @property
    def get_set_url(self) -> str:
        return "foundation-model/"

    def _new_obj_from_dict(self, data: dict) -> FoundationModel:
        """Creates a new object from the response data from the server.

        Args:
            data (dict): contains properties of the object

        Returns:
            obj of type _objclass

        """
        obj = self._objclass(self._connection)
        obj.initialize_from_dict(data)
        return obj
