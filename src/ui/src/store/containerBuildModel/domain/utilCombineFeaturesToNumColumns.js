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
import { getCombinations, getUniqueId } from "utils";

const combineFeaturesToNumColumns = (features) => {
  return _.reduce(
    features,
    (acc, feature) => {
      if (feature.numColumns > 0 && !_.isEmpty(feature?.params?.columns)) {
        // if feature has numColumns spit to smallest with combintation of columns
        const splittedColumns = getCombinations(feature?.params?.columns, feature.numColumns);
        const updatedParams = { ...feature?.params }; // copy

        splittedColumns.forEach((columns) => {
          acc.push({ ...feature, params: { ...updatedParams, columns }, localId: getUniqueId() });
        });
      } else {
        // if not use
        acc.push({ ...feature, localId: getUniqueId() });
      }
      return acc;
    },
    [],
  );
};

export default combineFeaturesToNumColumns;
