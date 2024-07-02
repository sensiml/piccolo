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


class LoginError(Exception):
    pass


class MethodDeprecatedError(LoginError):
    def __init__(self, message: str = "This method is no longer allowed.", *args):
        super(MethodDeprecatedError, self).__init__(message, *args)


class LoginAttemptsExceededError(LoginError):
    def __init__(
        self, message: str = "Maximum number of login attempts exceeded.", *args
    ):
        super(LoginAttemptsExceededError, self).__init__(message, *args)


class ConnectionAbortedError(LoginError):
    def __init__(self, message: str = "The connection was aborted by the user.", *args):
        super(ConnectionAbortedError, self).__init__(message, *args)
