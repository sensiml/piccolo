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

from datamanager.models import Sandbox, Team
from django.db import models
from django.db.models import JSONField
from engine.base.cache_manager import CacheManager


def evict_sandbox_caches_for_transform(sender, instance, **kwargs):
    """Find all sandboxes that use the given transform and evict their caches from that step forward."""
    sandboxes = Sandbox.objects.exclude(cache__isnull=True)
    for sandbox in [
        s for s in sandboxes if json.dumps(s.cache).find(instance.name) > 0
    ]:
        # Find the step index of the first instance of the transform
        cache = sandbox.cache
        eviction_point_found = False
        while not eviction_point_found:
            if isinstance(cache, dict):
                for i, step in enumerate(cache["pipeline"]):
                    if json.dumps(step).find('"{0}"'.format(instance.name)) > 0:
                        cache_manager = CacheManager(
                            sandbox, sandbox.pipeline, pipeline_id=sandbox.uuid
                        )
                        cache_manager.evict(i)
                        eviction_point_found = True
            eviction_point_found = True  # Stop looping if no eviction point is found


class ArchitectureDescription(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class CompilerDescription(models.Model):
    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid4, editable=False
    )
    name = models.CharField(max_length=255, default="")
    supported_arch = models.ForeignKey(
        ArchitectureDescription, on_delete=models.CASCADE
    )
    compiler_version = models.CharField(max_length=64)
    docker_image_base = models.CharField(max_length=255)
    docker_image_version = models.CharField(max_length=12, default="")

    def __str__(self):
        return "%s %s" % (self.name, self.compiler_version)

    def to_target_compiler(self):
        return {
            "compiler": self.name,
            "architecture": self.supported_arch.name,
            "version": self.compiler_version,
            "docker_image_base": self.docker_image_base,
        }


class ProcessorDescription(models.Model):
    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid4, editable=False
    )
    architecture = models.ForeignKey(ArchitectureDescription, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=255)
    manufacturer = models.CharField(max_length=255, default="")
    compiler_cpu_flag = models.CharField(max_length=100)
    float_options = JSONField(null=False, default=list)
    profiling_enabled = models.BooleanField(default=False)
    clock_speed_mhz = models.IntegerField(default=1)

    def __str__(self):
        if self.manufacturer is not None or self.manufacturer != "":
            return "%s %s" % (self.manufacturer, self.display_name)
        else:
            return "%s" % (self.display_name)

    def to_target_processor(self):
        return {
            "manufacturer": self.manufacturer,
            "architecture": self.architecture.name,
            "display_name": self.display_name,
            "cpu_flag": self.compiler_cpu_flag,
            "float_options": self.float_options,
        }


class PlatformDescriptionVersion2(models.Model):
    PLATFORM_TYPES = (("devkit", "devkit"), ("compiler", "compiler"))

    uuid = models.UUIDField(
        primary_key=True, unique=True, default=uuid4, editable=False
    )
    name = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=1000, null=True)
    processors = models.ManyToManyField(ProcessorDescription)
    can_build_binary = models.BooleanField(default=False)
    codegen_parameters = JSONField(null=False, default=dict)
    docker_image = models.CharField(max_length=255, null=True)
    docker_image_version = models.CharField(max_length=12, null=True, default=None)
    hardware_accelerators = JSONField(null=False, default=dict)
    platform_versions = JSONField(null=False, default=list)
    codegen_file_location = JSONField(null=False, default=list)
    # permissions lets us add enterprise, etc.
    permissions = JSONField(null=False, default=dict)
    default_selections = JSONField(null=False, default=dict)
    supported_source_drivers = JSONField(null=False, default=dict)
    supported_compilers = models.ManyToManyField(CompilerDescription)
    applications = JSONField(null=False, default=dict)
    nn_inference_engines = JSONField(null=False, default=dict)
    platform_type = models.CharField(
        max_length=8, choices=PLATFORM_TYPES, default="devkit"
    )
    documentation = models.CharField(max_length=255, null=True)
    manufacturer = models.CharField(max_length=64, null=True)


class LibraryPack(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    team = models.ForeignKey(Team, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    build_version = models.BigIntegerField(default=None, null=True, blank=True)
    description = models.CharField(max_length=512, null=True)
    maintainer = models.CharField(max_length=255, null=True)


class Transform(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    name = models.CharField(max_length=255)
    function_in_file = models.CharField(max_length=255)
    input_contract = JSONField(null=True)
    output_contract = JSONField(null=True)
    c_contract = JSONField(null=True)
    description = models.TextField(null=True)
    path = models.CharField(max_length=4096)
    type = models.CharField(max_length=22, null=True)
    subtype = models.CharField(max_length=22, null=True)
    has_c_version = models.BooleanField(default=False)
    c_file_name = models.CharField(max_length=255, null=True)
    core = models.BooleanField(default=False)
    dcl_executable = models.BooleanField(default=False)
    c_function_name = models.CharField(max_length=255, null=True)
    version = models.IntegerField(null=True)
    deprecated = models.BooleanField(default=False)
    automl_available = models.BooleanField(default=True)
    library_pack = models.ForeignKey(LibraryPack, null=True, on_delete=models.CASCADE)
    custom = models.BooleanField(default=False)

    class Meta:
        unique_together = (("name", "library_pack"), ("library_pack", "c_file_name"))


class CustomTransform(Transform):
    file_path = models.CharField(max_length=40, unique=True, default=uuid4)
    task = models.CharField(max_length=64, null=True, default=None)
    task_result = models.TextField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    logs = models.TextField(null=True, default=None)
    unit_tests = JSONField()


class FunctionCost(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    function = models.ForeignKey(
        Transform, blank=True, null=True, on_delete=models.CASCADE
    )
    processor = models.ForeignKey(
        ProcessorDescription, null=True, blank=True, on_delete=models.CASCADE
    )
    c_function_name = models.CharField(max_length=255)
    function_type = models.CharField(max_length=255)
    flash = models.CharField(max_length=255)
    sram = models.CharField(max_length=255)
    stack = models.CharField(max_length=255)
    latency = models.CharField(max_length=255)
    cycle_count = models.CharField(default="0", max_length=255)
    flash_dependencies = JSONField(null=False, default=list)
    stack_dependencies = JSONField(null=False, default=list)


class PipelineSeed(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=1000)
    pipeline = JSONField(null=True)
    input_contract = JSONField(null=True)


class ParameterInventory(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid4)
    function = models.ForeignKey(
        Transform, blank=True, null=True, on_delete=models.CASCADE
    )
    function_name = models.CharField(max_length=255)
    variable_name = models.CharField(max_length=255, null=True)
    variable_type = models.CharField(max_length=255, null=True)
    variable_values = JSONField(null=True)
    pipeline_key = models.CharField(max_length=255)
    classifiers_optimizers_group = models.IntegerField(default=0, null=True)
    binary_classifiers = models.BooleanField(default=False, null=True)
    allow_unknown = models.BooleanField(default=False, null=True)

    class Meta:
        unique_together = ("function", "variable_name")
