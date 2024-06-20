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

import _ from "lodash";
import api from "../api";
import helper from "../helper";
import logger from "../logger";

import { STORE_PLATFORMS, LOADING_PLATFORMS } from "./actionTypes";

const ARMGCC_UUID = "e9f53dfa-f434-4f24-9577-839c190f74da";

export const loadPlatforms = () => async (dispatch) => {
  dispatch({ type: LOADING_PLATFORMS });
  let platforms = [];
  try {
    const { data: responseBody } = await api.get("/platforms/v2");
    platforms = _.sortBy(responseBody, [(o) => _.capitalize(o.name)]);

    const armgcc = platforms[_.findIndex(platforms, (n) => n.uuid === ARMGCC_UUID)];

    platforms = _.remove(platforms, (n) => n.uuid !== ARMGCC_UUID);

    platforms = _.concat(armgcc, platforms);
  } catch (err) {
    logger.logError("", helper.getResponseErrorDetails(err), err, "loadPlatforms");
  }
  dispatch({
    type: STORE_PLATFORMS,
    platforms,
  });
};
