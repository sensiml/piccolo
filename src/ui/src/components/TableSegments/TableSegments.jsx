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

import React, { useMemo } from "react";
import { useTranslation } from "react-i18next";

import StandardTable from "components/StandardTable";
import LabelColoredName from "components/LabelColoredName";
import { Box } from "@mui/material";
import { ColumnType } from "components/StandardTable/StandardTableConstants";

const TableSegments = ({ segments, selectedSegment, onSelectSegmemts, onSelectSegmemt }) => {
  const { t } = useTranslation("components");

  const handlseSelectInTable = (selectedUUIDs) => {
    if (onSelectSegmemts) {
      onSelectSegmemts(selectedUUIDs);
    }
  };

  const handleSelectRow = (row) => {
    onSelectSegmemt(row);
  };

  const data = useMemo(() => {
    return { data: segments.map((el) => el), isFetching: false };
  }, [segments]);

  const renderLabel = (_value, row) => {
    return (
      <Box p={1.75}>
        <LabelColoredName name={row?.name || ""} color={row?.color || ""} />
      </Box>
    );
  };

  const columns = [
    {
      title: t("label-table.header-id"),
      field: "id",
      sortable: true,
      type: ColumnType.Numeric,
    },
    {
      title: t("label-table.header-name"),
      field: "name",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      render: renderLabel,
    },

    {
      title: "UUID",
      field: "uuid",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
  ];

  const options = {
    rowsPerPage: 10,
    rowsPerPageOptions: [10, 25, 50, 100, "All"],
    excludePrimaryFromDetails: true,
    showPagination: true,
    applyFilters: true,
    isDarkHeader: true,
    isDisabledSelectAll: true,
    selectionField: onSelectSegmemts && "id",
    onSelectInTable: handlseSelectInTable,
    isShowSelection: true,
    selectedRowId: selectedSegment,
    onRowSelection: (el, row) => handleSelectRow(row),
    noContentText: t("captures-table.empty-content"),
  };

  return (
    <StandardTable
      tableId="lableTable"
      tableData={data}
      tableColumns={columns}
      tableOptions={options}
    />
  );
};

export default TableSegments;
