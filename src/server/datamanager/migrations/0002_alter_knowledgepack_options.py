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

# Generated by Django 3.2.12 on 2024-06-21 07:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("datamanager", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="knowledgepack",
            options={
                "permissions": (
                    ("can_get_source", "Can get source builds of knowledgepacks"),
                    (
                        "can_get_enterprise",
                        "Can get enterprise builds of knowledgepacks",
                    ),
                    ("can_get_developer", "Can get developer builds of knowledgepacks"),
                    (
                        "has_classification_limit",
                        "Has limited number of classifications on binary builds.",
                    ),
                    (
                        "has_sample_rate_limit",
                        "Sample rate of knowledgepack device limited to < 10kHz",
                    ),
                ),
                "verbose_name": "Knowledge Pack",
                "verbose_name_plural": "Knowledge Packs",
            },
        ),
    ]
