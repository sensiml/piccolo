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
import os

from datamanager.models import Sandbox
from django.http import HttpResponse
from engine.base.cache_manager import CacheManager


def get_iteration_results(request, **kwargs):
    if request.method == "GET":
        sandbox = Sandbox.objects.with_user(
            uuid=kwargs["sandbox_uuid"],
            user=request.user,
            project__uuid=kwargs["project_uuid"],
        )[0]

        # read from cache
        cache_obj = CacheManager(sandbox, None)

        try:
            fitted_population_log, _ = cache_obj.get_result_from_cache(
                f"fitted_population_log.{kwargs['sandbox_uuid']}"
            )
        except:  # (FileNotFoundError, NoSuchKey)
            fitted_population_log = None

        if fitted_population_log is None:
            results = json.dumps({})
        else:
            results = json.dumps(fitted_population_log)

        return HttpResponse(results, content_type="application/json")


def get_pipeline_schema_rules(request):
    if request.method == "GET":
        with open(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "../../library/fixtures/pipeline_schema.json",
            )
        ) as f:
            pipeline_hierarchy = json.load(f)

        return HttpResponse(
            json.dumps(pipeline_hierarchy), content_type="application/json"
        )
