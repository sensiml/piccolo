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

from django.utils.deprecation import MiddlewareMixin
from datamanager.exceptions import NoAccessException
from django.contrib.auth import (
    PermissionDenied,
    get_user_model,
)
from oauth2_provider.middleware import (
    OAuth2TokenMiddleware as BaseOAuth2TokenMiddleware,
)
from django.contrib.auth.backends import ModelBackend
from logger.log_handler import LogHandler


logger = LogHandler(logging.getLogger(__name__))


def check_active(user):
    if not user.is_active:
        raise PermissionDenied


class OAuth2TokenMiddleware(BaseOAuth2TokenMiddleware, MiddlewareMixin):
    """Override OAuth2 Middleware to not enforce CSRFTokens when authenticated."""

    def process_request(self, request):
        super(OAuth2TokenMiddleware, self).process_request(request)
        if request.user:
            setattr(request, "_dont_enforce_csrf_checks", True)

    def process_exception(self, request, exception):
        if isinstance(exception, NoAccessException):
            return HttpResponse(exception, status=status.HTTP_403_FORBIDDEN)


class EmailAuthBackend(ModelBackend):
    """Django Auth backend to log user in by email instead of username"""

    def authenticate(self, request, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        if email is None:
            email = kwargs.get(UserModel.USERNAME_FIELD)

        try:
            user = UserModel._default_manager.get(
                email=None if email is None else email.lower()
            )

            if user.check_password(password):
                check_active(user)

                return user

            else:
                raise PermissionDenied

        except UserModel.DoesNotExist:
            # Run the default hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)


class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        try:
            case_insensitive_username_field = "{}__iexact".format(
                UserModel.USERNAME_FIELD
            )
            user = UserModel._default_manager.get(
                **{case_insensitive_username_field: username}
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a non-existing user (#20760).
            UserModel().set_password(password)
        else:
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
            else:
                raise PermissionDenied
