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

import { selectCapture } from "store/captures/selectors";
import _ from "lodash";

const getCaptureConfigurationFormData = (state, captureUUID) => {
  const savedCapture = selectCapture(captureUUID)(state);
  const captureConfigurations = state.captureConfigurations?.data;

  const res = [
    {
      name: "capture_configuration_uuid",
      label: "Sensor Configuration",
      formType: "select",
      defaultValue: savedCapture?.capture_configuration_uuid || "",
      options: _.map(captureConfigurations, (el) => ({
        name: el.name,
        value: el.uuid,
      })),
    },
  ];
  return res;
};

export default getCaptureConfigurationFormData;
