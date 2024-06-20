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

export const DEBUG = 10;
export const INFO = 20;
export const SUCCESS = 30;
export const WARNING = 40;
export const ERROR = 50;

export const STATUSES = {
  DEBUG,
  INFO,
  SUCCESS,
  WARNING,
  ERROR,
};

export const RUNNING = "RUNNING";
export const KILLING = "KILLING";
export const KILLING_ABORTED = "KILLING_ABORTED";
export const KILLED = "KILLED";
export const COMPLETED = "COMPLETED";
export const FAILED = "FAILED";
export const NOT_STARTED = "NOT_STARTED";

export const RUNNING_STATUSES = {
  RUNNING,
  KILLING,
  KILLING_ABORTED,
  KILLED,
  FAILED,
  COMPLETED,
  NOT_STARTED,
};
