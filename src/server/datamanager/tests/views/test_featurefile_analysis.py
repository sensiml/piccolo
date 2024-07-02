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

# pylint: disable=W0201
import logging
import os

import pandas as pd
import pytest
from datamanager.models import FeatureFile, FeatureFileAnalysis, Project, Team
from django.conf import settings
from rest_framework import status
from rest_framework.reverse import reverse

pytestmark = pytest.mark.django_db  # All tests use db

logger = logging.getLogger(__name__)

TEAM_NAME = "SensimlDevTeam"


####################################################################################
@pytest.fixture
def project():
    project = Project.objects.create(
        name="APITestProject",
        team=Team.objects.get(name=TEAM_NAME),
    )

    return project


####################################################################################
@pytest.fixture
def featurefile(project):
    featurefile = FeatureFile.objects.create(
        name="TestFile",
        project=project,
        format=".data_0.csv.gz",
        path="",
        is_features=True,
    )
    return featurefile


####################################################################################
@pytest.fixture
def featurefileanalysis(project, featurefile):
    featurfile_analysis = FeatureFileAnalysis.objects.create(
        name="Test.UMAP",
        project=project,
        featurefile=featurefile,
        is_features=True,
        path="",
        format=".csv.gz",
        analysis_type=FeatureFileAnalysis.AnalysisTypeEnum.UMAP,
        label_column="label",
    )

    featurfile_analysis = FeatureFileAnalysis.objects.create(
        name="Test.PCA",
        project=project,
        featurefile=featurefile,
        is_features=True,
        path="",
        format=".csv.gz",
        analysis_type=FeatureFileAnalysis.AnalysisTypeEnum.PCA,
        label_column="label",
    )


####################################################################################
def insert_feature_file(client, project):

    featurefile_list_url = reverse(
        "feature-file",
        kwargs={"project_uuid": project.uuid},
    )

    dirname = os.path.dirname(__file__)

    template_path = os.path.join(dirname, "data/feature_test_file.csv")

    with open(template_path, "rb") as f:
        response = client.post(
            featurefile_list_url,
            format="multipart",
            data={
                "file": f,
                "name": "test.csv",
                "is_features": True,
                "label_column": "myLabel",
            },
        )

    assert response.status_code == status.HTTP_200_OK

    return response


####################################################################################
@pytest.mark.usefixtures("authenticate")
def test_list_featurefile_analysis(client, project, featurefile, featurefileanalysis):
    featurefile_detail_url = reverse(
        "featurefile-analysis-list-create",
        kwargs={"project_uuid": project.uuid, "uuid": featurefile.uuid},
    )
    response = client.get(
        featurefile_detail_url,
    )

    # testing if the response is correct
    res = response.json()

    names = ["Test.PCA", "Test.UMAP"]

    assert len(res) == len(names)

    for r in res:
        assert "uuid" in r
        assert "name" in r
        r["name"] in names

        assert r["analysis_type"][0] == r["name"].split(".")[1][0]
        assert r["label_column"] == "label"


####################################################################################
@pytest.mark.usefixtures("authenticate")
def test_get_featurefile_analysis(client, project):

    settings.DEBUG = True

    response = insert_feature_file(client, project)
    featurefile_uuid = response.json()["uuid"]

    for analysis_type in ["UMAP", "PCA", "TSNE"]:
        featurefile_detail_url = reverse(
            "featurefile-analysis-list-create",
            kwargs={"project_uuid": project.uuid, "uuid": featurefile_uuid},
        )

        # COMPUTE THE ANLSYSIS
        response = client.post(
            featurefile_detail_url,
            data={"analysis_type": analysis_type, "shuffle_seed": 10, "n_sample": 30},
        )

        feature_analysis_data = response.json()

        feature_file_json_url = reverse(
            "feature-file-json",
            kwargs={
                "project_uuid": project.uuid,
                "uuid": feature_analysis_data["uuid"],
            },
        )

        # DATA FOR ANALYSIS OF THE FILE AS JSON
        res = client.get(feature_file_json_url)
        data = res.json()

        df = pd.DataFrame.from_dict(data)

        components_columns = [
            col for col in df.columns if col.split("_")[0] == analysis_type
        ]

        # testing if the number of stored components are the same as n_components in metadata
        assert feature_analysis_data["params"]["n_components"] == len(
            components_columns
        )

        # testing the number of rows. Must be equals n_sample
        assert df.shape[0] == 30


####################################################################################
@pytest.mark.usefixtures("authenticate")
def test_create_featurefile_analysis(client, project):
    settings.DEBUG = True

    response = insert_feature_file(client, project)

    featurefile_uuid = response.json()["uuid"]

    featurefile_detail_url = reverse(
        "featurefile-analysis-list-create",
        kwargs={"project_uuid": project.uuid, "uuid": featurefile_uuid},
    )
    response = client.get(
        featurefile_detail_url,
    )

    # There should be NO analysis file once a new feature file is inserted
    assert response.json() == []

    for analysis_type in ["UMAP", "TSNE", "PCA"]:
        featurefile_detail_url = reverse(
            "featurefile-analysis-list-create",
            kwargs={"project_uuid": project.uuid, "uuid": featurefile_uuid},
        )

        # COMPUTE THE ANLSYSIS
        response = client.post(
            featurefile_detail_url,
            data={"analysis_type": analysis_type, "shuffle_seed": 10, "n_sample": 300},
        )

        # Response should have the FeatureFileAnalysis object info with a uuid in there
        res = response.json()
        assert "uuid" in res
        assert "analysis_type" in res
        assert res["analysis_type"] == analysis_type

    featurefile_detail_url = reverse(
        "featurefile-analysis-list-create",
        kwargs={"project_uuid": project.uuid, "uuid": featurefile_uuid},
    )

    # LIST THE ANALYSIS DONE FOR THE FEATURE FILE WE ARE ANALYZING
    response = client.get(
        featurefile_detail_url,
    )

    # Response must have the UMAP, TSNE, PCA
    res = response.json()
    assert len(res) == 3

    type_ = ["UMAP", "TSNE", "PCA"]
    type_.sort()
    type__ = []
    for r in res:
        assert r["analysis_type"] in type_
        type__.append(r["analysis_type"])
    type__.sort()
    assert type_ == type__
