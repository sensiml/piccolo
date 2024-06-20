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
from uuid import uuid4
from pandas import Series

from datamanager.featurefile import (
    _get_featurefile_name,
    _get_featurefile_datastore,
    _locate_feature_file,
)
from datamanager.models import FeatureFile, FeatureFileAnalysis, Label
from datamanager.utils.feature_clustering import (
    FeatureClustering,
    NotEnoughSamplesException,
)
from django.core import serializers as django_serializers
from django.urls import re_path as url
from django.conf import settings
from drf_spectacular.utils import extend_schema, extend_schema_view
from engine.base.pipeline_utils import get_featurefile_folder_path
from rest_framework import generics, permissions, serializers, status
from rest_framework.response import Response
from rest_framework.urlpatterns import format_suffix_patterns


class FeatureFileAnalysisGenerateSerializer(serializers.Serializer):
    """Validates Async execute data"""

    analysis_type = serializers.ChoiceField(
        ["UMAP", "PCA", "TSNE"],
        default="UMAP",
    )

    shuffle_seed = serializers.IntegerField(default=0)
    analysis_seed = serializers.IntegerField(default=0)
    analysis_method = serializers.CharField(default="barnes_hut")
    n_neighbor = serializers.IntegerField(default=0)
    n_components = serializers.IntegerField(default=2)
    n_sample = serializers.IntegerField(default=settings.MAX_FEATUREFILE_RETURN_SIZE)


class FeatureFileAnalysisSerializer(serializers.ModelSerializer):
    """FeatureFile Serializer"""

    analysis_type = serializers.SerializerMethodField()

    analysis_type = serializers.SerializerMethodField()

    class Meta:
        model = FeatureFileAnalysis
        read_only_fields = ("uuid",)
        exclude = ("id", "path")

    def get_analysis_type(self, obj):
        if obj.analysis_type:
            return obj.get_analysis_type_display()
        return ""


def _serializer(featurefile):
    value = django_serializers.serialize(
        "json", [featurefile], fields=("name", "uuid", "is_features")
    )
    return json.loads(value)[0]["fields"]


@extend_schema_view(
    get=extend_schema(
        summary="List all feature analysis data files",
        description="Returns the list of all feature analysis data files given uuid",
    ),
    delpostete=extend_schema(
        summary="Generate a new feature analysis",
        description="Returns the meta data of the generated analysis file",
    ),
)
class FeatureFileAnalsysisView(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    )
    serializer_class = FeatureFileAnalysisSerializer
    lookup_field = "uuid"

    def get_serializer_class(self):
        if self.request.method in ["POST"]:
            return FeatureFileAnalysisGenerateSerializer

        return FeatureFileAnalysisSerializer

    def get_queryset(self):
        queryset = FeatureFile.objects.with_user(self.request.user).filter(
            project__uuid=self.kwargs["project_uuid"],
            uuid=self.kwargs["uuid"],
        )
        return queryset

    def list(self, request, *args, **kwargs):
        featurefile = self.get_object()
        queryset = FeatureFileAnalysis.objects.filter(
            featurefile=featurefile,
        )
        serializer = FeatureFileAnalysisSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):

        serializer_calss = self.get_serializer_class()

        serializer = serializer_calss(data=request.data, context={"request": request})

        serializer.is_valid(raise_exception=True)

        project_id = self.kwargs["project_uuid"]
        feature_file_id = self.kwargs["uuid"]
        user = request.user

        feature_file = _locate_feature_file(user, project_id, feature_file_id)
        project = feature_file.project
        s3 = _get_featurefile_datastore(feature_file)

        feature_file_df = s3.get_data(_get_featurefile_name(feature_file))

        shuffle_seed = serializer.data.get("shuffle_seed")
        analysis_seed = serializer.data.get("analysis_seed")
        analysis_method = serializer.data.get("analysis_method")
        n_neighbor = serializer.data.get("n_neighbor")
        n_components = serializer.data.get("n_components")
        n_sample = serializer.data.get("n_sample")

        analysis_type = serializer.data.get("analysis_type")

        label_column = feature_file.label_column
        if label_column is None:
            labels = Label.objects.filter(project__uuid=project_id, metadata=False)
            for label in labels:
                if label.name in feature_file_df.columns:
                    label_column = label.name

        fc = FeatureClustering(
            feature_file_df,
            label_column=label_column,
            shuffle_seed=shuffle_seed,
            n_sample=n_sample,
        )

        if analysis_type == "UMAP":
            try:
                output = fc.compute_umap(
                    n_components=n_components,
                    n_neighbor=n_neighbor,
                    random_state=analysis_seed,
                )
            except NotEnoughSamplesException as e:
                return Response(
                    data={"message": e.message}, status=status.HTTP_400_BAD_REQUEST
                )
            n_neighbor = output["n_neighbor"]
        elif analysis_type == "PCA":
            output = fc.compute_pca(
                n_components=n_components,
            )
        elif analysis_type == "TSNE":
            output = fc.compute_tsne(
                n_components=n_components,
                random_state=analysis_seed,
                method=analysis_method,
            )

        result = output["result"]

        # rounding off, fixing decimal precession
        roundoff_place = 2
        cols = [col for col in result.columns if analysis_type in col]
        decimals = Series([roundoff_place] * len(cols), index=cols)
        result = result.round(decimals)

        n_components = output["n_components"]
        n_sample = output["n_sample"]

        params = {
            "shuffle_seed": shuffle_seed,
            "analysis_seed": analysis_seed,
            "analysis_method": analysis_method,
            "n_neighbor": n_neighbor,
            "n_components": n_components,
            "n_sample": n_sample,
        }

        file_uuid = uuid4()

        fmt = ".csv.gz"
        file_name = "{}{}".format(file_uuid, fmt)

        analysis_type_dict = {
            "UMAP": FeatureFileAnalysis.AnalysisTypeEnum.UMAP,
            "TSNE": FeatureFileAnalysis.AnalysisTypeEnum.TSNE,
            "PCA": FeatureFileAnalysis.AnalysisTypeEnum.PCA,
        }

        folder_path = get_featurefile_folder_path(project)
        feature_file_analysis = FeatureFileAnalysis(
            uuid=file_uuid,
            project=project,
            name=str(file_uuid),
            format=fmt,
            is_features=True,
            path=folder_path,
            version=2,
            label_column=label_column,
            featurefile=feature_file,
            analysis_type=analysis_type_dict[analysis_type],
            params=params,
            number_rows=int(n_sample),
        )

        feature_file_analysis.save()

        s3.save_data(result, file_name, fmt=fmt)

        out_dict = FeatureFileAnalysisSerializer(feature_file_analysis).data

        return Response(out_dict)


urlpatterns = format_suffix_patterns(
    [
        url(
            r"^project/(?P<project_uuid>[^/]+)/featurefile-analysis/(?P<uuid>[^/]+)/$",
            FeatureFileAnalsysisView.as_view(),
            name="featurefile-analysis-list-create",
        ),
    ]
)
