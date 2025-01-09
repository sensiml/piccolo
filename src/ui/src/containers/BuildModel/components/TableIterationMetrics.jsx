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

import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { Tooltip, Box, Typography } from "@mui/material";

import { ColumnType } from "components/StandardTable/StandardTableConstants";

import StandardTable from "components/StandardTable";

const TableIterationMetrics = ({ iterationMetrics }) => {
  const { t } = useTranslation("models");

  const [metrics, setMetrics] = useState({
    data: iterationMetrics?.data,
    loading: false,
  });

  useEffect(() => {
    setMetrics({ data: iterationMetrics?.data, loading: false });
  }, [iterationMetrics]);

  const drawLabelDataFixed2 = (data) => {
    return !data ? "" : isNaN(data) ? data.toUpperCase() : Number(data).toFixed(2);
  };

  const drawLabelData = (data) => {
    return Number(data);
    // return !data ? "" : isNaN(data) ? data.toUpperCase() : Number(data);
  };

  const handleDoubleClick = () => {};

  const dataWithTooltip = (data) => {
    if (!data) {
      return "";
    }
    if (data?.name) {
      const jsonString = JSON.stringify(data.inputs, null, 2);
      return (
        <Tooltip
          title={
            <Typography variant="body2" component="pre">
              {jsonString}
            </Typography>
          }
        >
          <Box>{data.name}</Box>
        </Tooltip>
      );
    }
    return isNaN(data) ? data.toUpperCase() : Number(data).toFixed(0);
  };

  const columns = [
    {
      field: "f1_score",
      title: t("model-builder.table-iterations-f1-score"),
      primary: true,
      sortable: true,
      type: ColumnType.Numeric,
      render: drawLabelDataFixed2,
    },
    {
      field: "classifiers",
      title: t("model-builder.table-iterations-classifier"),
      render: dataWithTooltip,
      type: ColumnType.Text,
    },
    {
      field: "optimizers",
      title: t("model-builder.table-iterations-optimizer"),
      render: dataWithTooltip,
      type: ColumnType.Text,
    },
    {
      field: "features",
      title: t("model-builder.table-iterations-features"),
      sortable: true,
      render: drawLabelData,
      type: ColumnType.Numeric,
    },
    {
      field: "sram",
      title: t("model-builder.table-iterations-sram"),
      sortable: true,
      render: drawLabelData,
      type: ColumnType.Numeric,
    },
    {
      field: "accuracy",
      title: t("model-builder.table-iterations-accuracy"),
      sortable: true,
      render: drawLabelDataFixed2,
      type: ColumnType.Numeric,
    },
    {
      field: "sensitivity",
      title: t("model-builder.table-iterations-sensitivity"),
      sortable: true,
      render: drawLabelDataFixed2,
      type: ColumnType.Numeric,
    },
    {
      field: "original_iteration",
      title: t("model-builder.table-iterations-iteration"),
      sortable: true,
      render: drawLabelData,
      type: ColumnType.Numeric,
    },
  ];

  const options = {
    rowsPerPage: 25,
    showPagination: true,
    rowsPerPageOptions: [10, 25, 50, 100, "All"],
    noContentText: "No Data",
    applyFilters: true,
    tableProps: { size: "medium" },
    onRowDoubleClick: handleDoubleClick,
  };

  return (
    <StandardTable
      tableId="autoSenseIterationsTable"
      tableColumns={columns}
      tableData={metrics}
      tableOptions={options}
    />
  );
};

export default TableIterationMetrics;
