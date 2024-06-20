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
from logging import getLogger

import pytest

from datamanager.util_err_defs import (
    ContractDirection,
    ContractErrors,
    ErrorCategories,
    ErrorDefaults,
)
from datamanager.utils import UtilError, UtilErrorEncoder, UtilErrorList

logger = getLogger(__name__)


def _is_json(msg):
    try:
        """loads returns value error if this is not a JSON string"""
        json.loads(msg)
    except ValueError:
        return False
    return True


class TestUtilError:
    """Unit tests for UtilError and UtilErrorEncoder creation."""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.single_err = ""
        self.list_err = UtilErrorList()
        self.category_str1 = ErrorCategories.contract
        self.category_str2 = ErrorCategories.schema
        self.category_str3 = ErrorCategories.fileOps
        self.category_str4 = ""

        self.contract_direction1 = ContractDirection.dir_input
        self.contract_direction2 = ContractDirection.dir_output

        self.err_str1 = ""
        self.err_str2 = ""
        self.err_str3 = "Test Error Message"
        self.err_str4 = "Other Error Message"

        self.extra_str1 = ""
        self.extra_str2 = ""
        self.extra_str3 = ""
        self.extra_str4 = "Message_extra data"

        self.exception1 = TypeError
        self.exception2 = None
        self.exception3 = None
        self.exception4 = NameError

    def test_error(self):
        """Verify we build a proper error object, it gets JSON'd correctly"""
        self.single_err = UtilError(
            self.category_str1,
            self.err_str1,
            self.extra_str1,
            exception=self.exception1,
        )
        assert self.single_err.category == self.category_str1
        assert self.single_err.err == ErrorDefaults.err_default
        assert self.single_err.extra == ErrorDefaults.extra_default + str(
            self.exception1
        )

        json_msg = json.dumps(self.single_err, cls=UtilErrorEncoder)
        assert _is_json(json_msg)

    def test_contract_direction(self):
        """Verify we can set contract error messages"""
        self.single_err = UtilError(
            self.category_str1,
            self.err_str1,
            self.extra_str1,
            exception=self.exception1,
        )

        self.single_err.set_contract_mismatch(
            ContractDirection.dir_input, type(2), type(2.0)
        )

        assert self.single_err.category == self.category_str1
        assert (
            self.single_err.err
            == ContractDirection.dir_input
            + " "
            + ContractErrors.type_mismatch
            + "expected <class 'int'> received <class 'float'>"
        )

        assert self.single_err.extra == ErrorDefaults.extra_default + str(
            self.exception1
        )

        json_msg = json.dumps(self.single_err, cls=UtilErrorEncoder)
        assert _is_json(json_msg)

    def test_invalid_contract_dir(self):
        """Verify we can only set contract directions on contract errors"""
        self.single_err = UtilError(
            self.category_str2,
            self.err_str1,
            self.extra_str1,
            exception=self.exception1,
        )

        self.single_err.set_contract_mismatch("Input", type(2), type(2.0))

        assert self.single_err.category == self.category_str2
        assert self.single_err.err == ErrorDefaults.err_default

        assert self.single_err.extra == ErrorDefaults.extra_default + str(
            self.exception1
        )

        json_msg = json.dumps(self.single_err, cls=UtilErrorEncoder)
        assert _is_json(json_msg)

    def test_error_list(self):
        """Verify we build a proper error list, it gets JSON'd correctly.
        Tests potential for sending a list of errors at once.
        """
        self.list_err.err_list_add(
            self.category_str1, self.err_str1, self.extra_str1, self.exception1
        )
        self.list_err.err_list_add(
            self.category_str2, self.err_str2, self.extra_str2, self.exception2
        )
        self.list_err.err_list_add(
            self.category_str3, self.err_str3, self.extra_str3, self.exception3
        )
        self.list_err.err_list_add(
            self.category_str4, self.err_str4, self.extra_str4, self.exception4
        )

        # assert self.list_err.get_list()[0].category == self.category_str1

        assert self.list_err.get_list()[0].err == ErrorDefaults.err_default

        assert self.list_err.get_list()[0].extra == ErrorDefaults.extra_default + str(
            self.exception1
        )

        assert self.list_err.get_list()[1].category == self.category_str2

        assert self.list_err.get_list()[1].err == ErrorDefaults.err_default

        assert self.list_err.get_list()[1].extra == ErrorDefaults.extra_default

        assert self.list_err.get_list()[2].category == self.category_str3

        assert self.list_err.get_list()[2].err == self.err_str3

        assert self.list_err.get_list()[2].extra == ErrorDefaults.extra_default

        assert self.list_err.get_list()[3].category == ErrorCategories.general

        assert self.list_err.get_list()[3].err == self.err_str4

        assert self.list_err.get_list()[3].extra == self.extra_str4 + str(
            self.exception4
        )

        json_msg = self.list_err.get_list_response()
        assert _is_json(json_msg)
        logger.debug(json_msg)
