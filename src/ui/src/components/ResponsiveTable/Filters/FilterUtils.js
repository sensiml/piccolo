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

import * as React from "react";
import FilterListIcon from "@mui/icons-material/FilterList";
import { ColumnType, CompareOperators } from "./FilterConstants";
import { TbNotContainsIcon } from "./FilterIcons/TbNotContainsIcon";
import { TbContainsIcon } from "./FilterIcons/TbContainsIcon";
import { TbEqualsIcon } from "./FilterIcons/TbEqualsIcon";
import { TbGreaterThanIcon } from "./FilterIcons/TbGreaterThanIcon";
import { TbNotEqualsIcon } from "./FilterIcons/TbNotEqualsIcon";
import { TbGreaterOrEqualsToIcon } from "./FilterIcons/TbGreaterOrEqualsToIcon";
import { TbLessThanIcon } from "./FilterIcons/TbLessThanIcon";
import { TbLessOrEqualsToIcon } from "./FilterIcons/TbLessOrEqualsToIcon";

export const handleFilterChange = (column) => (event) => {
  // TODO no-param-reassign
  // eslint-disable-next-line no-param-reassign
  column.filterText = event.target.value;
};

export const onKeyDown = () => (event) => {
  if (event.keyCode === 13) {
    event.preventDefault();
    event.stopPropagation();
  }
};

export const getOperators = (column) => {
  if (
    column.type === ColumnType.Numeric ||
    column.type === ColumnType.Date ||
    column.type === ColumnType.DateTime
  ) {
    return [
      CompareOperators.Equals,
      CompareOperators.NotEquals,
      CompareOperators.Gt,
      CompareOperators.Gte,
      CompareOperators.Lt,
      CompareOperators.Lte,
    ];
  }
  return [
    CompareOperators.Contains,
    CompareOperators.NotContains,
    CompareOperators.Equals,
    CompareOperators.NotEquals,
  ];
};

export const getOperatorText = (value) => {
  switch (value) {
    case CompareOperators.NotContains:
    case CompareOperators.Contains:
    case CompareOperators.Equals:
    case CompareOperators.NotEquals:
      return value;
    case CompareOperators.Gt:
      return "Greater than";
    case CompareOperators.Gte:
      return "Greater than or equals to";
    case CompareOperators.Lt:
      return "Less than";
    case CompareOperators.Lte:
      return "Less than or equals to";
    default:
      return "None";
  }
};

export const getOperatorIcon = (operator) => {
  switch (operator) {
    case CompareOperators.NotContains:
      return <TbNotContainsIcon />;
    case CompareOperators.Contains:
      return <TbContainsIcon />;
    case CompareOperators.Equals:
      return <TbEqualsIcon />;
    case CompareOperators.NotEquals:
      return <TbNotEqualsIcon />;
    case CompareOperators.Gt:
      return <TbGreaterThanIcon />;
    case CompareOperators.Gte:
      return <TbGreaterOrEqualsToIcon />;
    case CompareOperators.Lt:
      return <TbLessThanIcon />;
    case CompareOperators.Lte:
      return <TbLessOrEqualsToIcon />;
    default:
      return <FilterListIcon />;
  }
};

const numericComparer = (value1, value2, operator) => {
  if (value1 === undefined || value2 === undefined) return false;

  let val1 = value1;
  let val2 = value2;

  if (value1 && Number.isInteger(value1)) {
    val1 = value1;
    val2 = parseInt(value2, 10);
  } else {
    val1 = parseFloat(value1);
    val2 = parseFloat(value2);
  }

  switch (operator) {
    case CompareOperators.NotEquals:
      return val1 !== val2;
    case CompareOperators.Gt:
      return val1 > val2;
    case CompareOperators.Gte:
      return val1 >= val2;
    case CompareOperators.Lt:
      return val1 < val2;
    case CompareOperators.Lte:
      return val1 <= val2;
    default:
      return val1 === val2;
  }
};

const dateComparer = (value1, value2, operator, compareTime) => {
  const dt1 = value1 instanceof Date ? value1 : new Date(value1);
  const dt2 = value2 instanceof Date ? value2 : new Date(value2);

  if (!dt1 || !dt2) return false;

  if (!compareTime) {
    dt1.setHours(0, 0, 0, 0);
    dt2.setHours(0, 0, 0, 0);
  }

  switch (operator) {
    case CompareOperators.NotEquals:
      return dt1.getTime() !== dt2.getTime();
    case CompareOperators.Gt:
      return dt1 > dt2;
    case CompareOperators.Gte:
      return dt1.getTime() >= dt2.getTime();
    case CompareOperators.Lt:
      return dt1 < dt2;
    case CompareOperators.Lte:
      return dt1.getTime() <= dt2.getTime();
    default:
      return dt1.getTime() === dt2.getTime();
  }
};

const dateComparerTime = (value1, value2, operator) => {
  return dateComparer(value1, value2, operator, true);
};

const textComparer = (value1, value2, operator) => {
  if (!value1 || !value2) return false;

  if (Number.isInteger(value1)) return numericComparer(value1, value2);

  const val1 = value1.toLowerCase();
  const val2 = value2.toLowerCase();

  switch (operator) {
    case CompareOperators.NotContains:
      return val1.search(val2) === -1;
    case CompareOperators.Equals:
      return val1 === val2;
    case CompareOperators.NotEquals:
      return val1 !== val2;
    default:
      return val1.search(val2) !== -1;
  }
};

const applyFilter = (actual, filter, dataTypeFilter) => {
  if (filter.value === undefined) return true;
  const filterVals = Array.isArray(filter.value) ? filter.value : [filter.value];
  return (
    filterVals.length === 0 ||
    filterVals.some((filtVal) => dataTypeFilter(actual, filtVal, filter.col.filterOperator))
  );
};

export const filterComparer = (actual, filter) => {
  if (!filter || !filter.col || !filter.col.type) return true;
  // TODO no-param-reassign
  // eslint-disable-next-line no-param-reassign
  if (filter.value !== undefined) filter.col.filterRequested = false;
  switch (filter.col.type) {
    case ColumnType.Numeric:
      return applyFilter(actual, filter, numericComparer);
    case ColumnType.Date:
      return applyFilter(actual, filter, dateComparer);
    case ColumnType.DateTime:
      return applyFilter(actual, filter, dateComparerTime);
    default:
      return applyFilter(actual, filter, textComparer);
  }
};
