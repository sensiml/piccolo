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

import api from "store/api";
import logger from "store/logger";
import helper from "store/helper";
import { setShowBannersAfterLogin } from "store/common/actions";
import { LOAD_TEAM_INFO } from "./actionTypes";

export const loadTeamSubscription = () => async (dispatch) => {
  try {
    const { data: teamInfo } = await api.get("/team-subscription/");
    dispatch({ type: LOAD_TEAM_INFO, teamInfo });
    dispatch(setShowBannersAfterLogin(teamInfo));
  } catch (err) {
    logger.logError("", helper.getResponseErrorDetails(err), err, "loadTeamSubscription");
  }
};

export default loadTeamSubscription;
