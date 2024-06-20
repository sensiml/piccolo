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

/**
  ("#58D963"), "Green"),
  ("#F49534"), "Orange"),
  ("#7754AB"), "Purple"),
  ("#D14D49"), "Red"),
  ("#C8CF4E"), "Yellow"),
  ("#70A0B5"), "Sky Blue"),
  ("#13631a"), "Forest Green"),
  ("#319476"), "Teal"),
  ("#B570AC"), "Pink"),
  ("#707070"), "Gray"),
  ("#421609"), "Brown"),
  ("#132AD4"), "Dark Blue"),
  ("#C7AD1C"), "Dark Yellow"),
  ("#D47400"), "Dark Orange"),
  ("#330C4A"), "Dark Purple"),
  ("#00A2FF"), "Light Blue"),
 */
import _ from "lodash";

export const DEFAULT_COLORS = [
  "#1D7DC4", // blue
  "#58D963", // green
  "#F49534", // orange
  "#7754AB", // purple
  "#D14D49", // red
  "#C8CF4E", // yellow
  "#70A0B5", // sky blue
  "#13631a", // forest green
  "#319476", // teal
  "#B570AC", // pink
  "#707070", // gray
  "#421609", // brown
  "#132AD4", // dark blue
  "#C7AD1C", // dark yellow
  "#D47400", // dark orange
  "#330C4A", // dark purple
  "#00A2FF", // light blue
];

export const DEFALULT_LABEL = { name: "Label", value: "Unknown", color: "#001f32" };

export const getColorByIndex = (index) => {
  let color = DEFAULT_COLORS[index];
  if (!color) {
    color = `#${_.toUpper(Math.floor(Math.random() * 16777215).toString(16))}`; // random
  }
  return color;
};
