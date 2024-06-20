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
import { RESPONSIVE } from "consts";

export const filterTruncate = (str, len) => {
  return _.truncate(str, { length: len });
};

export const filterTruncateResponsive = (str, windowSize) => {
  // eslint-disable-next-line no-console
  if (windowSize < RESPONSIVE.WIDTH_FOR_PHONE_TEXT) {
    return _.truncate(str, { length: RESPONSIVE.TRUNCATE_NAME_OVER_PHONE_TEXT });
  }

  if (windowSize < RESPONSIVE.WIDTH_FOR_TABLET_TEXT) {
    return _.truncate(str, { length: RESPONSIVE.TRUNCATE_NAME_OVER_TABLET_TEXT });
  }

  if (windowSize < RESPONSIVE.WIDTH_FOR_SHORT_TEXT) {
    return _.truncate(str, { length: RESPONSIVE.TRUNCATE_NAME_OVER_SHORT_TEXT });
  }

  return _.truncate(str, { length: RESPONSIVE.TRUNCATE_NAME_OVER });
};

export const filterTruncateMiddle = (fullStr, strLen = 0, separator = "...") => {
  if (!fullStr) {
    return "";
  }
  if (fullStr.length <= strLen || strLen === 0) {
    return fullStr;
  }

  const sepLen = separator.length;
  const charsToShow = strLen - sepLen;
  const frontChars = Math.ceil(charsToShow / 2);
  const backChars = Math.floor(charsToShow / 2);

  return fullStr.substr(0, frontChars) + separator + fullStr.substr(fullStr.length - backChars);
};

export const filterToSnakeCase = (str) => {
  return _.snakeCase(str);
};

export const filterFormatDate = (dateString) => {
  if (!dateString) {
    return "";
  }
  return new Date(dateString).toLocaleString("en-US", {
    month: "numeric",
    year: "numeric",
    day: "numeric",
    hour: "numeric",
    minute: "numeric",
    hour12: true,
  });
};

export const filterFormatSecondsToDuration = (value) => {
  const hours = Math.floor(value / 360);
  const minutes = Math.floor(value / 60);
  const seconds = (value % 60).toFixed(2);
  return `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}:${seconds
    .toString()
    .padStart(2, "0")}`;
};

export default {
  filterTruncate,
  filterToSnakeCase,
  filterFormatDate,
  filterTruncateResponsive,
  filterFormatSecondsToDuration,
};
