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

import makeStyles from "@mui/styles/makeStyles";

const cellColorGreen = "#81c784";
const cellColorOrange = "#ef6c00";
const cellColorDarkRed = "#d50000";

const getCellColor = (percentage) => {
  // below 80% Green
  if (percentage < 80) return cellColorGreen;

  // between 80 to 100% Orange
  if (percentage < 100) return cellColorOrange;

  // 100% Dark Red
  return cellColorDarkRed;
};

const getTextColor = (percentage) => {
  // less than 90% Black
  if (percentage < 80) return "#000000";

  // greater than 90% White
  return "#FFFFFF";
};

const useStyles = (percentage) =>
  makeStyles(() => ({
    capsuleCell: {
      height: 15,
      display: "inline-block",
    },
    firstSection: {
      borderRadius: percentage > 90 ? "5px 5px 5px 5px" : "5px 0px 0px 5px",
      padding: 3,
      display: percentage === 0 ? "none" : "inline-block",
      background: getCellColor(percentage),
      width: `${percentage > 90 ? 91 : percentage}%`,
    },

    secondSection: {
      borderRadius: percentage === 0 ? "5px 5px 5px 5px" : "0px 5px 5px 0px",
      padding: percentage > 90 ? 0 : 2,
      background: "#FFFFF",
      border: "1px solid",
      borderColor: getCellColor(percentage),
      display: percentage > 90 ? "none" : "inline-block",
      width: `${percentage > 90 ? 1 : 100 - percentage - 15}%`,
    },
    floater: {
      top: 2,
      clear: "both",
      position: "absolute",
      left: 10,
      color: getTextColor(percentage),
    },
    container: {
      minWidth: 120,
      display: "inline-block",
    },
    mainContainer: {
      position: "relative",
    },
  }))();

export default useStyles;
