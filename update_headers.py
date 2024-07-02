import os
import argparse

# Copyright notice header
notice = """Copyright 2017-2024 SensiML Corporation

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
License along with SensiML Piccolo AI. If not, see <https://www.gnu.org/licenses/>."""

copyright_header_python = f'''"""
{notice}
"""
'''

copyright_header_c = f"""/*
{notice}
*/
"""

copyright_header_js = f"""/*
{notice}
*/
"""

# TODO MAKEFILE


def prepend_header_to_file(file_path, header):
    with open(file_path, "r+") as file:
        content = file.read()
        file.seek(0, 0)
        file.write(header + "\n" + content)


def traverse_and_prepend_header(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".py"):
                prepend_header_to_file(file_path, copyright_header_python)
            elif file.endswith(".c") or file.endswith(".h"):
                prepend_header_to_file(file_path, copyright_header_c)
            elif file.endswith(".js") or file.endswith(".jsx"):
                prepend_header_to_file(file_path, copyright_header_js)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Prepend copyright notice header to Python and C source code files."
    )
    parser.add_argument(
        "directory_path", type=str, help="The path to the directory to traverse"
    )

    args = parser.parse_args()
    directory_path = args.directory_path
    traverse_and_prepend_header(directory_path)
