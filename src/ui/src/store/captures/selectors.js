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

import { ROUTES } from "routers";
import { generatePath } from "react-router-dom";
import { sortAlphabeticallyAsc } from "utils";

import { setSelectedLabelUUID } from "store/labels/selectors";
import { selectSelectedSessionUUID } from "store/sessions/selectors";

export const selectCapture = (captureUUID) => (state) => {
  if (!_.isEmpty(state.captures?.capturesStatistics?.data)) {
    return state.captures.capturesStatistics.data.find((el) => el.uuid === captureUUID);
  }
  return "";
};

export const selectCapturesStatistics = (state) => {
  const projectUUID = state.projects?.selectedProject?.uuid;
  const labelUUID = setSelectedLabelUUID(state);
  const sessionUUID = selectSelectedSessionUUID(state);
  if (!_.isEmpty(state.captures?.capturesStatistics?.data)) {
    return {
      data: state.captures.capturesStatistics.data
        .sort((a, b) => sortAlphabeticallyAsc(a.name, b.name))
        .map((el) => ({
          ...el,
          openFileURL: `${generatePath(ROUTES.MAIN.DATA_MANAGER.child.CAPTURE_DETAILS_SCREEN.path, {
            projectUUID,
            captureUUID: el.uuid,
          })}?label=${labelUUID}&session=${sessionUUID}`,
        })),
      isFetching: state.captures?.capturesStatistics?.isFetching || false,
    };
  }
  return { data: [], isFetching: state.captures?.capturesStatistics?.isFetching || false };
};

export const selectCaptureUUIDs = (state) => {
  if (!_.isEmpty(state.captures?.capturesStatistics?.data)) {
    return state.captures.capturesStatistics.data.map(({ uuid }) => uuid);
  }
  return "";
};

export const selectCaptureSensorData = (state) => {
  if (!_.isEmpty(state.captures?.captureSensorData?.data)) {
    return state.captures?.captureSensorData?.data;
  }
  return [[]];
};
