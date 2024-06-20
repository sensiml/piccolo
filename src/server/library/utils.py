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
import logging
import re

logger = logging.getLogger(__name__)


def parse_docstring_contracts(function):
    """Read the function's docstring and interpret the I/O contracts."""
    # Replace multi-space entries with single space
    docstr = re.sub(r"\s+(?=\S)", " ", function.__doc__, flags=re.MULTILINE)
    docstr = json.loads(docstr)
    input_contract = json.dumps(docstr["pre"])  # Re-encode contracts as json
    output_contract = json.dumps(docstr["post"])
    description = ""
    if "description" in docstr:
        description = docstr["description"]

    return input_contract, output_contract, description
