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
import _ from "lodash";

import { useTranslation } from "react-i18next";
import { Box } from "@mui/material";

import StandardTable from "components/StandardTable";
import LabelColoredName from "components/LabelColoredName";
import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { FORM_TYPES } from "consts";

const TableSegments = ({
  featureData,
  labelColumn,
  labelValues,
  colorHashMap,
  selectedSegmentIndex,
  selectionField,
  isFetching = false,
  onSelectSegmemts,
  onSelectSegmemtIndex,
}) => {
  const { t } = useTranslation("components");

  const handlseSelectInTable = (selectedIDs) => {
    if (onSelectSegmemts) {
      onSelectSegmemts(selectedIDs);
    }
  };

  const handleSelectRow = (row) => {
    onSelectSegmemtIndex(row.id - 1);
  };

  const segments = useMemo(() => {
    if (!_.isEmpty(featureData?.segment_uuid) && labelColumn) {
      return featureData.segment_uuid.map((uuid, index) => {
        const labelName = featureData[labelColumn] ? featureData[labelColumn][index] : "";
        return {
          uuid,
          id: index + 1,
          name: labelName,
          color: colorHashMap[labelName],
        };
      });
    }
    return [];
  }, [featureData, labelColumn]);

  const data = useMemo(() => {
    return { data: segments.map((el) => el), isFetching };
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
      formType: !_.isEmpty(labelValues) ? FORM_TYPES.FORM_SELECT_TYPE : FORM_TYPES.FORM_STRING_TYPE,
      lookup: !_.isEmpty(labelValues)
        ? labelValues.reduce((acc, val) => {
            acc[val] = val;
            return acc;
          }, {})
        : [],
      render: renderLabel,
    },

    {
      title: "UUID",
      field: "uuid",
      sortable: true,
      type: ColumnType.Text,
      filterable: false,
    },
  ];

  const options = {
    rowsPerPage: 10,
    rowsPerPageOptions: [10, 25, 50, 100, "All"],
    excludePrimaryFromDetails: true,
    showPagination: true,
    applyFilters: true,
    isDarkHeader: true,
    selectionField,
    selectionFieldIsSortable: false,
    onSelectInTable: handlseSelectInTable,
    isDisabledSelectAll: true,
    isShowSelection: true,
    selectedRowId: selectedSegmentIndex + 1,
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
