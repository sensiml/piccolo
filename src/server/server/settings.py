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

from __future__ import absolute_import

import logging
import os
import random
import string
import sys
import uuid

import django
import environ
import iptools
from appdirs import AppDirs
from celery.schedules import crontab

logging.getLogger("child").propagate = False


def load_env(filename=".env", dir=os.path.dirname(__file__)):
    if os.path.isfile(os.path.join(dir, filename)):
        environ.Env.read_env(os.path.join(dir, filename))
    else:
        raise Exception("Unable to locate file" + os.path.join(dir, filename))


env = environ.Env(
    ENVIRONMENT=(str, ""),
    SECRET_KEY=(str, "asdf"),
    ALLOWED_HOSTS=(str, "localhost"),
    DEBUG=(bool, False),
    EMAIL_FROM_ADDRESS=(str, "info@sensiml.com"),
    HOSTNAME=(str, "localhost"),
    REDIS_ADDRESS=(str, "127.0.0.1"),
    BROKER_URL=(str, "redis://localhost:6379"),
    CELERY_RESULT_BACKEND=(str, "redis://localhost:6379"),
    DATABASE_URL=(str, "psql://piccoloadmin:piccoloadmin3@127.0.0.1/piccolodb"),
    TIME_ZONE=(str, "UTC"),
    LANGUAGE_CODE=(str, "en-us"),
    AWS_ACCESS_KEY=(str, ""),
    AWS_SECRET_KEY=(str, ""),
    OAUTH2_RATELIMIT=(str, "100/h"),
    AWS_S3_BUCKET=(str, ""),
    AWS_S3_ACCELERATE_ENDPOINT=(bool, False),
    AWS_REGION=(str, "us-west-2"),
    AWS_DOCKER_RUNNER_ACCESS_KEY=(str, ""),
    AWS_DOCKER_RUNNER_SECRET_KEY=(str, ""),
    AWS_DOCKER_RUNNER_REGION=(str, "us-west-2"),
    AWS_CODEGEN_BUCKET_NAME=(str, ""),
    AWS_BUCKET_INSTALLER_CONFIGS=(str, ""),
    AWS_DOCKER_RUNNER_CLUSTER_NAME=(str, ""),
    AWS_DOCKER_RUNNER_FARGATE_CLUSTER_NAME=(str, ""),
    AWS_FARGATE_CLUSTER_NAME=(str, ""),
    AWS_FARGATE_TASK_SCALE_IN_PROTECTION_TIME=(int, 60),
    MIN_AWS_FARGATE_WORKER=(int, 2),
    MAX_AWS_FARGATE_WORKER=(int, 40),
    AWS_FARGATE_WORKER_SERVICE_NAME=(str, ""),
    DEFAULT_SUBSCRIPTION_UUID=(str, "0f1d7143-0f62-4f2a-b1e9-de9f48acd89e"),
    DEVELOPER_SUBSCRIPTION_NAME=(str, "DEVELOPER"),
    PASSWORD_RESET_PROTOCOL=(str, "https"),
    MODEL_PROFILER=(str, "model_profiler.py"),
    DEBUG_FUNCTIONS=(bool, False),  # raises exceptions when transforms fail
    AWS_DOCKER_CONTAINER_CPU=(int, 2048),
    AWS_DOCKER_CONTAINER_RAM=(int, 4096),
    AWS_DOCKER_CONTAINER_CPU_TENSORFLOW=(int, 2048),
    AWS_DOCKER_CONTAINER_RAM_TENSORFLOW=(int, 4096),
    AWS_DOCKER_CONTAINER_CPU_LIMIT=(int, int(6e7)),
    # Fargate Settings Settings
    AWS_DOCKER_TASK_USE_FARGATE=(bool, False),
    AWS_DOCKER_TASK_EXECUTION_ROLE_ARN=(str, ""),
    AWS_DOCKER_TASK_ROLE_ARN=(str, ""),
    AWS_DOCKER_RUNNER_TASK_SUBNETS=(str, ""),
    AWS_DOCKER_RUNNER_TASK_SECURITY_GROUP=(str, ""),
    SENSIML_SUPPORT=(str, "https://sensiml.com/support/"),
    # End Fargate Settings Settings
    AWS_DOCKER_LOGS=(str, "sml_docker_logs"),
    DOCKER_REGISTRY=(str, ""),
    SESSION_COOKIE_SECURE=(bool, True),
    CSRF_COOKIE_SECURE=(bool, True),
    ENABLE_API_KEY_AUTHENTICATION=(bool, True),
    OAUTH_APP_NAME=(str, "WebUI"),
    OAUTH_MINIMUM_OAUTH2_TOKEN_EXPIRES_SEC=(int, 36000),
    OAUTH_DEFAULT_OAUTH2_TOKEN_EXPIRES_SEC=(int, 36000),
    OAUTH_CLIENT_ID=str,
    OAUTH_CLIENT_SECRET=str,
    OAUTH_TOKEN_KEY_URL=str,
    OAUTH2_AUTHORIZATION_URL=(str, r"^oauth/"),
    OAUTH_TOKEN_URL=(str, r"^oauth/token/$"),
    GOOGLE_OAUTH_CLIENT_ID=(str, ""),
    GOOGLE_OAUTH_CLIENT_SECRET=(str, ""),
    GOOGLE_ACCESS_TOKEN_OBTAIN_URL=(str, ""),
    GOOGLE_USER_INFO_URL=(str, ""),
    OAUTH_CALLBACK_WEBUI_URL=(str, "/auth/oauth-callback/"),
    OAUTH_CALLBACK_MPLADV_URL=(str, "http://localhost:3000/"),
    CAPTURE_VIDEO_MAX_MB=(int, 5000),
    LOG_LEVEL=(str, "DEBUG"),
    CONSOLE_LOG_LEVEL=(str, "DEBUG"),
    SITE_URL=(str, "http://localhost:8000"),
    INTERNAL_IPS=list,
    EMAIL_HOST_PASSWORD=(str, ""),
    AWS_SES_ACCESS_KEY_ID=(str, ""),
    AWS_SES_SECRET_ACCESS_KEY=(str, ""),
    EMAIL_BACKEND=(str, "django.core.mail.backends.console.EmailBackend"),
    RECAPTCHA_PUBLIC_KEY=(str, ""),
    RECAPTCHA_PRIVATE_KEY=(str, ""),
    CODEGEN_USE_ECS_FOR_DOCKER=(bool, False),
    CAPTCHA_BYPASS_FOR_LOCAL_ENABLE=(bool, True),
    BONSAI=(str, "/home/sml-app/EdgeML/"),
    CLASSIFIER_LIBS=(str, "/home/sml-app/install/lib/"),
    MAX_BATCH_SIZE=(int, 2),
    USE_S3_BUCKET=(bool, False),
    SLACK_WEBHOOK_API_URL=(str, ""),
    ACTIVATION_CODE_AUTH=(str, "11111"),
    LIFECYCLE_QUEUE_PIPELINE_STEPS=(str, ""),
    AUTOSCALING_GROUP_PIPELINE_STEPS=(str, ""),
    AUTOSCALING_MIN_DESIRED_CAPACITY=(int, 1),
    STARTER_CLASSIFICATION_LIMIT=(int, 100000),
    BASIC_EDITION_SAMPLE_RATE_LIMIT=(int, 10000),
    TRAINING_PROGRESS_LOGS=(bool, False),
    FREE_TEAM_PK=(int, 5),
    CORS_WEBUI_SERVER_WHITELIST=(str, ""),
    HUBSPOT_API_KEY=(str, ""),
    CORS_SENSIML_COM_WHITELIST=(str, ""),
    SENSIML_REGISTRATION_SUCCESS=(str, "/accounts/register/complete"),
    SENSIML_SERVER_URL=(str, "https://sensiml.com/"),
    SUBSCRIPTION_PLAN_URL=(str, "https://sensiml.com/plans/"),
    PYTHON_CLIENT_NAME=(str, "SensiML"),
    FILE_DIR=(str, ""),
    AUTOSCALING_FACTOR=(int, 4),  # number of tasks in queue per worker
    AUTOSCALLING_COOLDOWN=(int, 4),  # number of attempts to before termination
    AUTOSCALLING_SCALE_IN_MAX=(int, 1),
    AUTOSCALLING_WORKER_BUFFER=(int, 2),
    IS_CREATE_SUBSCRIBTION_SERVICE_ACCOUNTS=(bool, True),
    CHARGEBEE_SITE=(str, ""),
    CHARGEBEE_PUBLISHERKEY=(str, ""),
    CHARGEBEE_WEBHOOK_API_KEY=(str, ""),
    RANDOM_TEST_DATABASE=(bool, True),
    LOCAL_INSTALLERS_JSON=(str, ""),
    CUSTOM_TRANSFORM_CPU_TIME=(int, 5),
    CELERY_RDB_PORT=(int, 6899),
    DOCKER_HOST_SML_DATA_DIR=(str, ""),
    INSIDE_LOCAL_DOCKER=(bool, True),
    LOCAL_DOCKER_SERVER_DATA_VOLUMNE_NAME=(str, "sensiml_server_data"),
    FOUNDATION_MODEL_STORE_DOMAIN=(str, "sensiml"),
    FOUNDATION_MODEL_STORE_PROJECT=(str, "sensiml"),
    ADMIN_SITE_HEADER=(str, "SensiML Account Management"),
    ADMIN_SITE_TITLE=(str, "SensiML"),
    AWS_ACCOUNT_ID=(str, ""),
    KNOWLEDGEPACK_LIBRARY_NAME=(str, "libsensiml"),
    KNOWLEDGEPACK_DIRECTORY_NAME=(str, "sensiml"),
    NEW_ACCOUNT_URL=(str, "documentation/"),
    CODEGEN_TENSORFLOW_PLATFORM_VERSION=(str, "0a4bec2a"),
    AWS_CUSTOMER_REPORT_LOG_BUCKET=(str, "sml.customer.reports"),
    ALLOW_UPDATE_PROJECT_SCHEMA=(bool, False),
    EMBEDDED_SDK_LICENSE=(
        str,
        """/* ----------------------------------------------------------------------
* Copyright (c) 2022 SensiML Corporation
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
* 1. Redistributions of source code must retain the above copyright notice,
*    this list of conditions and the following disclaimer.
*
* 2. Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
* 3. Neither the name of the copyright holder nor the names of its contributors
*    may be used to endorse or promote products derived from this software
*    without specific prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
* ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
* LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
* ---------------------------------------------------------------------- */
""",
    ),
)


print(f'ECS AGENT URI SETTING {os.environ.get("ECS_AGENT_URI")}')

if os.environ.get("DJANGO_ENV"):
    if os.environ.get("DJANGO_ENV_PATH"):
        load_env(
            ".env.{}".format(os.environ["DJANGO_ENV"].strip().lower()),
            dir=os.environ.get("DJANGO_ENV_PATH"),
        )
        print(
            "Loading ENV from",
            os.path.join(
                os.environ.get("DJANGO_ENV_PATH"),
                ".env.{}".format(os.environ["DJANGO_ENV"].strip().lower()),
            ),
        )
    else:
        load_env(
            ".env.{}".format(os.environ["DJANGO_ENV"].strip().lower()),
            dir=os.path.expanduser("~"),
        )
        print(
            "Loading ENV from",
            os.path.join(
                os.path.expanduser("~"),
                ".env.{}".format(os.environ["DJANGO_ENV"].strip().lower()),
            ),
        )
else:
    print("No environment {} found".format(os.environ.get("DJANGO_ENV")))


LOCAL_DOCKER_SERVER_DATA_VOLUMNE_NAME = env("LOCAL_DOCKER_SERVER_DATA_VOLUMNE_NAME")
ENVIRONMENT = env("ENVIRONMENT")
FREE_TEAM_PK = env("FREE_TEAM_PK")
SENSIML_LIBRARY_PACK = None
DOCKER_HOST_SML_DATA_DIR = env("DOCKER_HOST_SML_DATA_DIR")
print("DOCKER HOST SML DATAT DIR", DOCKER_HOST_SML_DATA_DIR)
INSIDE_LOCAL_DOCKER = env("INSIDE_LOCAL_DOCKER")


# Private Label Settings
KNOWLEDGEPACK_LIBRARY_NAME = env("KNOWLEDGEPACK_LIBRARY_NAME")
KNOWLEDGEPACK_DIRECTORY_NAME = env("KNOWLEDGEPACK_DIRECTORY_NAME")
EMBEDDED_SDK_LICENSE = env("EMBEDDED_SDK_LICENSE")
SUBSCRIPTION_PLAN_URL = env("SUBSCRIPTION_PLAN_URL")
ADMIN_SITE_HEADER = env("ADMIN_SITE_HEADER")
ADMIN_SITE_TITLE = env("ADMIN_SITE_TITLE")

# number of segments a community edition user can add to their project
STARTER_LABEL_LIMIT = 2500

logger = logging.getLogger("server")
appdirs = AppDirs("server", appauthor="SensiML")

CUSTOM_TRANSFORM_PATH_VARIABLES = ":/home/sml-app/emsdk/upstream/bin:/home/sml-app/emsdk/upstream/emscripten:/home/sml-app/wabt/build/"
CUSTOM_TRANSFORM_CPU_TIME = env("CUSTOM_TRANSFORM_CPU_TIME")
MODEL_PROFILER = env("MODEL_PROFILER")

# registration success url for sensiml.com
SENSIML_REGISTRATION_SUCCESS = env("SENSIML_REGISTRATION_SUCCESS")
SENSIML_SERVER_URL = env("SENSIML_SERVER_URL")
NEW_ACCOUNT_URL = env("NEW_ACCOUNT_URL")

FOUNDATION_MODEL_STORE_PROJECT = env("FOUNDATION_MODEL_STORE_PROJECT")
FOUNDATION_MODEL_STORE_DOMAIN = env("FOUNDATION_MODEL_STORE_DOMAIN")

# SECURITY WARNING: keep the secret key used in production secret!
USE_S3_BUCKET = env("USE_S3_BUCKET")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env("DEBUG")
DEBUG_FUNCTIONS = env("DEBUG_FUNCTIONS")
ALLOWED_HOSTS = env("ALLOWED_HOSTS").split(",")
print(ALLOWED_HOSTS)


SENSIML_SUPPORT = env("SENSIML_SUPPORT")
SITE_ID = 1

HOSTNAME = env("HOSTNAME")
EMAIL_FROM_ADDRESS = env("EMAIL_FROM_ADDRESS")
HOST_UUID = str(uuid.uuid5(uuid.NAMESPACE_DNS, HOSTNAME))

REDIS_ADDRESS = env("REDIS_ADDRESS")
BROKER_URL = env("BROKER_URL")

CELERY_RDB_PORT = env("CELERY_RDB_PORT")
CELERY_SEND_TASK_ERROR_EMAILS = True

PYTHON_CLIENT_NAME = env("PYTHON_CLIENT_NAME")


# Celery Settings
CELERY_REDIS_ADDRESS = env("REDIS_ADDRESS")
CELERY_BROKER_URL = env("BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_ACCEPT_CONTENT = [
    "application/json",
    "application/x-python-serialize",
    "pickle",
    "json",
]
CELERY_TASK_SERIALIZER = "pickle"
CELERY_RESULT_SERIALIZER = "pickle"
CELERY_TIMEZONE = env("TIME_ZONE")
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_PREFETCH_MULTIPLIER = 1
CELERY_TASK_REJECT_ON_WORKER_LOST = True
CELERY_TASK_ACKS_LATE = True
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_ROUTES = {
    "datamanager.tasks.pipeline_async": {"queue": "pipelines"},
    "datamanager.tasks.gridsearch_async": {"queue": "pipelines"},
    "datamanager.tasks.auto_async": {"queue": "pipelines"},
    "datamanager.tasks.autosegment_async": {"queue": "pipelines"},
    "datamanager.tasks.recognize_signal_async": {"queue": "pipelines"},
    "datamanager.tasks.generate_knowledgepack_v2": {"queue": "knowledgepack"},
    "datamanager.tasks.process_custom_transform": {"queue": "pipelines"},
    "datamanager.tasks.querydata_async": {"queue": "pipelines"},
    "datamanager.tasks.delete_project_task": {"queue": "pipelines"},
    "logger.tasks.log_reports": {"queue": "management"},
    "server.tasks.cpu_resource_allocation": {"queue": "management"},
    "server.autoscaling.scale_in_ecs": {"queue": "management"},
    "engine.tasks.execute_function": {"queue": "pipeline_steps"},
    "engine.tasks.execute_function_return_success": {"queue": "pipeline_steps"},
    "engine.tasks.sleep_time": {"queue": "pipeline_steps"},
}


TZINFO = "UTC"

CELERY_BEAT_SCHEDULE = {
    "log_reports": {
        "task": "logger.tasks.log_reports",
        "schedule": crontab(minute=0, hour=0),  # every day at midnight
    },
    "subscription_refill": {
        "task": "server.tasks.cpu_resource_allocation",
        "schedule": crontab(minute=0, hour=0),  # every day at midnight
    },
}

# The number of extra workers to reserve beyond the predicted amount
AUTOSCALLING_WORKER_BUFFER = env("AUTOSCALLING_WORKER_BUFFER")
# Queues to check for autoscaling
# ['pipelines','pipeline_steps','knowledgepack','file_upload','file_upload_large','celery']
AUTOSCALING_CHECK_QUEUES = ["pipeline_steps"]
AUTOSCALING_FACTOR = env("AUTOSCALING_FACTOR")  # number of tasks in queue per worker
AUTOSCALLING_COOLDOWN = env("AUTOSCALLING_COOLDOWN")
AUTOSCALLING_COOLDOWN_KEY = "autoscaling_counter"
# These should be eventually specified in the .env file as they are per environment
AUTOSCALING_GROUP_PIPELINE_STEPS = env("AUTOSCALING_GROUP_PIPELINE_STEPS")
AUTOSCALLING_SCALE_IN_MAX = env("AUTOSCALLING_SCALE_IN_MAX")
# These should be eventually specified in the .env file
LIFECYCLE_QUEUE_PIPELINE_STEPS = env("LIFECYCLE_QUEUE_PIPELINE_STEPS")
AUTOSCALING_MIN_DESIRED_CAPACITY = env("AUTOSCALING_MIN_DESIRED_CAPACITY")

DEFAULT_SUBSCRIPTION_UUID = env("DEFAULT_SUBSCRIPTION_UUID")
DEVELOPER_SUBSCRIPTION_NAME = env("DEVELOPER_SUBSCRIPTION_NAME")


if AUTOSCALING_GROUP_PIPELINE_STEPS:
    CELERY_BEAT_SCHEDULE["scale_in_ecs"] = {
        "task": "server.autoscaling.scale_in_ecs",
        "schedule": crontab(),
    }

# Application definition
INSTALLED_APPS = (
    "django.contrib.sites",
    "registration",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "oauth2_provider",
    "django.contrib.sessions",
    "captcha",
    "rest_framework",
    "rest_framework_docs",
    "rest_framework_api_key",
    "corsheaders",
    "datamanager",
    "logger",
    "library",
    "engine",
    "server",
    "widget_tweaks",
    "drf_spectacular",
)

##
DJANGO_ROOT = os.path.dirname(os.path.realpath(django.__file__))
SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
FILE_DIR = env("FILE_DIR")
if not FILE_DIR:
    FILE_DIR = BASE_DIR

MIDDLEWARE = (
    "django.middleware.common.CommonMiddleware",
    "server.middleware.XForwardedForMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "datamanager.authenticate.OAuth2TokenMiddleware",
    # "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "crum.CurrentRequestUserMiddleware",
    "server.middleware.NoCacheMiddleware",
    # must be at end, see https://github.com/omarish/django-cprofile-middleware
    "django_cprofile_middleware.middleware.ProfilerMiddleware",
)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
            ]
        },
    }
]


SERIALIZATION_MODULES = {"yml": "django.core.serializers.pyyaml"}

TRAINING_PROGRESS_LOGS = env("TRAINING_PROGRESS_LOGS")

SLACK_WEBHOOK_API_URL = env("SLACK_WEBHOOK_API_URL")
LOG_LEVEL = env("LOG_LEVEL")
CONSOLE_LOG_LEVEL = env("CONSOLE_LOG_LEVEL")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            "datefmt": "%d/%b/%Y %H:%M:%S",
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "file": {
            "level": getattr(logging, LOG_LEVEL, None),
            "class": "logging.FileHandler",
            "filename": "server.log",
            "formatter": "verbose",
        },
        "console": {
            "level": getattr(logging, CONSOLE_LOG_LEVEL, None),
            "class": "logging.StreamHandler",
            "stream": sys.stderr,
            "formatter": "verbose",
        },
        "user_logs": {
            "level": getattr(logging, LOG_LEVEL, None),
            "class": "logging.FileHandler",
            "filename": "client_logs.log",
            "formatter": "verbose",
        },
        "usage_logger": {
            "level": getattr(logging, LOG_LEVEL, None),
            "class": "logging.FileHandler",
            "filename": "usage_logs.log",
            "formatter": "verbose",
        },
        "null": {"level": "DEBUG", "class": "django.utils.log.logging.NullHandler"},
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        "django.db.backends": {
            "handlers": ["console"],
            "propagate": False,
            "level": "ERROR",
        },
        "datamanager": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "codegen": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "library": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "engine": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "server": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "oauth": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "logger.data_logger": {"handlers": ["usage_logger"], "level": "INFO"},
        "logger.serializers": {"handlers": ["user_logs"], "level": "INFO"},
    },
}

ROOT_URLCONF = "server.urls"
WSGI_APPLICATION = "server.wsgi.application"


if env("RANDOM_TEST_DATABASE"):
    letters = string.ascii_letters
    test_database = "test_piccolodb_" + "".join(
        random.choice(letters) for i in range(10)
    )
else:
    test_database = "test_piccolodb"

default_db = env.db()
default_db["TEST"] = {"NAME": test_database}

DATABASES = {"default": default_db}  # Parses DATABASE_URL

NEW_PROJECT_DESCRIPTION = """"""
CORS_ORIGIN_ALLOW_ALL = False
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_REGEX_WHITELIST = (
    "^http://localhost",
    "null",
    "file://",
    env("CORS_WEBUI_SERVER_WHITELIST"),
    env("CORS_SENSIML_COM_WHITELIST"),
)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Be sure to set these to true in production
SESSION_COOKIE_SECURE = env("SESSION_COOKIE_SECURE")
SESSION_COOKIE_AGE = 86400
CSRF_COOKIE_SECURE = env("CSRF_COOKIE_SECURE")
LANGUAGE_CODE = env("LANGUAGE_CODE")

TIME_ZONE = env("TIME_ZONE")
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/admin"

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_PATH = "/"
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 8},
    },
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Rest Framework settings
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions, or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework.renderers.AdminRenderer",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    # 'PAGE_SIZE': 1000, # Clients and tests must be updated to read 'results' for data
    "EXCEPTION_HANDLER": "datamanager.exceptions.jsend_exception_handler",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


SPECTACULAR_SETTINGS = {
    "TITLE": "Cloud API",
    "DESCRIPTION": "REST APIs for machine learning automation and data management",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/project",
    "OAUTH2_FLOWS": [],
    "OAUTH2_AUTHORIZATION_URL": env("OAUTH2_AUTHORIZATION_URL"),
    "OAUTH2_TOKEN_URL": env("OAUTH_TOKEN_URL"),
}

OAUTH2_PROVIDER = {
    "OAUTH2_BACKEND_CLASS": "oauth2_provider.oauth2_backends.OAuthLibCore",
}

STRICT_JSON = False
OAUTH2_RATELIMIT = env("OAUTH2_RATELIMIT")  # Max number of requests per username
OAUTH_TOKEN_URL = env("OAUTH_TOKEN_URL")
OAUTH2_AUTHORIZATION_URL = env("OAUTH2_AUTHORIZATION_URL")

# Registration settings
AWS_SES_REGION_NAME = "us-west-2"
AWS_SES_REGION_ENDPOINT = "email.us-west-2.amazonaws.com"

EMAIL_BACKEND = env("EMAIL_BACKEND")
AWS_SES_ACCESS_KEY_ID = env("AWS_SES_ACCESS_KEY_ID")
AWS_SES_SECRET_ACCESS_KEY = env("AWS_SES_SECRET_ACCESS_KEY")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_HOST_USER = env("EMAIL_FROM_ADDRESS")
EMAIL_PORT = 465
EMAIL_TIMEOUT = 30
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = env("EMAIL_FROM_ADDRESS")
ACCOUNT_ACTIVATION_DAYS = 7  # One-week activation window
SEND_ACTIVATION_EMAIL = True
REGISTRATION_OPEN = True
REGISTRATION_AUTO_LOGIN = False  # Automatically log the user in
REGISTRATION_MINIMUM_PASS_LENGTH = 8
# Registration Captcha settings
RECAPTCHA_PUBLIC_KEY = env("RECAPTCHA_PUBLIC_KEY")
RECAPTCHA_PRIVATE_KEY = env("RECAPTCHA_PRIVATE_KEY")
NOCAPTCHA = True
CAPTCHA_BYPASS_FOR_LOCAL_ENABLE = env("CAPTCHA_BYPASS_FOR_LOCAL_ENABLE")
LOCAL_INSTALLERS_JSON = env("LOCAL_INSTALLERS_JSON")
PASSWORD_RESET_PROTOCOL = env("PASSWORD_RESET_PROTOCOL")
ADMINS = (("Webmaster", "webmaster@sensiml.com"),)
REGISTRATION_ADMINS = (("Info", "info@sensiml.com"),)
SITE_URL = env("SITE_URL")


AUTHENTICATION_BACKENDS = (
    "oauth2_provider.backends.OAuth2Backend",
    "datamanager.authenticate.EmailAuthBackend",
    "datamanager.authenticate.CaseInsensitiveModelBackend",
)


# Analytic Engine App location settings
SERVER_PROJECT_IMAGE_ROOT = os.path.join(FILE_DIR, "static", "projectimages")
SERVER_BASE_DIRECTORY = os.path.join(FILE_DIR, "datamanager")
SERVER_CAPTURE_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "capture")
SERVER_CAPTURE_VIDEO_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "capture-video")
SERVER_CUSTOM_TRANSFORM_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "custom_transforms")
SERVER_DATA_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "datafile")
SERVER_MODEL_STORE_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "model_store")
SERVER_CACHE_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "pipelinecache")
SERVER_QUERY_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "querydata")
SERVER_FEATURE_FILE_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "featurefile")
SERVER_CODEGEN_ROOT = os.path.join(SERVER_BASE_DIRECTORY, "codegen")

# Analytic Engine app performance settings

MAX_BATCH_SIZE = env("MAX_BATCH_SIZE")

# Maximum shard (DataFrame) size in MB
MAX_SHARD_MEMORY_SIZE = 400
SHARD_MEMORY_SPLIT_SIZE = 10
# Number of segments to allow per query split
MAX_SHARD_SEGMENT_SIZE = 500  # sql limit, can increase but need to change query format
SHARD_SEGMENT_SPLIT_SIZE = 400
# THESE MUST ALSO BE CHANGED IN fg_algorithms.c
MAX_SEGMENT_LENGTH = 32768
MAX_COLS = 3
MAX_FFT_SIZE = 512
MAX_FEATUREFILE_RETURN_SIZE = 300
DATA_UPLOAD_MAX_MEMORY_SIZE = 262144000
MAX_PIPELINE_FEATURES = 250
MAX_RECOGNITION_SAMPLES = 16000 * 100 * 60  # 16khz * 100 minutes * 60 seconds

KBUSER_DEFAULT_GROUPS = ("ProjectAdmin", "DataUpload", "ExperimentDeveloper")
CODEGEN_USE_ECS_FOR_DOCKER = env("CODEGEN_USE_ECS_FOR_DOCKER")

# Hubspot Integration
IS_CREATE_SUBSCRIBTION_SERVICE_ACCOUNTS = env("IS_CREATE_SUBSCRIBTION_SERVICE_ACCOUNTS")
HUBSPOT_API_KEY = env("HUBSPOT_API_KEY")
CHARGEBEE_SITE = env("CHARGEBEE_SITE")
CHARGEBEE_PUBLISHERKEY = env("CHARGEBEE_PUBLISHERKEY")
CHARGEBEE_WEBHOOK_API_KEY = env("CHARGEBEE_WEBHOOK_API_KEY")


# S3 Access Key settings
AWS_ACCESS_KEY = env("AWS_ACCESS_KEY") if env("AWS_ACCESS_KEY") else None
AWS_SECRET_KEY = env("AWS_SECRET_KEY") if env("AWS_SECRET_KEY") else None
AWS_REGION = env("AWS_REGION") if env("AWS_REGION") else None

AWS_DOCKER_RUNNER_ACCESS_KEY = (
    env("AWS_DOCKER_RUNNER_ACCESS_KEY") if env("AWS_DOCKER_RUNNER_ACCESS_KEY") else None
)
AWS_DOCKER_RUNNER_SECRET_KEY = (
    env("AWS_DOCKER_RUNNER_SECRET_KEY") if env("AWS_DOCKER_RUNNER_SECRET_KEY") else None
)
AWS_DOCKER_RUNNER_REGION = (
    env("AWS_DOCKER_RUNNER_REGION") if env("AWS_DOCKER_RUNNER_REGION") else None
)

AWS_FARGATE_CLUSTER_NAME = env("AWS_FARGATE_CLUSTER_NAME")
AWS_FARGATE_TASK_SCALE_IN_PROTECTION_TIME = env(
    "AWS_FARGATE_TASK_SCALE_IN_PROTECTION_TIME"
)
AWS_FARGATE_WORKER_SERVICE_NAME = env("AWS_FARGATE_WORKER_SERVICE_NAME")

OAUTH_APP_NAME = env("OAUTH_APP_NAME")
OAUTH_MINIMUM_OAUTH2_TOKEN_EXPIRES_SEC = env("OAUTH_MINIMUM_OAUTH2_TOKEN_EXPIRES_SEC")
OAUTH_DEFAULT_OAUTH2_TOKEN_EXPIRES_SEC = env("OAUTH_DEFAULT_OAUTH2_TOKEN_EXPIRES_SEC")

GOOGLE_OAUTH_CLIENT_ID = env("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = env("GOOGLE_OAUTH_CLIENT_SECRET")
GOOGLE_ACCESS_TOKEN_OBTAIN_URL = env("GOOGLE_ACCESS_TOKEN_OBTAIN_URL")
GOOGLE_USER_INFO_URL = env("GOOGLE_USER_INFO_URL")


OAUTH_CALLBACK_WEBUI_URL = env("OAUTH_CALLBACK_WEBUI_URL")
OAUTH_CALLBACK_MPLADV_URL = env("OAUTH_CALLBACK_MPLADV_URL")

CAPTURE_VIDEOS_EXT_LIST = [".mp4", ".webm"]
CAPTURE_VIDEO_MAX_MB = env("CAPTURE_VIDEO_MAX_MB")
CAPTURE_VIDEO_S3_ROOT = "capture-video"

# SensiML Analytic Engine S3 settings
AWS_S3_BUCKET = env("AWS_S3_BUCKET")
AWS_S3_ACCELERATE_ENDPOINT = env("AWS_S3_ACCELERATE_ENDPOINT")
AWS_CUSTOMER_REPORT_LOG_BUCKET = env("AWS_CUSTOMER_REPORT_LOG_BUCKET")
DOCKER_REGISTRY = env("DOCKER_REGISTRY")
AWS_ACCOUNT_ID = env("AWS_ACCOUNT_ID")
AWS_CODEGEN_BUCKET_NAME = env("AWS_CODEGEN_BUCKET_NAME")
AWS_BUCKET_INSTALLER_CONFIGS = env("AWS_BUCKET_INSTALLER_CONFIGS")
AWS_DOCKER_RUNNER_CLUSTER_NAME = env("AWS_DOCKER_RUNNER_CLUSTER_NAME")
AWS_DOCKER_RUNNER_FARGATE_CLUSTER_NAME = env("AWS_DOCKER_RUNNER_FARGATE_CLUSTER_NAME")
AWS_DOCKER_CONTAINER_CPU = env("AWS_DOCKER_CONTAINER_CPU")
AWS_DOCKER_CONTAINER_CPU_LIMIT = env("AWS_DOCKER_CONTAINER_CPU_LIMIT")
AWS_DOCKER_CONTAINER_RAM = env("AWS_DOCKER_CONTAINER_RAM")
AWS_DOCKER_CONTAINER_CPU_TENSORFLOW = env("AWS_DOCKER_CONTAINER_CPU_TENSORFLOW")
AWS_DOCKER_CONTAINER_RAM_TENSORFLOW = env("AWS_DOCKER_CONTAINER_RAM_TENSORFLOW")
AWS_DOCKER_LOGS = env("AWS_DOCKER_LOGS")

AWS_DOCKER_TASK_USE_FARGATE = env("AWS_DOCKER_TASK_USE_FARGATE")
AWS_DOCKER_TASK_EXECUTION_ROLE_ARN = env("AWS_DOCKER_TASK_EXECUTION_ROLE_ARN")
AWS_DOCKER_TASK_ROLE_ARN = env("AWS_DOCKER_TASK_ROLE_ARN")
AWS_DOCKER_RUNNER_TASK_SUBNETS = env("AWS_DOCKER_RUNNER_TASK_SUBNETS")
AWS_DOCKER_RUNNER_TASK_SECURITY_GROUP = env("AWS_DOCKER_RUNNER_TASK_SECURITY_GROUP")

# SensiML Analytic Engine Code Generation settings
CODEGEN_SUPPORT_SRC_DIR = os.path.join(BASE_DIR, "codegen", "templates")
CODEGEN_SUPPORT_DIR = CODEGEN_SUPPORT_SRC_DIR
CODEGEN_PLATFORM_DIR = os.path.join(CODEGEN_SUPPORT_SRC_DIR, "compilers")
CODEGEN_C_FUNCTION_LOCATION = os.path.join(BASE_DIR, "../", "embedded_ml_sdk")
CODEGEN_C_UTEST_FUNCTION_LOCATION = os.path.join(BASE_DIR, "../", "utest")
CODEGEN_TENSORFLOW_PLATFORM_VERSION = env("CODEGEN_TENSORFLOW_PLATFORM_VERSION")

STARTER_CLASSIFICATION_LIMIT = env("STARTER_CLASSIFICATION_LIMIT")
BASIC_EDITION_SAMPLE_RATE_LIMIT = env("BASIC_EDITION_SAMPLE_RATE_LIMIT")
ALLOW_UPDATE_PROJECT_SCHEMA = env("ALLOW_UPDATE_PROJECT_SCHEMA")

# Bonsai C++ library
BONSAI = env("BONSAI")

CLASSIFIER_LIBS = env("CLASSIFIER_LIBS")
KB_CODEGEN_REMOVE_LOCAL_FILES = False

# SensiML Analytic Engine device budgets
KB_BUDGETS = {}


FILE_UPLOAD_HANDLERS = ["django.core.files.uploadhandler.TemporaryFileUploadHandler"]

# Size in bytes to chunk file uploads when using chunks()
FILE_UPLOAD_CHUNK_SIZE = 67108864
# Max filesize in bytes
FILE_UPLOAD_LARGE_SIZE = 33554432
FILE_UPLOAD_LARGE_QUEUE_NAME = "file_upload_large"

# Background Capture UUID
BACKGROUND_CAPTURE_PROJECT_UUID = "a81b4147-bb65-41f5-bfe1-f37e2bd18c4c"
BACKGROUND_CAPTURE_PROJECT_NAME = "BackgroundCaptureProject_f5fe5936"
BACKGROUND_CAPTURE_S3_BUCKET = "sml-config"
BACKGROUND_CAPTURE_S3_FOLDER = "BackgroundCaptures"

BANNED_FILE_EXTENSIONS = (
    ".exe",
    ".scr",
    ".msi",
    ".cmd",
    ".bat",
    ".js",
    ".node",
    ".py",
    ".pyw",
    ".vbs",
    ".ps1",
    ".sh",
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "server/static")]
STATIC_ROOT = os.path.join(BASE_DIR, "static")
OAUTH_CLIENT_ID = env("OAUTH_CLIENT_ID", default=None)
OAUTH_CLIENT_SECRET = env("OAUTH_CLIENT_SECRET", default=None)

ACTIVATION_CODE_AUTH = env("ACTIVATION_CODE_AUTH")

JWT = {
    # Accepted algorithms for decoder
    "ALGORITHMS": ["RS256", "RS512", "HS256", "HS512"],
    "OPTIONS": {"require_exp": True, "require_iat": True, "verify_aud": False},
    "ALGORITHM": "HS256",  # Algorithm to use when signing new tokens
    "TTL": 86400,  # token lifetime in seconds
    "SIGNING_KEY": SECRET_KEY,
    "VERIFICATION_KEY": SECRET_KEY,  # Shared secret or public key
    # allowed scopes
    "SCOPES": ["jv.data", "jv.user", "jv.admin", "jv.pipeline"],
}

INTERNAL_IPS = iptools.IpRangeList(
    *env(
        "INTERNAL_IPS",
        default=[
            "127.0.0.0/8",
            "192.55.54.32/27",
            "192.55.55.32/27",
            "198.175.68.32/27",
            "192.55.79.160/27",
            "134.134.139.64/27",
            "134.134.137.64/27",
            "134.191.232.64/27",
            "192.198.151.32/27",
            "134.191.220.64/27",
            "134.191.221.64/27",
            "192.198.147.160/27",
            "192.198.146.160/27",
            "192.102.204.32/27",
            "58.32.203.133/32",
            "58.32.203.132/32",
            "192.55.46.32/27",
        ],
    )
)


try:
    import json
    import warnings

    with open(os.path.join(SITE_ROOT, "..", "..", "environ_config.json")) as f:
        globals().update(json.load(f))
    warnings.warn(
        "environ_config.json is deprecated and will be removed. Please use environmental variables or .env",
        DeprecationWarning,
    )
except (IOError, ValueError):
    pass

try:
    pass

    warnings.warn(
        "Using multiple configuration files is deprecated and will be removed. Please use environmental variables or .env",
        DeprecationWarning,
    )
except ImportError:
    pass
