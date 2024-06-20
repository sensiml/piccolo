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
import { v4 as uuidv4 } from "uuid";

export const getUniqueId = () => {
  return uuidv4();
};

export const getCombinations = (array, n) => {
  if (array.length < n) {
    return [];
  }

  // eslint-disable-next-line no-shadow
  const combineRecur = (array, n) => {
    // eslint-disable-next-line no-param-reassign
    if (--n < 0) {
      return [[]];
    }
    const combinations = [];
    // eslint-disable-next-line no-param-reassign
    array = array.slice();
    while (array.length - n) {
      const value = array.shift();
      combineRecur(array, n).forEach((combination) => {
        combination.unshift(value);
        combinations.push(combination);
      });
    }
    return combinations;
  };

  return combineRecur(array, n);
};

export const getFileExtention = (filename) => {
  if (filename) {
    return _.split(filename, ".").pop();
  }
  return "";
};

export const getFileName = (filename) => {
  if (filename) {
    return _.split(filename, ".").slice(0, -1).join(".");
  }
  return "";
};

export const getColorFromDCLFormat = (color = "") => {
  if (color && color.slice(1, 3) === "FF") {
    return `#${color.slice(3)}`;
  }
  return color;
};

export const getColorToDCLFormat = (color = "") => {
  return `#FF${color.slice(1)}`;
};

/*
const updatedData = data.reduce((acc, el, index) => {
  if (index === 0) {
    titles.forEach((_name) => acc.push([]));
  }
  titles.forEach((name, nameInx) => {
    acc[nameInx].push({
      label: index,
      value: el[name],
    });
  });
  return acc;
}, []);

*/

export const CSVToJSON = (data, delimiter = ",") => {
  const titles = data
    .slice(0, data.indexOf("\n"))
    .split(delimiter)
    .filter((name) => name !== "sequence");
  return data
    .slice(data.indexOf("\n") + 1)
    .split("\n")
    .reduce((acc, row, indexRow) => {
      if (indexRow === 0) {
        titles.forEach((_name) => acc.push([]));
      }
      const values = row.split(delimiter).slice(1);
      values.forEach((value, index) => {
        acc[index].push({
          sequence: indexRow,
          name: _.trim(titles[index]),
          value: _.toNumber(_.trim(value)),
        });
      });
      return acc;
    }, []);
};

export const sortAlphabeticallyAsc = (a, b) => {
  if (_.toLower(a) < _.toLower(b)) {
    return -1;
  }
  if (_.toLower(a) > _.toLower(b)) {
    return 1;
  }
  return 0;
};
