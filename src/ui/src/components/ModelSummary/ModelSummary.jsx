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

/* eslint-disable no-restricted-syntax */
import React, { useState, useEffect } from "react";
import { Box, Typography } from "@mui/material";
import StandardTable from "components/StandardTable";
import { ColumnType } from "components/StandardTable/StandardTableConstants";
import NeuralNetworkSummary from "./NeuralNetworkSummary";
import PMEModelSummary from "./PMEModelSummary";

const ModelSummary = ({ model, showTitle }) => {
  const drawLabel = (column) => {
    return <Typography variant="button">{column.title.toUpperCase()}</Typography>;
  };

  const defaultColumn = {
    title: "classifier",
    field: "classifier",
    primary: true,
    sortable: true,
    type: ColumnType.Text,
    filterable: true,
    renderLabel: drawLabel,
  };

  const [modelSummary, setModelSummary] = useState({
    data: null,
    isFetching: model.isFetching,
  });

  const [modelParameters, setModelParameters] = useState({
    data: null,
    isFetching: model.isFetching,
  });

  const [modelSummaryColumns, setModelSummaryColumns] = useState(null);

  const loadData = (m) => {
    const data = {};
    const columns = [];
    if (Object.entries(m).length !== 0 && m.constructor === Object) {
      data.classifier = m.device_configuration?.classifier;
      data.uuid = m.uuid;
      const pipelineSummaryCount = m.pipeline_summary?.length || 0;

      if (m.device_configuration?.classifier === "PME") {
        data.optimizer = m.pipeline_summary[pipelineSummaryCount - 1].optimizers[0].name;
        data.neurons = m.neuron_array.length;
        data.classification_mode = m?.device_configuration?.classification_mode ? "KNN" : "RBF";
        data.distance_mode = m?.device_configuration.distance_mode ? "LSUP" : "L1";
      } else if (m.device_configuration?.classifier === "Decision Tree Ensemble") {
        data.n_estimators =
          m.pipeline_summary[pipelineSummaryCount - 1].optimizers[0].inputs.n_estimators;
        data.max_depth =
          m.pipeline_summary[pipelineSummaryCount - 1].optimizers[0].inputs.max_depth;
      } else if (m.device_configuration?.classifier === "Boosted Tree Ensemble") {
        //
      } else if (m.device_configuration?.classifier === "TensorFlow Lite for Microcontrollers") {
        //
      }
    }
    columns.splice(0, columns.length);
    if (Object.entries(data).length !== 0 && data.constructor === Object) {
      columns.push(defaultColumn);
      for (const x in data) {
        if (x !== "classifier") {
          columns.push({
            title: x,
            field: x,
            sortable: true,
            type: ColumnType.Text,
            filterable: true,
            renderLabel: drawLabel,
          });
        }
      }
    }
    setModelSummary({
      data: [data],
      isFetching: false,
    });
    setModelParameters({
      data: m,
      isFetching: false,
    });
    setModelSummaryColumns(columns);
  };

  useEffect(() => {
    if (model && model.data) {
      loadData(model.data || {});
    }
  }, [model]);

  const title = "Model Summary";
  const options = {
    rowsPerPage: 20,
    showPagination: true,
    applyFilters: true,
    noContentText: "No Model Summary",
    excludePrimaryFromDetails: true,
    isDarkHeader: true,
  };

  return (
    <Box>
      <StandardTable
        tableId="modelSummaryTable"
        tableColumns={modelSummaryColumns}
        tableData={modelSummary}
        tableTitle={showTitle ? title : null}
        tableOptions={options}
      />
      {model?.data?.device_configuration?.classifier === "PME" && modelParameters ? (
        <PMEModelSummary model={modelParameters} />
      ) : null}
      {model?.data?.device_configuration?.classifier === "TensorFlow Lite for Microcontrollers" ? (
        <NeuralNetworkSummary model={model} />
      ) : null}
    </Box>
  );
};

export default ModelSummary;
