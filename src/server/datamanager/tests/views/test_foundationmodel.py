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

import pytest
from datamanager.models import FoundationModel
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)


@pytest.fixture
def foundation_models():
    foundation_models = []
    for i in range(1000):
        foundation_models.append(
            FoundationModel.objects.create(
                name="TestKnowledgePack_{}".format(i),
                model_results={
                    "model_size": 5488,
                    "metrics": {"validation": {"accuracy": 99.99}},
                },
                feature_summary=[
                    {"Feature": "gen_0013_GyroscopeXZeroCrossingRate"},
                    {"Feature": "gen_0014_GyroscopeYZeroCrossingRate"},
                    {"Feature": "gen_0016_AccelerometerXZeroCrossingRate"},
                ],
            )
        )

    return foundation_models


def find(name, kpList):
    for kp in kpList:
        if kp.name == name:
            return kp
    return None


@pytest.mark.usefixtures("authenticate")
def test_foundation_models(client, foundation_models):

    import time

    start = time.time()
    response = client.get(reverse("foundation-model-list"))
    print(time.time() - start)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1000

    result1 = response.data[0]
    kp = find(result1["name"], foundation_models)
    assert result1["features_count"] == len(kp.feature_summary)
    assert result1["model_size"] == kp.model_results["model_size"]
