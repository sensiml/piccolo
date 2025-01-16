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
import { selectedMetadataSampleRate } from "store/metadata/selectors";

export const selectedSampleRate = (uuid) => (state) => {
  /**
   * @returns {Number || undefined} sampleRate
   */
  const catpureCongList = state.captureConfigurations?.data || [];
  let sampleRate = selectedMetadataSampleRate(state);

  if (sampleRate) {
    return sampleRate;
  }

  if (_.isArray(catpureCongList) && catpureCongList.length > 0) {
    let captureConfigObj = {};
    if (uuid) {
      captureConfigObj = catpureCongList.find((el) => el.uuid === uuid)?.configuration || {};
    } else {
      captureConfigObj = catpureCongList[0]?.configuration || {};
    }

    if (!_.isEmpty(captureConfigObj)) {
      // eslint-disable-next-line camelcase
      const { capture_sources } = captureConfigObj;
      if (_.isArray(capture_sources)) {
        _.forEach(capture_sources, (sourceEl) => {
          sampleRate = sourceEl.sample_rate;
        });
      }
    }
  }
  return sampleRate;
};
