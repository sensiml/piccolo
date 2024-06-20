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

import uuid


def is_valid_uuid4(uuid_string):

    """
    Validate that a UUID string is in
    fact a valid uuid4.
    Happily, the uuid module does the actual
    checking for us.
    It is vital that the 'version' kwarg be passed
    to the UUID() call, otherwise any 32-character
    hex string is considered valid.
    """

    try:
        val = uuid.UUID(uuid_string, version=4)
    except ValueError:
        # If it's a value error, then the string
        # is not a valid hex code for a UUID.
        return False
    return True


def uppercase_dataframe(columns):
    """Makes a dataframe have uppercase column names"""
    column_upper = {}
    for column in columns:
        try:
            column_upper[column] = column.upper()
        except:
            pass  # isinstance(column, str) not working

    return column_upper


def c_line(indent, text):
    return "\t" * indent + text + "\n"


def c_line_nr(indent, text):
    """
    [SDL-1093]
    Same as c_line without a carriage return/newline at the end
    """
    return "\t" * indent + text


def uuid_str_to_c_array(uuid_str):
    """
    Geenrates a C array representing UUID.
    :param uuid_str: string or UUID to be converted to array
    :return: string representation of C array
    """

    # Don't fail if someone accidentally passes a UUID object.
    uuid_obj = uuid.UUID(str(uuid_str))

    out = ["{"]
    for byte in uuid_obj.bytes:
        out.append(hex(byte))
        out.append(",")
    # Replace last comma with a closing bracket
    out[-1] = "}"
    return "".join(out)


def c_model_name(model_name, add_index=True):
    cleaned_model_name = "".join(e if e.isalnum() else "_" for e in str(model_name))
    if add_index:
        return "KB_MODEL_{}_INDEX".format(cleaned_model_name)

    return cleaned_model_name
