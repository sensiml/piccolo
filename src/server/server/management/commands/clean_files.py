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

from datamanager.models import EventFile, FeatureFile, KnowledgePack, Sandbox
from django.conf import settings
from django.core.management.base import BaseCommand
from library.models import Transform


def clean_file(root, file_name):
    """Deletes the given file from disk."""
    try:
        os.remove("{0}/{1}".format(root, file_name))
    except Exception as e:
        print(e)
        return False

    return True


def compare_and_clean_files(objects_in_db, file_root, dryrun=False):
    """Looks for orphaned files in the given file root, deletes them, and reports the number deleted."""
    counts = {".py": 0, ".pyc": 0, ".csv": 0, ".h5": 0, ".json": 0, ".gen": 0}

    other_files = []
    file_list = os.listdir(file_root)
    for file_ in file_list:
        file_parts = os.path.splitext(os.path.split(file_)[1])
        if file_parts[0] not in objects_in_db:
            if (
                file_parts[1] in [".py", ".pyc", ".csv", ".h5", ".json", ".gen"]
                and file_parts[0] != "__init__"
            ):
                if dryrun or clean_file(file_root, file_):
                    counts[os.path.splitext(os.path.split(file_)[1])[1]] += 1
            else:
                other_files.append(file_)

    print("From {}:".format(file_root))

    for file_type in [".py", ".pyc", ".csv", ".h5", ".json", ".gen"]:
        if len(
            [
                1
                for n in file_list
                if os.path.splitext(os.path.split(n)[1])[1] == file_type
            ]
        ):
            print(
                "Deleted {0} of {1} {2} files".format(
                    counts[file_type],
                    len(
                        [
                            1
                            for n in file_list
                            if os.path.splitext(os.path.split(n)[1])[1] == file_type
                        ]
                    ),
                    file_type,
                )
            )
    if len(other_files):
        print("    Skipped {0} files or folders".format(len(other_files)))

    return 0


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dryrun",
            default=False,
            help="Don't actually delete files.",
        )

    def handle(self, *args, **options):
        help = """Clears the file system of all orphaned transforms, eventfiles, featurefiles, knowledgepacks, and sandbox caches.

        Removes any files with the relevant extensions ('.py', '.pyc', '.csv', '.h5', '.json', and '.gen') in the root
        folders defined in the django settings file that DO NOT have a corresponding entry in the database. Also looks
        for the existence of code generation folders without an associated knowledgepack entry and deletes them.
        """

        # Transforms
        transforms_in_db = [
            os.path.splitext(os.path.split(t.path)[1])[0]
            for t in Transform.objects.all()
        ]
        compare_and_clean_files(
            transforms_in_db, settings.KBLIB_ROOT, options["dryrun"]
        )

        # EventFiles and FeatureFiles
        eventfiles_in_db = [
            os.path.splitext(os.path.split(e.path)[1])[0]
            for e in EventFile.objects.all()
        ]
        featurefiles_in_db = [
            os.path.splitext(os.path.split(f.path)[1])[0]
            for f in FeatureFile.objects.all()
        ]
        compare_and_clean_files(
            eventfiles_in_db + featurefiles_in_db,
            settings.SERVER_DATA_ROOT,
            options["dryrun"],
        )

        # KnowledgePacks
        knowledgepacks_in_db = [
            os.path.splitext(os.path.split(k.neuron_array)[1])[0]
            for k in KnowledgePack.objects.all()
        ]

        # NEEDS TESTING!! DON'T UNCOMMENT THIS UNLESS YOU ARE SURE IT WORKS
        """
        if 'SERVER_CODEGEN_ROOT' in dir(settings):
            code_gens_in_db = [k.uuid for k in KnowledgePack.objects.all()]
            directory_list = os.listdir(settings.SERVER_CODEGEN_ROOT)
            counts = 0
            for directory in [d for d in directory_list if d not in code_gens_in_db]:
                counts += 1
                if not dryrun:
                    shutil.rmtree('{0}/{1}'.format(settings.SERVER_CODEGEN_ROOT, directory), ignore_errors=True)

            print 'From {0}:'.format(settings.SERVER_CODEGEN_ROOT)
            print '    Deleted {0} of {1} code gen directories'.format(counts,
                                                            len(directory_list))
        """

        # Sandbox caches
        caches_in_db = [s.cache for s in Sandbox.objects.all() if s.cache]
        files_in_caches_in_db = []
        for cache in caches_in_db:
            files_in_caches_in_db += [
                os.path.splitext(value)[0]
                for key, value in cache["data"].items()
                if isinstance(value, str)
            ]
        compare_and_clean_files(
            files_in_caches_in_db, settings.SERVER_CACHE_ROOT, options["dryrun"]
        )
