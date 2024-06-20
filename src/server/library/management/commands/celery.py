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

import sys
from subprocess import call

from django.conf import settings
from django.core.management import BaseCommand


class bcolors:
    BLUE = "\033[94m"
    NC = "\033[0m"


class Command(BaseCommand):
    help = (
        bcolors.BLUE
        + "This script allows for running celery queues in dev mode"
        + bcolors.NC
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "queue",
            action="store",
            type=str,
            help=self.style.WARNING(
                "Select from a comma separated list of queues to run eg "
            )
            + self.style.MIGRATE_HEADING("(pipeline,knowledgepack). ")
            + self.style.WARNING("This is a required argument"),
        )
        parser.add_argument(
            "--loglevel",
            action="store",
            type=str,
            choices=["INFO", "WARNING", "ERROR", "DEBUG"],
            default="DEBUG",
            dest="loglevel",
            help=self.style.WARNING(
                "Sets the logging level of the celery queue you are running."
            )
            + self.style.MIGRATE_HEADING(" Default=DEBUG"),
        )

    def handle(self, *args, **options):
        queue = options.get("queue")
        queue_settings = [
            value["queue"] for key, value in settings.CELERY_ROUTES.items()
        ]
        invalid_queue = False

        # check that commas are properly formatted
        queue_entry = queue.split(",")
        for i in [0, -1]:
            if queue_entry[i] == None or queue_entry[i] == "":
                self.stdout.write(
                    self.style.ERROR(
                        "Stray commas at the beginning and end of your celery queue list are not allowed"
                    )
                )
                self.stdout.write(
                    self.style.ERROR("You entered: ") + self.style.WARNING(queue)
                )
                # sys.exit(1)

        # check that only queues in the settings are specified
        for q in queue_entry:
            if q not in queue_settings:
                self.stdout.write(
                    self.style.ERROR("queue entry: ")
                    + self.style.WARNING(q)
                    + self.style.ERROR(
                        " not found in the available queues list from django settings: "
                    )
                    + self.style.MIGRATE_HEADING(
                        [
                            value["queue"]
                            for key, value in settings.CELERY_ROUTES.items()
                        ]
                    )
                )
                invalid_queue = True

        if invalid_queue == True:
            sys.exit(1)

        loglevel = options.get("loglevel").upper()

        self.stdout.write(
            self.style.SUCCESS("Celery Queue: ") + self.style.MIGRATE_HEADING(queue)
        )
        self.stdout.write(
            self.style.SUCCESS("Loglevel: ") + self.style.MIGRATE_HEADING(loglevel)
        )

        call(
            [
                "celery",
                "--app=server.celery:app",
                "worker",
                "--loglevel=" + loglevel,
                "-Ofair",
                "-Q",
                "celery," + queue,
            ]
        )
