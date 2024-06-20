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

import errno
import sys
from distutils import dir_util

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "deploys the codegen support files for creating knowledgepacks"
    can_import_settings = True

    def handle(self, *args, **options):
        print("updating codegen support files ...\n")
        try:
            codegen_support_src = settings.CODEGEN_SUPPORT_SRC_DIR
            codegen_support_dst = settings.CODEGEN_SUPPORT_DIR
            dir_util.copy_tree(codegen_support_src, codegen_support_dst)

        except OSError as e:
            if e.errno == errno.EACCES:
                print(
                    e.strerror
                    + " Please check permission on following path: "
                    + settings.SERVER_DATA_ROOT
                )
                sys.exit(1)

            if e.errno == errno.ENOENT:
                print(
                    e.strerror
                    + " Please ensure that "
                    + codegen_support_src
                    + " and "
                    + codegen_support_dst
                    + " exist."
                )
                sys.exit(1)

        except:
            print("Unexpected error occurred during file creation")
            sys.exit(1)
