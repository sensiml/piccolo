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

import React, { useEffect, useState } from "react";
import _ from "lodash";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import StandardTable from "components/StandardTable";

const PMEModelSummary = ({ model }) => {
  const [modelParameters, setModelParameters] = useState({
    data: null,
    isFetching: model.isFetching,
  });

  useEffect(() => {
    if (!_.isEmpty(model.data?.neuron_array)) {
      const ModelParameterData = model.data?.neuron_array.map((elArr) => {
        return {
          ...elArr,
          category_name: model.data.class_map[elArr.Category],
          Vector: elArr.Vector.toString(),
        };
      });

      setModelParameters({
        data: ModelParameterData,
        isFetching: false,
      });
    }
  }, [model]);

  const options = {
    rowsPerPage: 20,
    showPagination: true,
    applyFilters: true,
    noContentText: "No Model Summary",
    excludePrimaryFromDetails: true,
    isDarkHeader: true,
  };

  const modelparameterColumns = [
    {
      title: "Category",
      field: "category_name",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: "Category ID",
      field: "Category",
      primary: true,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "AIF",
      field: "AIF",
      primary: true,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Pattern",
      field: "Vector",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
  ];

  return (
    <StandardTable
      tableId="modelParamterTable"
      tableColumns={modelparameterColumns}
      tableData={modelParameters}
      tableTitle={true}
      tableOptions={options}
    />
  );
};

export default PMEModelSummary;
