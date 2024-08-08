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

from django.db import migrations
from django.conf import settings


def get_database_user():
    return settings.DATABASES["default"]["USER"]


class Migration(migrations.Migration):

    dependencies = [
        ("datamanager", "0002_alter_knowledgepack_options"),
    ]

    operations = [
        migrations.RunSQL(
            f"""DO
$do$
BEGIN
   IF EXISTS (
      SELECT                       -- SELECT list can stay empty for this
      FROM   pg_user
      WHERE  usename = '{get_database_user()}' AND usesuper = 't') THEN
      CREATE EXTENSION IF NOT EXISTS tablefunc;
   END IF;
END
$do$;"""
        )
    ]
