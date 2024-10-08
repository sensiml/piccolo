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

import { DISABLED_CLASSIFIERS } from "consts";

export const selectTransformsByTypeSubType =
  (type, subtype, transformList, excludeTransform) => (state) => {
    let filteredByDirect = [];
    let filteredByType = [];
    const knowedTypes = {
      // tmp
      // "Validation": "Validation Method",
      // "Optimizer": "Training Algorithm",
    };
    const getType = (parentType) => {
      if (knowedTypes[parentType]) {
        return knowedTypes[parentType];
      }
      return parentType;
    };

    if (state?.transforms?.data?.length) {
      const activeTransforms = [...state?.transforms?.data];
      if (transformList?.length) {
        filteredByDirect = activeTransforms.filter((trsf) => transformList.includes(trsf.name));
      }
      if (!subtype?.length) {
        filteredByType = activeTransforms.filter((trsf) => trsf.type === getType(type?.trim()));
      } else {
        filteredByType = activeTransforms.filter(
          (trsf) => trsf.type === type?.trim() && subtype.includes(trsf.subtype?.trim()),
        );
      }
      if (excludeTransform?.length) {
        filteredByDirect = filteredByDirect.filter((trsf) => !excludeTransform.includes(trsf.name));
        filteredByType = filteredByType.filter((trsf) => !excludeTransform.includes(trsf.name));
      }
    }
    const res = [...filteredByType, ...filteredByDirect];
    return res.filter((el) => !DISABLED_CLASSIFIERS.includes(el.name));
  };

export const getTransformByName = (name) => (state) => {
  if (state?.transforms?.data?.length) {
    const activeTransforms = [...state?.transforms?.data];
    return activeTransforms.find((trsf) => trsf.name === name);
  }
  return {};
};
