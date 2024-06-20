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

export const PLATROFM_TYPES = ["compiler", "devkit"];

export const STEP_SELECT_PLATFORM = 1;
export const STEP_SUBMIT_DOWNLOAD = 2;
export const STEP_SELECTED_PLATFORM = 3;

export const ARMGCC_UUID = "e9f53dfa-f434-4f24-9577-839c190f74da";

export const FORMATS = [
  { name: "Binary", value: "bin", isBinary: true },
  { name: "Library", value: "lib", isBinary: false },
  { name: "Source", value: "source", isBinary: false },
];

export const DRIVERS_DEFAULT_KEY = "Default";
export const SOURCE_DEFAULT_LIST = [{ value: "Custom", name: "Custom", isNotAllowForBinary: true }];
