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

from datamanager import featurefile, recognizevector, sandbox
from datamanager.views.automl import get_iteration_results, get_pipeline_schema_rules
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django.urls import re_path as url
from django.views.generic import TemplateView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

admin.autodiscover()


urlpatterns = [
    # Please note that this first block of urls has mislabeled parameters: *_id actually refers to *_uuid
    # TODO: Someone should fix this
    url(
        r"^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/recognize_features/$",
        recognizevector.recognize_features,
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/recognize_signal/$",
        recognizevector.RecognizeAsyncView.as_view(),
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/knowledgepack/(?P<uuid>[^/]+)/recognize_signal/$",
        recognizevector.RecognizeAsyncView.as_view(),
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/featurefile/$",
        featurefile.feature_file,
        name="feature-file",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/featurefile/(?P<uuid>[^/]+)/$",
        featurefile.feature_file,
        name="feature-file-detail",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/featurefile/(?P<uuid>[^/]+)/data/$",
        featurefile.feature_file_binary,
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/featurefile/(?P<uuid>[^/]+)/json/$",
        featurefile.feature_file_json,
        name="feature-file-json",
    ),
    url(r"^get-metrics-set/$", sandbox.sandbox_get_metrics_set),
    # required for Django Rest Framework
    url(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^", include("datamanager.urls")),
    url(r"^", include("library.urls")),
    url(r"^", include("logger.urls")),
    url(
        r"^admin/login/",
        admin.site.login,
        kwargs={"extra_context": {"is_nav_sidebar_enabled": False}},
    ),
    # Django doesn't render the favicon
    url(r"^favicon.ico", lambda request: HttpResponse(status=204)),
    url(r"^index$", TemplateView.as_view(template_name="index.html")),
    # get automl calls
    url(
        r"^automl/pipeline-schema-rules/",
        get_pipeline_schema_rules,
        name="pipeline_schema_rules",
    ),
    url(
        r"^automl/pipeline-hierarchy-rules/",
        get_pipeline_schema_rules,
        name="pipeline_schema_rules_alias",
    ),
    url(
        r"^project/(?P<project_uuid>[^/]+)/sandbox/(?P<sandbox_uuid>[^/]+)/automl-iteration-metrics/$",
        get_iteration_results,
        name="iteration_results",
    ),
    path("oauth/", include('oauth2_provider.urls', namespace='oauth2_provider')),
    # YOUR PATTERNS
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "api/",
        SpectacularSwaggerView.as_view(),
        name="swagger-ui",
    ),
    url(r"^$", TemplateView.as_view(template_name="webui/index.html")),
]

admin.site.site_header = settings.ADMIN_SITE_HEADER
admin.site.title = settings.ADMIN_SITE_TITLE
