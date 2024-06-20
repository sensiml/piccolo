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

import logging

from logger.log_handler import LogHandler

from codegen.codegen_gcc_generic import GCCGenericCodeGenerator

logger = LogHandler(logging.getLogger(__name__))


class MINGW64GenericCodeGenerator(GCCGenericCodeGenerator):
    def __init__(
        self,
        knowledgepacks,
        uuid,
        task_id,
        device_conf,
        build_type,
        test_data=None,
        target_os=None,
    ):
        super(MINGW64GenericCodeGenerator, self).__init__(
            knowledgepacks, uuid, task_id, device_conf, build_type
        )
        self.kb_generated_files.append("Makefile")
        self.test_data = test_data
        self.target_os = target_os
        self.kb_generated_files.append("library_exports.def")
        self.kb_generated_files.append("sml_recognition_run.c")
        self.kb_generated_files.append("sml_recognition_run.h")

    def create_compile_flags(self):
        # TODO: These should be read as execution params for CFLAGS< LDFLAGS, etc instead of fill files,
        ret = {}
        ret[
            "readme_compile_string"
        ] = "`x86_64-w64-mingw320-gcc main.c -o sensiml.exe -L../libsensiml -lsensiml -lm -I../libsensiml`"

        return ret
