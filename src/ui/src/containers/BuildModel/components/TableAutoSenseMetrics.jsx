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

import { generatePath, useHistory, Link } from "react-router-dom";

import { Tooltip } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import ExploreIcon from "@mui/icons-material/Explore";

import { ROUTES } from "routers";

import StandardTable from "components/StandardTable";

const TableAutoSenseMetrics = ({ autosenseMetrics, projectUUID, pipelineUUID }) => {
  const routersHistory = useHistory();
  const { t } = useTranslation("models");

  const [metrics, setMetrics] = useState({
    data: autosenseMetrics,
    loading: true,
  });

  const getModelPagePath = (modelUUID) => {
    const pathParams = {
      ...(projectUUID && { projectUUID }),
      ...(pipelineUUID && { pipelineUUID }),
      ...(modelUUID && { modelUUID }),
    };
    return generatePath(ROUTES.MAIN.MODEL_EXPLORE.path, pathParams);
  };

  useEffect(() => {
    setMetrics({ data: autosenseMetrics, loading: false });
  }, [autosenseMetrics]);

  const drawLabelData = (data) => {
    return !data ? "" : isNaN(data) ? data.toUpperCase() : Number(data).toFixed(0);
  };

  const handleDoubleClick = (event, row) => {
    routersHistory.push(getModelPagePath(row.knowledgepack));
  };

  const openModelRender = (modelUUID) => {
    return (
      <Tooltip title="Explore Model..">
        <Link to={getModelPagePath(modelUUID)}>
          <IconButton variant="contained" color="primary" size="small">
            <ExploreIcon />
          </IconButton>
        </Link>
      </Tooltip>
    );
  };

  const columns = [
    { field: "name", title: t("model-builder.table-autosense-model-name"), primary: true },
    {
      field: "accuracy",
      title: t("model-builder.table-autosense-model-accuracy"),
      render: drawLabelData,
    },
    {
      field: "classifiers_sram",
      title: t("model-builder.table-autosense-model-classifiers_sram"),
      render: drawLabelData,
    },
    {
      field: "features",
      title: t("model-builder.table-autosense-model-features"),
      render: drawLabelData,
    },
    {
      field: "sensitivity",
      title: t("model-builder.table-autosense-model-sensitivity"),
      render: drawLabelData,
    },
    {
      field: "f1_score",
      title: t("model-builder.table-autosense-model-f1_score"),
      render: drawLabelData,
    },
    { field: "knowledgepack", title: "", render: openModelRender },
  ];

  const options = {
    rowsPerPage: 5,
    showPagination: false,
    noContentText: t("model-builder.table-autosense-model-no-data"),
    tableProps: { size: "medium" },
    onRowDoubleClick: handleDoubleClick,
  };

  return (
    <StandardTable
      tableId="autoSenseMetricsTable"
      tableColumns={columns}
      tableData={metrics}
      tableOptions={options}
    />
  );
};

export default TableAutoSenseMetrics;
