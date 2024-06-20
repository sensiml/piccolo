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

from datamanager.models import Project, Sandbox


def _check_parents(user, project_id):
    return Project.objects.with_user(
        user=user,
        uuid=project_id,
    ).exists()


def _get_project(user, project_id):
    return Project.objects.with_user(user=user).get(uuid=project_id)


def _locate_sandbox(user, project_id, sandbox_id=""):
    sandboxes = Sandbox.objects.with_user(
        user=user,
        project__uuid=project_id,
    )
    return sandboxes if sandbox_id == "" else sandboxes.get(uuid=sandbox_id)
