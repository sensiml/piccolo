/*
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
*/

import { STATUSES, RUNNING_STATUSES } from "consts";

// runnig
export const RUNNING = "RUNNING";
export const KILLING = "KILLING";
export const KILLING_ABORTED = "KILLING_ABORTED";
export const KILLED = "KILLED";
export const COMPLETED = "COMPLETED";
export const FAILED = "FAILED";

export const RUNNING_STATUS = { ...RUNNING_STATUSES };

// mesage

export const MESSAGE_STATUS = { ...STATUSES };

// api
export const API_RUNNING_STATUS = ["PENDING", "STARTED", "SENT"];
export const API_ERROR_STATUS = ["FAILURE"];
export const API_TERMINATTED_STATUS = ["REVOKED"];
