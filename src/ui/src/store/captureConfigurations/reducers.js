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

import { STORE_CAPTURE_CONFIGURATIONS, LOADING_CAPTURE_CONFIGURATIONS } from "./actionTypes";

const initialCaptureConfigurationsState = { data: [], isFetching: false };
export const captureConfigurations = (state = initialCaptureConfigurationsState, action) => {
  switch (action.type) {
    case LOADING_CAPTURE_CONFIGURATIONS:
      return { data: [], isFetching: true };
    case STORE_CAPTURE_CONFIGURATIONS:
      return { data: action.captureConfigurations, isFetching: false };
    default:
      return state;
  }
};

export default captureConfigurations;
