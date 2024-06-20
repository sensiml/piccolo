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
from uuid import UUID

from datamanager.exceptions import KnowledgePackCombinationException


def validate_kb_description(kb_description_str, knowledgepack_id):
    kb_description = None

    if isinstance(kb_description_str, str):
        kb_description = json.loads(kb_description_str)

    if kb_description is None:
        kb_description = {
            "0": {
                "uuid": knowledgepack_id,
                "parent": None,
                "segmenter_from": None,
                "results": None,
            }
        }

    for name in kb_description:
        kp_uuid = kb_description[name].get("uuid", None)
        kp_parent = kb_description[name].get("parent", None)
        kp_segmenter_from = kb_description[name].get("segmenter_from", None)
        kp_result = kb_description[name].get("results", None)
        kp_json = {}
        kp_json["uuid"] = str(kp_uuid) if kp_uuid else None
        kp_json["parent"] = str(kp_parent) if kp_parent else None
        kp_json["segmenter_from"] = (
            str(kp_segmenter_from) if kp_segmenter_from else None
        )
        kp_json["results"] = kp_result if kp_result else None
        kp_json["source"] = str(kb_description[name].get("source", "custom")).lower()

        if kp_json["uuid"] is None:
            raise KnowledgePackCombinationException(
                "\nError:  Knowledge Pack UUID cannot be empty."
            )

        try:
            UUID(kp_json["uuid"], version=4)
        except:
            raise KnowledgePackCombinationException(
                "\nError: Invalid knowledge pack UUID {}".format(kp_json["uuid"])
            )

        # if it has a parent, set its source to the same
        if kp_json["parent"]:
            kp_json["source"] = str(
                kb_description[kp_json["parent"]].get("source", "custom")
            ).lower()

        # if it is a parent check the source is valid
        elif kp_json["source"].lower() not in ["motion", "audio", "custom"]:
            try:
                UUID(kp_json["source"], version=4)
            except:
                raise KnowledgePackCombinationException(
                    "\nError: Invalid Capture Configuration UUID {}".format(
                        kp_json["source"]
                    )
                )

        if name:
            if len(name) > 120:
                raise KnowledgePackCombinationException(
                    "\nError: Names must be less than 120 characters"
                )
            if not all(x.isalpha() or x == "_" or x.isdigit() for x in name):
                raise KnowledgePackCombinationException(
                    "\nError: Model names can only consist of letters and underscores"
                )

        if kp_json["parent"] and kp_json["parent"] not in kb_description.keys():
            raise KnowledgePackCombinationException(
                "\nError: Parent must be either None or a named model."
            )

        if kp_json["parent"] == name:
            raise KnowledgePackCombinationException(
                "\nError: A model cannot have itself as a parent."
            )

        if kp_json["segmenter_from"] == "parent" and kp_json["parent"] is None:
            raise KnowledgePackCombinationException(
                "\nError: A parent model must use its own segmenter."
            )

        kb_description.update({name: kp_json})

    return kb_description
