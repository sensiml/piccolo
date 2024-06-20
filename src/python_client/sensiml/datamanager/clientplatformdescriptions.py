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
from pandas import DataFrame


from sensiml.datamanager.clientplatformdescription import ClientPlatformDescription
import sensiml.base.utility as utility
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sensiml.connection import Connection


class ClientPlatformDescriptions:
    """Base class for a collection of functions"""

    def __init__(self, connection: Connection):
        self._connection = connection
        self.build_platform_descriptions()

    def __getitem__(self, index: int) -> ClientPlatformDescription:
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()

        df = self()
        for p in self.platform_list:
            if index not in df.index:
                continue
            if df.loc[index].equals(p().loc[0]):
                return p
        return None

    def refresh(self):
        self.build_platform_descriptions()

    def build_platform_descriptions(self):
        """Populates the platform_list property from the server."""
        self.platform_list = []
        self.platform_dict = {}

        platforms = self.get_platforms()
        for platform in platforms:
            self.platform_dict[f"{platform.name}"] = platform
            self.platform_list.append(platform)

    def get_platform_by_name(self, name: str) -> ClientPlatformDescription:
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()
        return self.platform_dict.get(name, None)

    def get_platform_by_id(self, id: int) -> ClientPlatformDescription:
        if len(self.platform_list) == 0:
            self.build_platform_descriptions()

        return next((x for x in self.platform_list if x.uuid == id), None)

    def get_platform_by_uuid(self, uuid: str) -> ClientPlatformDescription:
        return self.get_platform_by_id(uuid)

    def _new_platform_description_from_dict(
        self, data: dict
    ) -> ClientPlatformDescription:
        """Creates and populates a platform from a set of properties.

        Args:
            data (dict): contains properties of a platform

        Returns:
            platform
        """
        platform = ClientPlatformDescription(self._connection)
        platform.initialize_from_dict(data)
        return platform

    def get_platforms(self, function_type="") -> list[ClientPlatformDescription]:
        """Gets all functions as function objects.

        Args:
            function_type (optional[str]): type of function to retrieve

        Returns:
            list of functions
        """
        url = "platforms/v2"
        response = self._connection.request("get", url)
        try:
            response_data, err = utility.check_server_response(response)
        except ValueError:
            print(response)

        platformDescriptions = list()
        for platformdesc in response_data:
            platformDescriptions.append(
                self._new_platform_description_from_dict(platformdesc)
            )

        return platformDescriptions

    def list_processors(self) -> DataFrame:
        all_platforms = self.get_platforms()
        procs = {"name": {}}
        for plat in all_platforms:
            for processor in plat.processors:
                if processor.display_name not in procs["name"].keys():
                    procs["name"][processor.display_name] = processor.uuid
        return DataFrame(procs)

    def __call__(self):
        return self.__str__()

    def __str__(self):
        all_platforms = self.get_platforms()
        if len(all_platforms) < 0:
            return DataFrame()
        ret = DataFrame(p.__dict__() for p in all_platforms)
        # for plat in all_platforms:
        #     ret = ret.append(plat(), ignore_index=True)
        return ret.sort_values(by="Id").set_index("Id", drop=True)
