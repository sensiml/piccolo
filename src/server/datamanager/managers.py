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

from django.contrib.auth.models import UserManager
from django.db import models


logger = logging.getLogger(__name__)


class TeamMemberManager(UserManager):
    pass


class TeamLimitedManager(models.Manager):
    def __init__(self, relation_to_team=None):
        super(TeamLimitedManager, self).__init__()
        self.relation_to_team = relation_to_team

    def with_user(self, user, **kwargs):
        objects = super(TeamLimitedManager, self).get_queryset()
        if self.relation_to_team is None:
            raise Exception("Relation to team not configured for this model!")

        kwargs.update({self.relation_to_team + "__pk": user.teammember.team.pk})

        return objects.filter(**kwargs)
