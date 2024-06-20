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

from django.db.models import JSONField
from django.db import models

from datamanager.models import Capture, KnowledgePack, Project, Sandbox, Team


class LogLevel(models.Model):
    name = models.CharField(max_length=100, unique=True, null=False)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Log(models.Model):
    loglevel = models.ForeignKey(LogLevel, null=True, on_delete=models.SET_NULL)
    application = models.ForeignKey(Application, null=True, on_delete=models.SET_NULL)
    message = models.CharField(max_length=500, null=True)
    stacktrace = models.TextField(blank=True)
    username = models.CharField(max_length=150, null=True)
    tag = models.ManyToManyField(Tag)
    client_information = JSONField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)


class UsageLog(models.Model):
    operation = models.CharField(max_length=32)
    team = models.ForeignKey(Team, null=True, on_delete=models.SET_NULL)
    project = models.ForeignKey(Project, null=True, on_delete=models.SET_NULL)
    pipeline = models.ForeignKey(Sandbox, null=True, on_delete=models.SET_NULL)
    knowledgepack = models.ForeignKey(
        KnowledgePack, null=True, on_delete=models.SET_NULL
    )
    capture = models.ForeignKey(Capture, null=True, on_delete=models.SET_NULL)
    process_id = models.CharField(max_length=36, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    runtime = models.IntegerField(null=True)
    detail = JSONField(null=True, default=None)
