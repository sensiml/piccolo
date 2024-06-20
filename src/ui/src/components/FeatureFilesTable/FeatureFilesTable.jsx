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
import StandardTable from "components/StandardTable";
import { Typography } from "@mui/material";
import { ColumnType } from "components/StandardTable/StandardTableConstants";

const FeatureFilesTable = ({ featurefiles, onRowSelectionAction }) => {
  const [featureFileList, setFeatureFileList] = useState(featurefiles);

  const drawLabel = (column) => (
    <Typography variant="button" noWrap>
      {column.title.toUpperCase()}
    </Typography>
  );

  const columns = [
    {
      title: "Name",
      field: "name",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
    },
    {
      title: "Created",
      field: "created_at",
      sortable: true,
      type: ColumnType.Date,
      filterable: true,
      renderLabel: drawLabel,
    },
    {
      title: "UUID",
      field: "uuid",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      renderLabel: drawLabel,
    },
  ];

  useEffect(() => {
    setFeatureFileList(featurefiles);
  }, [featurefiles]);

  const title = "Feature Files";
  const options = {
    rowsPerPage: 5,
    showPagination: true,
    noContentText: "No Feature Files",
    excludePrimaryFromDetails: true,
    onRowSelection: onRowSelectionAction || null,
    applyFilters: true,
  };
  return (
    <StandardTable
      tableId="featureFileTable"
      tableColumns={columns}
      tableData={featureFileList}
      tableTitle={title}
      tableOptions={options}
    />
  );
};

export default FeatureFilesTable;
