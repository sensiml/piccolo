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

export const selectedSessionData = (sessionId) => (state) => {
  if (!_.isEmpty(state?.sessions?.data)) {
    return state.sessions.data.find((el) => _.toString(el.id) === _.toString(sessionId)) || {};
  }
  return {};
};

export const selectedSessionName = (sessionId) => (state) => {
  if (_.isArray(state?.sessions?.data) && !_.isEmpty(state?.sessions?.data)) {
    return state.sessions.data.find((el) => el.id === sessionId)?.name || {};
  }
  return "";
};

export const selectSelectedSessionData = (state) => {
  if (state.sessions?.data && state?.sessions?.selectedSessionUUID) {
    return state.sessions.data.find(
      (el) => _.toString(el.id) === _.toString(state?.sessions?.selectedSessionUUID),
    );
  }
  return {};
};

export const selectDefaultSessionData = (state) => {
  if (state?.sessions?.data?.length) {
    return state.sessions.data[0];
  }
  return {};
};

export const selectSelectedSessionUUID = (state) => {
  let selectedSessionUUID = selectSelectedSessionData(state)?.id;
  if (!selectedSessionUUID) {
    selectedSessionUUID = selectDefaultSessionData(state)?.id;
  }
  return _.toString(selectedSessionUUID) || "";
};

export const selectSessoionTableData = (state) => {
  const getAlgorithmName = (parameters) => {
    const parsedParameters = JSON.parse(parameters);
    return parsedParameters?.name || "";
  };
  if (state?.sessions?.data?.length) {
    return state.sessions.data.map((el) => ({
      name: el.name,
      type: el.custom ? "Manual" : "Auto",
      algorithm: getAlgorithmName(el.parameters) || "",
      uuid: _.toString(el.id),
      custom: el.custom,
    }));
  }
  return [];
};
