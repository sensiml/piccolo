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

import base64
import json
import logging

from numpy import int32, int64
from pandas import DataFrame
from rest_framework import renderers
from rest_framework.renderers import JSONRenderer

logger = logging.getLogger(__name__)


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"
    charset = "utf-8"

    def render(self, data, media_type=None, renderer_context=None):
        return str(data).encode(self.charset)


class BinaryRenderer(renderers.BaseRenderer):
    media_type = "application/octet-stream"
    format = "bin"
    charset = None
    render_style = "binary"

    def render(self, data, media_type=None, renderer_context=None):
        return data


class Base64Renderer(renderers.BaseRenderer):
    media_type = "text/plain"
    format = "txt"
    charset = "utf-8"

    def render(self, data, media_type=None, renderer_context=None):
        return base64.b64encode(data).encode(self.charset)


class KnowledgeBuilderEncoder(json.JSONEncoder):
    # Pylint false positive.
    def default(self, obj):  # pylint: disable=E0202
        if isinstance(obj, DataFrame):
            # The old check here just assumed whatever obj was had
            # a to_json() method, which could cause a crash.
            return obj.to_dict(orient="records")
        elif type(obj) in [int32, int64]:
            return int(obj)
        return super(KnowledgeBuilderEncoder, self).default(obj)


class KnowledgeBuilderRenderer(JSONRenderer):
    encoder_class = KnowledgeBuilderEncoder
