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

# Unstable workaround for multiprocessing
# This will almost certainly break something someday
# import django
# django.setup()
#
import logging
import traceback

from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def jsend_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if status.is_server_error(response.status_code):
            logger.exception(traceback.format_exc())
        else:
            # don't log client errors as exceptions
            logger.debug(traceback.format_exc())
        if isinstance(exc, ValidationError):
            response.data = {
                "status": response.status_code,
                "detail": "Request failed validation",
                "data": response.data,
            }
        else:
            response.data.update(
                {
                    "status": response.status_code,
                    "detail": response.data.get("detail", exc.__class__.__name__),
                }
            )
    else:
        logger.exception(traceback.format_exc())
        response = Response(
            data={
                "status": status.HTTP_500_INTERNAL_SERVER_ERROR,
                "detail": "{0}: {1}".format(exc.__class__.__name__, exc),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        if settings.DEBUG:
            response.data["trace"] = traceback.format_exc()
    return response


class BadRequest(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Bad request"


class NotImplemented(APIException):
    status_codoe = status.HTTP_501_NOT_IMPLEMENTED
    default_detail = "Not Implemented"


class NoAccessException(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Access Denied"


class KnowledgeBuilderException(APIException):
    default_detail = "Knowledge Builder Exception"
    default_context = ""

    def __init__(self, detail=None, context=None):
        super(KnowledgeBuilderException, self).__init__(detail=detail)
        self._context = context if context else self.default_context

    @property
    def context(self):
        return self._context

    def __str__(self):
        msg = super(KnowledgeBuilderException, self).__str__()
        if self._context:
            return "{0}\nContext: {1}".format(msg, self._context)
        else:
            return msg

    def __dict__(self):
        return {
            "summary": super(KnowledgeBuilderException, self).__str__(),
            "context": self._context,
        }


class PipelineParseError(KnowledgeBuilderException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Failed to parse pipeline step."


class PipelineExecuting(KnowledgeBuilderException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = (
        "A pipeline with the same name is currently running,"
        + "wait until it finishes before submitting."
    )


class PipelineExecutionWarning(KnowledgeBuilderException):
    status_code = status.HTTP_206_PARTIAL_CONTENT
    default_detail = "Failed during execution of pipeline step."


class QueryExecutionWarning(KnowledgeBuilderException):
    status_code = status.HTTP_206_PARTIAL_CONTENT
    default_detail = "Failed during query of data."


class QueryFormatError(KnowledgeBuilderException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Query is formed improperly."


class AsynchronousRetrievalWarning(KnowledgeBuilderException):
    status_code = status.HTTP_203_NON_AUTHORITATIVE_INFORMATION
    default_detail = "Cached result is out of date with the sandbox or query."


class NoCaptureSampleSchemaError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Project has no or invalid capture sample schema."


class KnowledgePackConfigError(KnowledgeBuilderException):
    status_code = status.HTTP_428_PRECONDITION_REQUIRED
    default_detail = "Device Configuration not included or could not be parsed"


class KnowledgePackCombinationException(KnowledgeBuilderException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = (
        "Failed to Generate Knowledgepack: kp_combo must be a list of kp uuids."
    )


class KnowledgePackInvalidDeviceError(KnowledgeBuilderException):
    status_code = status.HTTP_412_PRECONDITION_FAILED
    default_detail = "Unsupported device configuration"


class KnowledgePackTaskExecutingError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "KnowledgePack task currently running."


class KnowledgePackGenerationError(KnowledgeBuilderException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Failed to Generate KnowledgePack data."


class FileUploadError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred while processing the uploaded file."


class BadCaptureSchemaError(FileUploadError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Invalid capture schema"


class BadFileTypeError(FileUploadError):
    """Error for any problems with the uploaded file type"""


class BadFileExtensionError(BadFileTypeError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This file type is not allowed."


# Non-rest_framework errors


class BaseError(Exception):
    """Base error class for exceptions that may not be part of rest_framework"""

    default_detail = "An error occurred."
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, detail=None, *args, **kwargs):
        self.detail = detail if detail else self.default_detail
        super(BaseError, self).__init__(self.detail)


class InvalidTeamError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "This user belongs to a different team."


class TeamRegistrationError(BaseError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "An error occurred in registration."

    def __init__(self, detail=None):
        self.detail = detail if detail else self.default_detail
        super(BaseError, self).__init__(self.detail)
