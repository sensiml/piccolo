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
import json
from unittest.mock import Mock
from logger.log_handler import LogHandler


class TestLogHandler:
    def setup_class(self):
        pass

    def test_debug_logging_with_header(self):
        mock_logger = Mock()
        new_uuid = str(uuid.uuid4())
        header = {"UUID": new_uuid, "log_type": "PID"}
        message = {
            "name": "test 1",
            "value": 100,
            "text": "A Debug message with header",
            "log_type": "datamanager",
            "public": False,
        }
        lh = LogHandler(mock_logger, header)
        lh.debug(message)
        final_message = json.dumps({**header, **message})
        mock_logger.debug.assert_called_with(final_message)

    def test_info_logging_with_header(self):
        mock_logger = Mock()
        new_uuid = str(uuid.uuid4())
        header = {"pid": new_uuid}
        message = {
            "name": "test 2",
            "value": 200,
            "text": "An Info message with header",
            "log_type": "datamanager",
            "public": False,
        }
        lh = LogHandler(mock_logger, header)
        lh.info(message)
        final_message = json.dumps({**header, **message})
        mock_logger.info.assert_called_with(final_message)

    def test_warn_logging_with_header(self):
        mock_logger = Mock()
        new_uuid = str(uuid.uuid4())
        header = {"pid": new_uuid}
        message = {
            "name": "test 3",
            "value": 300,
            "text": "A Warning message with header",
            "log_type": "datamanager",
            "public": False,
        }
        lh = LogHandler(mock_logger, header)
        lh.warn(message)
        final_message = json.dumps({**header, **message})
        mock_logger.warn.assert_called_with(final_message)

    def test_error_logging_with_header(self):
        mock_logger = Mock()
        new_uuid = str(uuid.uuid4())
        header = {"pid": new_uuid}
        message = {
            "name": "test 4",
            "value": 400,
            "text": "An Error message with header",
            "log_type": "datamanager",
            "public": False,
        }
        lh = LogHandler(mock_logger, header)
        lh.error(message)
        final_message = json.dumps({**header, **message})
        mock_logger.error.assert_called_with(final_message)

    def test_debug_logging_with_out_header(self):
        mock_logger = Mock()
        str(uuid.uuid4())
        message = {
            "name": "test 1",
            "value": 100,
            "text": "A Debug message with out header",
            "log_type": "datamanager",
            "public": False,
        }

        lh = LogHandler(mock_logger)
        lh.debug(message)
        mock_logger.debug.assert_called_with(json.dumps(message))

    def test_info_logging_with_out_header(self):
        mock_logger = Mock()
        str(uuid.uuid4())
        message = {
            "name": "test 2",
            "value": 200,
            "text": "An Info message with out header",
            "log_type": "datamanager",
            "public": False,
        }
        lh = LogHandler(mock_logger)
        lh.info(message)
        mock_logger.info.assert_called_with(json.dumps(message))

    def test_warn_logging_with_out_header(self):
        mock_logger = Mock()
        str(uuid.uuid4())
        message = {
            "name": "test 3",
            "value": 300,
            "text": "A Warning message with out header",
            "public": False,
            "log_type": "datamanager",
        }
        lh = LogHandler(mock_logger)
        lh.warn(message)
        mock_logger.warn.assert_called_with(json.dumps(message))

    def test_error_logging_with_out_header(self):
        mock_logger = Mock()
        str(uuid.uuid4())
        message = {
            "name": "test 4",
            "value": 400,
            "text": "An Error message with out header",
            "public": False,
            "log_type": "datamanager",
        }
        lh = LogHandler(mock_logger)
        lh.error(message)
        mock_logger.error.assert_called_with(json.dumps(message))

    def test_exception_log(self):
        mock_logger = Mock()
        try:
            raise ValueError("Test1")
        except Exception as e:
            str(uuid.uuid4())
            message = {
                "name": "test 4",
                "value": 400,
                "data": e,
                "public": False,
                "log_type": "datamanager",
            }
            lh = LogHandler(mock_logger)
            x = lh._encode_exception(message)
            assert x["data"]["error_message"] == "Test1"
            assert x["data"]["traceback"].endswith(
                'line 154, in test_exception_log\n    raise ValueError("Test1")\n'
            )
