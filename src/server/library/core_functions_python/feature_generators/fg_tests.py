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

import time


def fg_sleep_time(input_data, columns, sleep_time=30, **kwargs):
    """
    Test Function that sleeps for a specified amount of time. Used
    For testing celery worker shutdown and unsubscribe.

    """

    time.sleep(sleep_time)

    return input_data


fg_sleep_time_contracts = {
    "input_contract": [
        {"name": "input_data", "type": "DataFrame"},
        {
            "name": "columns",
            "type": "list",
            "element_type": "str",
            "description": "Column on which to apply the feature generator",
        },
        {"name": "sleep_time", "type": "int", "default": 30},
        {"name": "group_columns", "type": "list"},
    ],
    "output_contract": [{"name": "output_data", "type": "DataFrame", "family": True}],
}
