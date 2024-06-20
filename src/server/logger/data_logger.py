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
import logging

from library.models import ProcessorDescription, CompilerDescription

logger = logging.getLogger(__name__)


def usage_log(
    operation,
    team,
    team_member,
    detail=None,
    PJID=None,
    PID=None,
    CID=None,
    KPID=None,
    PROC=None,
    extra=None,
    runtime=None,
):

    log = {}
    log["log_type"] = "usage"
    log["operation"] = operation
    log["team"] = team.name
    log["team_uuid"] = str(team.uuid)
    log["team_member_uuid"] = str(team_member.uuid)
    log["runtime"] = runtime

    log["detail"] = detail

    if detail:
        target_compiler = detail.get("target_compiler", "")
        target_processor = detail.get("target_processor", "")

        if isinstance(target_processor, ProcessorDescription) and isinstance(
            target_compiler, CompilerDescription
        ):
            detail["target_compiler"] = target_compiler.to_target_compiler()
            detail["target_processor"] = target_processor.to_target_processor()

    if PJID:
        log["project"] = PJID.name
        log["PJID"] = str(PJID.uuid)
    if PID:
        log["pipeline"] = PID.name
        log["PID"] = str(PID.uuid)
    if CID:
        log["capture"] = CID.name
        log["CID"] = str(CID.uuid)
    if PROC:
        log["PROC"] = PROC
    if extra:
        log["extra"] = extra

    logger.info(json.dumps(log))


def report_log(data):
    data["log_type"] = "customer_report"

    logger.info(json.dumps(data))
