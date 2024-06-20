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

from rest_framework import serializers


class SandboxAsyncSerializer(serializers.Serializer):
    """Validates Async execute data"""

    execution_type = serializers.ChoiceField(
        ["pipeline", "grid_search", "auto", "autosegment_search", "automlv2"],
        default="pipeline",
    )
    grid_params = serializers.JSONField(required=False)
    auto_params = serializers.JSONField(required=False)
    run_parallel = serializers.BooleanField(required=False)
