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

import React, { useState } from "react";
import _ from "lodash";
import { Box, Typography } from "@mui/material";
import StandardTable from "components/StandardTable";
import FeatureStatsChart from "components/FeatureStatsChart";

import { ColumnType } from "components/StandardTable/StandardTableConstants";

const FeatureSummary = ({
  isFetching,
  showTitle,
  classMap = {},
  featureSummary = [],
  featureStatistics = [],
}) => {
  const [pageData, setPageData] = useState([]);

  const drawLabel = (column) => (
    <Typography variant="button">{column.title.toUpperCase()}</Typography>
  );
  const columns = [
    {
      title: "Feature",
      field: "Feature",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
    },
    {
      title: "Category",
      field: "Category",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
    },
    {
      title: "Generator",
      field: "Generator",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
    },
    {
      title: "Sensors",
      field: "Sensors",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
    },
  ];

  const title = "Feature Summary";
  const options = {
    rowsPerPage: 8,
    showPagination: true,
    noContentText: "No Feature Summary",
    excludePrimaryFromDetails: true,
    applyFilters: true,
    isDarkHeader: true,
    capturePageData: (_pageData) => setPageData(_pageData),
  };
  return (
    <>
      <StandardTable
        tableId="featureSummaryTable"
        tableColumns={columns}
        tableData={{ data: featureSummary, isFetching }}
        tableTitle={showTitle ? title : null}
        tableOptions={options}
      />
      {!_.isEmpty(featureStatistics) ? (
        <Box mt={2}>
          <FeatureStatsChart
            key="featureStatsCharts"
            featureStatistics={featureStatistics}
            classMap={classMap || {}}
            usedFeatureNames={pageData.map((row) => row.Feature)}
          />
        </Box>
      ) : null}
    </>
  );
};

export default FeatureSummary;
