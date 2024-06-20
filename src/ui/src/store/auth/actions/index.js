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

import { push } from "connected-react-router";

import { ROUTES } from "routers";
import { resetAuthHeader } from "store/api";

import { LOG_OUT } from "./actionTypes";

export { logIn, logInOauthCallback } from "./login";
export { default as loadTeamInfo } from "./loadTeamSubscription";

export const resetApp = () => async (dispatch) => {
  resetAuthHeader();
  await dispatch({ type: LOG_OUT });
  push({ pathname: ROUTES.AUTH.child.LOGIN.path });
};

export const logOut = () => async (dispatch) => {
  await dispatch(resetApp());
  push({ pathname: ROUTES.AUTH.child.LOGIN.path });
};
