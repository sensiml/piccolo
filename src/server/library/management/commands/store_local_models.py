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

import library.model_zoo.mfcc23x49_w480_d320_dscnn_v02 as mfcc23x49_w480_d320_dscnn_v02
import library.model_zoo.mfcc23x49_w480_d320_dscnn_v03 as mfcc23x49_w480_d320_dscnn_v03
import library.model_zoo.mfcc23x49_w480_d320_dscnn_v04 as mfcc23x49_w480_d320_dscnn_v04
import library.model_zoo.mfe23x24_w480_d320_dscnn_v01 as mfe23x24_w480_d320_dscnn_v01
import library.model_zoo.mfcc23x49_trimmed16x49_w480_d320_dscnn_filt16 as trimmed16x49_w480_d320_dscnn_filt16
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Loads models from the model zoo into the server as foundation models"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str)

    def handle(self, *args, **options):

        pass

        options.get("name")

        mfcc23x49_w480_d320_dscnn_v04.load()
        mfcc23x49_w480_d320_dscnn_v03.load()
        mfcc23x49_w480_d320_dscnn_v02.load()
        mfe23x24_w480_d320_dscnn_v01.load()
        trimmed16x49_w480_d320_dscnn_filt16.load()
