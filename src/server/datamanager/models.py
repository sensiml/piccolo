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

import os
from uuid import uuid4

from datamanager.managers import TeamLimitedManager, TeamMemberManager
from datamanager.datastore import get_datastore
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, JSONField, signals
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy
from engine.base import model_store

# Stored signal (trigger) procedures
def delete_capture_from_disk(sender, instance, **kwargs):
    datastore = get_datastore()
    datastore.delete(instance.file)


def delete_capture_video_from_disk(sender, instance, **kwargs):
    datastore = get_datastore()
    if datastore.is_remote:
        datastore.delete(instance.remote_path)
    else:
        datastore.delete(instance.file_path)


def delete_knowledge_pack_from_disk(sender, instance, **kwargs):
    datastore = get_datastore()
    datastore.delete_path(os.path.join(settings.SERVER_CODEGEN_ROOT, instance.uuid))

    if (
        isinstance(instance.neuron_array, dict)
        and instance.neuron_array.get("model_store", None) is not None
    ):
        if hasattr(instance, "foundationmodel"):
            model_store.delete_model(
                settings.FOUNDATION_MODEL_STORE_PROJECT,
                settings.FOUNDATION_MODEL_STORE_DOMAIN,
                instance.neuron_array["model_store"]["model"]["model_id"],
            )
        else:
            model_store.delete_model(
                instance.sandbox.project.uuid,
                instance.sandbox.uuid,
                instance.neuron_array["model_store"]["model"]["model_id"],
            )


def delete_feature_file_from_disk(sender, instance, **kwargs):
    if (
        KnowledgePack.objects.filter(feature_file_id=instance.feature_file_id).count()
        == 1
    ):
        datastore = get_datastore(folder="featurefile")
        datastore.delete(
            os.path.join(
                instance.feature_file.path,
                instance.feature_file.name + instance.feature_file.format,
            )
        )

        FeatureFile.objects.filter(id=instance.feature_file.id).delete()


def delete_caches_from_disk(sender, instance, cache_folder="pipelinecache", **kwargs):
    if isinstance(instance, Query):
        cache_folder = "querydata"

    if instance.cache:
        datastore = get_datastore(
            bucket=settings.SERVER_BASE_DIRECTORY, folder=cache_folder
        )
        datastore.remove_folder(instance.uuid)


def evict_sandbox_caches_for_query(sender, instance, **kwargs):
    """Finds all associated sandboxes and deletes their caches if they start with a query. The instance argument must
    be a capture or capturelabelvalue."""

    affected_sandboxes = []

    if isinstance(instance, CaptureLabelValue):
        affected_sandboxes = Sandbox.objects.filter(
            project=instance.capture.project
        ).exclude(cache__isnull=True)
    elif isinstance(instance, Capture) or isinstance(instance, Query):
        affected_sandboxes = Sandbox.objects.filter(project=instance.project).exclude(
            cache__isnull=True
        )

    # delete query related things
    delete_caches_from_disk(sender=Sandbox, instance=instance, cache_folder="querydata")

    for sandbox in affected_sandboxes:
        cache = sandbox.cache
        if (
            cache
            and isinstance(cache, dict)
            and "pipeline" in cache
            and len(cache["pipeline"])
            and cache["pipeline"][0]["type"] == "query"
        ):
            if (
                isinstance(instance, Query)
                and cache["pipeline"][0]["name"] != instance.name
            ):
                continue

            # Delete everything in the cache
            delete_caches_from_disk(sender=Sandbox, instance=sandbox)
            sandbox.cache = None
            sandbox.save(update_fields=["cache"])


def evict_sandbox_caches_for_featurefile(sender, instance, **kwargs):
    """Finds all associated sandboxes and deletes their caches if they start with the given featurefile."""
    affected_sandboxes = Sandbox.objects.filter(project=instance.project).exclude(
        cache__isnull=True
    )
    for sandbox in affected_sandboxes:
        cache = sandbox.cache
        if (
            cache
            and isinstance(cache, dict)
            and "pipeline" in cache
            and len(cache["pipeline"])
            and cache["pipeline"][0]["type"] == "featurefile"
            and cache["pipeline"][0]["name"] == instance.name
        ):
            # Delete everything in the cache
            delete_caches_from_disk(sender=Sandbox, instance=sandbox)
        sandbox.cache = None
        sandbox.save(update_fields=["cache"])


def update_capture_last_modified(sender, instance, **kwargs):
    instance.capture.last_modified = timezone.now()
    instance.capture.version = F("version") + 1
    instance.capture.save(update_fields=["last_modified", "version"])


def update_capture_video_last_modified_video(sender, instance, **kwargs):
    instance.capture.last_modified_video = instance.last_modified
    instance.capture.save(update_fields=["last_modified_video"])


def delete_capture_video_last_modified_video(sender, instance, **kwargs):
    capture_video_count = sender.objects.filter(capture=instance.capture).count()
    if capture_video_count == 0:
        instance.capture.last_modified_video = None
        instance.capture.save(update_fields=["last_modified_video"])


# Abstract Base Class for Models


class BaseModel(models.Model):
    # id = models.BigAutoField(primary_key=True) # Not currently supported but will need to be addressed

    class Meta:
        abstract = True


class Team(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    uaa_id = models.CharField(
        unique=True, max_length=200, null=True, blank=True, verbose_name="UAA Client ID"
    )
    uuid = models.CharField(max_length=36, unique=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    internal = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.uuid)

    def __str__(self):
        return str(self.uuid)


@receiver(pre_save, sender=Team)
def team_pre_save(sender, instance, **kwargs):
    if instance.uaa_id == "":
        instance.uaa_id = None


class TeamMember(User):
    user = models.OneToOneField(User, parent_link=True, on_delete=models.CASCADE)
    uuid = models.UUIDField(unique=True, default=uuid4)
    team = models.ForeignKey(
        Team, related_name="teammembers", null=True, on_delete=models.CASCADE
    )
    objects = TeamMemberManager()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "team member"
        verbose_name_plural = "team members"

    def save(self, **kwargs):
        self.username = self.email[:30]
        self.is_staff = True
        return super(TeamMember, self).save(**kwargs)

    def __unicode__(self):
        return self.email

    def __str__(self):
        return self.email


class Project(models.Model):
    name = models.CharField(max_length=200)
    uuid = models.CharField(max_length=36, unique=True, default=uuid4)
    capture_sample_schema = JSONField(null=True, default=None)
    team = models.ForeignKey(Team, null=False, on_delete=models.CASCADE)
    objects = TeamLimitedManager(relation_to_team="team")
    settings = JSONField(null=True, default=None)
    optimized = models.BooleanField(default=False)
    profile = JSONField(null=True, default=None)
    plugin_config = JSONField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    active_pipelines = JSONField(null=True, default=None)
    description = models.TextField(null=True, default=None)
    image_file_name = models.CharField(
        max_length=1100, null=True, unique=True, default=None
    )
    last_modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ("team", "name")


class CaptureConfiguration(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid4)
    name = models.CharField(max_length=255)
    configuration = JSONField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = TeamLimitedManager(relation_to_team="project__team")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("name", "project"), ("project", "uuid"))


class Label(BaseModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="labels", null=True
    )
    name = models.CharField(max_length=1000)
    type = models.CharField(max_length=32)
    uuid = models.UUIDField(unique=True, default=uuid4)
    metadata = models.BooleanField(default=False)
    # defines if a field is selectable through a dropdown or a user can enter text directly
    is_dropdown = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = TeamLimitedManager(relation_to_team="project__team")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "project")


class LabelValue(BaseModel):
    value = models.CharField(max_length=1000)
    label = models.ForeignKey(
        Label, on_delete=models.CASCADE, related_name="label_values"
    )
    color = models.CharField(max_length=9, null=True)
    uuid = models.UUIDField(unique=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = TeamLimitedManager(relation_to_team="project__label__team")

    def __unicode__(self):
        return self.value

    def __str__(self):
        return self.value

    class Meta:
        unique_together = ("label", "value")


class DataTypes(models.IntegerChoices):
    NULL = 0
    INT32 = 1
    FLOAT32 = 2


class Capture(BaseModel):
    name = models.CharField(max_length=250, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="captures"
    )
    file = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.IntegerField(null=True)
    number_samples = models.IntegerField(null=True)
    max_sequence = models.IntegerField(null=True)
    calculated_sample_rate = models.FloatField(null=True)
    set_sample_rate = models.IntegerField(null=True)
    objects = TeamLimitedManager(relation_to_team="project__team")
    uuid = models.CharField(max_length=36, unique=True, default=uuid4)
    task = models.CharField(max_length=64, null=True, default=None)
    task_result = models.CharField(max_length=128, null=True, default=None)
    capture_configuration = models.ForeignKey(
        CaptureConfiguration, null=True, on_delete=models.SET_NULL
    )
    last_modified = models.DateTimeField(auto_now=True)
    last_modified_video = models.DateTimeField(auto_now=False, null=True, default=None)
    version = models.IntegerField(default=0)
    format = models.CharField(max_length=10, default=".csv")
    schema = models.JSONField(null=True)
    datatype = models.SmallIntegerField(
        choices=DataTypes.choices, default=DataTypes.NULL
    )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "project")


signals.pre_delete.connect(delete_capture_from_disk, sender=Capture)


class CaptureVideoTypeEnum(models.TextChoices):
    UPLOADED = "U", gettext_lazy("UPLOADED TO CLOUD")
    REMOTE = "R", gettext_lazy("REMOTE LOCATION")
    STREAM = "S", gettext_lazy("STREAMABLE")


class CaptureVideo(BaseModel):
    uuid = models.UUIDField(unique=True, default=uuid4)
    capture = models.ForeignKey(Capture, on_delete=models.CASCADE)
    video_type = models.CharField(
        max_length=1,
        choices=CaptureVideoTypeEnum.choices,
        default=CaptureVideoTypeEnum.UPLOADED,
        null=True,
    )
    name = models.CharField(max_length=255, blank=True, null=True)  # file name
    file_size = models.IntegerField(null=True)
    keypoints = models.JSONField(null=True)
    is_processed = models.BooleanField(null=True, default=False)
    is_file_deleted = models.BooleanField(null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = TeamLimitedManager(relation_to_team="capture__project__team")

    def __str__(self):
        return self.name

    @property
    def ext(self):
        return os.path.splitext(self.name)[1]

    @property
    def file_path(self):
        return f"{settings.SERVER_CAPTURE_VIDEO_ROOT}/{self.capture.project.uuid}/{self.uuid}{self.ext}"

    @property
    def remote_path(self):
        return f"{settings.CAPTURE_VIDEO_S3_ROOT}/{self.capture.project.uuid}/{self.uuid}{self.ext}"

    @staticmethod
    def get_folder(project_uuid, is_local=True):
        if is_local:
            return f"{settings.SERVER_CAPTURE_VIDEO_ROOT}/{project_uuid}"
        return f"{settings.CAPTURE_VIDEO_S3_ROOT}/{project_uuid}"


signals.pre_delete.connect(delete_capture_video_from_disk, sender=CaptureVideo)
signals.post_delete.connect(
    delete_capture_video_last_modified_video, sender=CaptureVideo
)
signals.post_save.connect(update_capture_video_last_modified_video, sender=CaptureVideo)


class CaptureMetadataValue(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    capture = models.ForeignKey(Capture, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    label_value = models.ForeignKey(LabelValue, on_delete=models.CASCADE)
    objects = TeamLimitedManager(relation_to_team="capture__project__team")
    uuid = models.UUIDField(unique=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("capture", "label")


class CaptureLabelValue(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    capture = models.ForeignKey(Capture, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    label_value = models.ForeignKey(LabelValue, on_delete=models.CASCADE)
    segmenter = models.ForeignKey("Segmenter", on_delete=models.CASCADE, null=True)
    capture_sample_sequence_start = models.BigIntegerField()
    capture_sample_sequence_end = models.BigIntegerField()
    objects = TeamLimitedManager(relation_to_team="capture__project__team")
    uuid = models.UUIDField(unique=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (
            "capture",
            "segmenter",
            "label",
            "label_value",
            "capture_sample_sequence_start",
            "capture_sample_sequence_end",
        )


class Segmenter(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    parent = models.ForeignKey("self", null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    function = models.CharField(max_length=255, null=True)
    parameters = JSONField(null=True, default=None)
    custom = models.BooleanField(default=False)
    preprocess = JSONField(null=True, default=None)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = TeamLimitedManager(relation_to_team="project__team")

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "project")


class Sandbox(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    uuid = models.CharField(max_length=40, unique=True, default=uuid4)
    name = models.CharField(max_length=200)
    pipeline = JSONField(default=None, null=True)
    users = models.ManyToManyField(User)
    objects = TeamLimitedManager(relation_to_team="project__team")
    cache_enabled = models.BooleanField(default=True)
    cache = JSONField(null=True)
    device_config = JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    result_type = models.CharField(max_length=40, default="")
    last_modified = models.DateTimeField(auto_now=True)
    private = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    hyper_params = JSONField(default=None, null=True)
    cpu_clock_time = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Sandboxes"


signals.pre_delete.connect(delete_caches_from_disk, sender=Sandbox)


class PipelineExecution(models.Model):
    class ExecutionTypeEnum(models.TextChoices):
        PIPELINE = "V1", gettext_lazy("PIPE")
        AUTOML = "V2", gettext_lazy("AUTOML")
        RECOGNITION = "V3", gettext_lazy("RECOGNITION")
        CODEGEN = "V4", gettext_lazy("CODEGEN")
        GRIDSEARCH = "V5", gettext_lazy("GRIDSEARCH")
        AUTOSEG = "V6", gettext_lazy("AUTOSEG")

    class ExecutionStatusEnum(models.TextChoices):
        STARTED = "N", gettext_lazy("STARTED")
        SUCCESS = "S", gettext_lazy("SUCCESS")
        FAILED = "F", gettext_lazy("FAILED")

    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    project_uuid = models.UUIDField(default=uuid4)
    pipeline_uuid = models.UUIDField(default=uuid4)
    task_id = models.UUIDField(default=uuid4)
    execution_type = models.CharField(
        max_length=2, choices=ExecutionTypeEnum.choices, null=True
    )
    status = models.CharField(
        max_length=1, choices=ExecutionStatusEnum.choices, null=True
    )


class FeatureFile(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=40, unique=True, default=uuid4)
    name = models.CharField(max_length=200)
    format = models.CharField(max_length=200, default="")
    path = models.CharField(max_length=1024)
    is_features = models.BooleanField(default=False)
    objects = TeamLimitedManager(relation_to_team="project__team")
    created_at = models.DateTimeField(auto_now_add=True)
    version = models.SmallIntegerField(default=2)
    label_column = models.CharField(max_length=64, null=True)
    number_rows = models.IntegerField(default=0, null=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    class Meta:
        unique_together = (("project", "name"),)


class FeatureFileAnalysis(FeatureFile):
    class AnalysisTypeEnum(models.TextChoices):
        PCA = "P", gettext_lazy("PCA")
        UMAP = "U", gettext_lazy("UMAP")
        TSNE = "T", gettext_lazy("TSNE")

    # TODO: investigate related_name
    featurefile = models.ForeignKey(
        FeatureFile, on_delete=models.CASCADE, related_name="+"
    )
    analysis_type = models.CharField(
        max_length=1, choices=AnalysisTypeEnum.choices, null=False
    )
    params = JSONField(default=None, null=True)


class KnowledgePack(models.Model):
    uuid = models.UUIDField(unique=True, default=uuid4)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    sandbox = models.ForeignKey(Sandbox, on_delete=models.SET_NULL, null=True)
    feature_file = models.ForeignKey(FeatureFile, null=True, on_delete=models.SET_NULL)
    # uses Pythons datetime.datetime
    # Note: auto_now/add implicitly set editable to False in django.
    execution_time = models.DateTimeField(auto_now=True, editable=False)
    # Path to file containing JSON string of model generator results
    neuron_array = JSONField(default=None, null=True)
    model_results = JSONField(default=None, null=True)
    configuration_index = models.CharField(max_length=40, null=True)
    name = models.CharField(max_length=40, null=True)
    model_index = models.CharField(max_length=40, null=True)
    pipeline_summary = JSONField(default=None, null=True)
    knowledgepack_summary = JSONField(default=None, null=True)
    query_summary = JSONField(default=None, null=True)
    feature_summary = JSONField(default=None, null=True)
    transform_summary = JSONField(default=None, null=True)
    device_configuration = JSONField(default=None, null=True)
    sensor_summary = JSONField(default=None, null=True)
    class_map = JSONField(default=None, null=True)
    cost_summary = JSONField(default=None, null=True)
    knowledgepack_description = JSONField(default=None, null=True)
    task = models.UUIDField(null=True, blank=True, unique=True)
    logs = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = TeamLimitedManager(relation_to_team="project__team")

    def __unicode__(self):
        return str(self.uuid)

    def __str__(self):
        return str(self.uuid)

    class Meta:
        verbose_name = "Knowledge Pack"
        verbose_name_plural = "Knowledge Packs"

        permissions = (
            ("can_get_source", "Can get source builds of knowledgepacks"),
            ("can_get_enterprise", "Can get enterprise builds of knowledgepacks"),
            ("can_get_developer", "Can get developer builds of knowledgepacks"),
            (
                "has_classification_limit",
                "Has limited number of classifications on binary builds.",
            ),
            (
                "has_sample_rate_limit",
                "Sample rate of knowledgepack device limited to < 10kHz",
            ),
        )


signals.pre_delete.connect(delete_knowledge_pack_from_disk, sender=KnowledgePack)


def default_trainable_layer(*args, **kwargs):
    return {"0": 0}


class FoundationModel(KnowledgePack):
    description = models.CharField(max_length=255, null=True)
    auxiliary_datafile = models.CharField(max_length=255, null=True)
    model_profile = JSONField(default=None, null=True)
    trainable_layer_groups = JSONField(default=default_trainable_layer, null=True)


class Query(models.Model):
    project = models.ForeignKey(Project, null=True, on_delete=models.CASCADE)
    uuid = models.CharField(max_length=40, unique=True, default=uuid4)
    name = models.CharField(max_length=200)
    segmenter = models.ForeignKey(
        Segmenter, null=True, related_name="+", on_delete=models.SET_NULL
    )
    columns = models.CharField(max_length=5000, null=True)
    metadata_columns = models.CharField(max_length=5000, null=True)
    eventlabel_columns = models.CharField(max_length=5000, null=True)
    metadata_filter = models.CharField(max_length=5000, null=True)
    eventlabel_filter = models.CharField(max_length=5000, null=True)
    capture_configurations = models.ManyToManyField(CaptureConfiguration, default=None)
    label_column = models.CharField(max_length=200, null=True)
    combine_labels = JSONField(default=None, null=True)
    objects = TeamLimitedManager(relation_to_team="project__team")
    created_at = models.DateTimeField(auto_now_add=True)
    summary_statistics = JSONField(null=True)
    segment_info = JSONField(null=True)
    cache = JSONField(null=True)
    task = models.UUIDField(null=True, blank=True, unique=True)
    task_status = models.CharField(max_length=5000, null=True)
    last_modified = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = (("project", "name"),)


signals.pre_delete.connect(evict_sandbox_caches_for_query, sender=Query)
signals.pre_delete.connect(delete_caches_from_disk, sender=Query)
