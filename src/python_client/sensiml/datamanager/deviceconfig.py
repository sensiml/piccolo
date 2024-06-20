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

import warnings


class DeviceConfig(dict):
    """
    Defines dictionary class for device configuration to be sent from sensiml to the
    Server for KnowledgePack code/binary generation.
    """

    # List of fields and their defaults
    fields = {
        "target_platform": 0,
        "build_flags": "",
        "budget": {},
        "debug": False,
        "sram_size": None,
        "test_data": "",
        "application": "",
        "sample_rate": 100,
        "kb_description": None,
    }

    def __init__(self, iterable=None, strict=True, **kwargs):
        super(DeviceConfig, self).__init__()
        object.__setattr__(self, "_strict", strict)
        for k, v in self.fields.items():
            self[k] = v
        if iterable:
            for k, v in dict(iterable).items():
                setattr(self, k, v)
        if kwargs:
            for k, v in kwargs.items():
                setattr(self, k, v)

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if self._strict and name not in self.fields.keys():
            out_str = f"{name} not in device configuration."
            out_str += "\nYou may need to update the device configuration on KB Cloud."
            warnings.warn(out_str, DeprecationWarning)

            return
        if name == "budget":
            assert isinstance(value, dict), "Budget is not a dictionary."
        elif name == "debug":
            value = bool(value)

        self[name] = value

    def initialize_from_dict(self, init_dict):
        """DEPRECATED: Populates a single device config from a dictionary of properties.

        Args:
            (dict): contains target_platform, platform_version, build_flags, budget, debug and sram_size
        """
        warnings.warn(
            "initialize_from_dict() is deprecated. Please pass arguments to constructor",
            DeprecationWarning,
        )
        for k, v in init_dict.items():
            setattr(self, k, v)
