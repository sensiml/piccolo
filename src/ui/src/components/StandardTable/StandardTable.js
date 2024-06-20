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

/* eslint-disable no-unused-vars */
import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";
import { useSelector } from "react-redux";
import { Box, Checkbox, IconButton, Paper, Grid, Tooltip, Typography } from "@mui/material";
// eslint-disable-next-line import/no-named-as-default
import ResponsiveTable from "components/ResponsiveTable";
import ErrorBoundary from "components/ErrorBoundary";
import helper from "store/helper";

import { ElementLoader } from "components/UILoaders";

import SelectionMenu from "./SelectionMenu";
import useStyles from "./StandardTableStyles";
import { ColumnType } from "./StandardTableConstants";

const StandardTable = ({
  tableId,
  tableColumns,
  tableData,
  tableTitle,
  tableOptions,
  tableXS = 12,
  isResetPageAfterUpdateTableData = false,
}) => {
  const { selectionField, selectionFieldIsSortable } = tableOptions;

  const classes = useStyles(
    _.isUndefined(tableOptions.isDarkHeader) ? true : tableOptions.isDarkHeader,
  );
  const [page, setPage] = useState(tableOptions.page ? tableOptions.page : 0);
  const [rowsPerPage, setRowsPerPage] = useState(
    tableOptions.rowsPerPage ? tableOptions.rowsPerPage : 5,
  );

  const [selectedItems, setSelectedItems] = useState([]);
  const [filteredData, setFilteredData] = useState([]);

  const [selectionMenuAnchor, setSelectionMenuAnchor] = useState(null);
  const [isOpenSelectionMenu, setIsOpenSelectionMenu] = useState(false);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };
  const isNavBarOpen = useSelector((state) => state.common.values.navBarIsOpen);
  const handleChangeRowsPerPage = (event) => {
    setPage(0);
    setRowsPerPage(event.target.value === "All" ? tableData.data.length + 10 : event.target.value);
  };

  const tableProps = {
    size: "small",
    stickyHeader: false,
    "aria-label": "sticky table",
  };

  const defaultFilterRowStyle = {
    minHeight: 10,
  };

  const defaultFilterCellStyle = {};

  const tableContainerProps = {
    className: `${classes.scrolledConrainer} ${
      isNavBarOpen ? classes.container : classes.containerClosed
    }`,
  };
  const contextMenuProps = {
    className: classes.contextMenu,
  };
  const handleRowDoubleClick = () => {};
  const handleRowSelection = () => {};
  const noContentText = "No Content";
  const excludePrimaryFromDetails = false;
  const tableHeadCellOptions = {
    className: tableOptions.headersCentered
      ? `${classes.tableCenteredHeader} ${classes.tableHeader}`
      : classes.tableHeader,
    classes: { sizeSmall: classes.sizeSmallCell },
  };
  const tableMainCellOptions = {
    className: classes.tableMainCell,
  };

  const tableSortLabelProps = {
    classes: {
      active: classes.tableSortLabelProps,
      icon: classes.tableSortLabelProps,
    },
  };

  // const handleOpenSelectionMenu = (event) => {
  //   setSelectionMenuAnchor(event.currentTarget);
  // };

  // const handleCloseSelectionMenu = () => {
  //   setSelectionMenuAnchor(null);
  // };

  const getTableCellStyle = (column, row) => {
    return column.handleCellStyles
      ? { className: column.handleCellStyles(column, row, classes) }
      : null;
  };

  const getTableRowStyle = (row, rowIndex) => {
    if (!tableOptions.getCustomRowProps) return {};
    const clsName = tableOptions.getCustomRowProps(row, rowIndex, classes);

    return helper.isNullOrEmpty(clsName) ? {} : { className: clsName };
  };

  const handleOpenSelectionMenu = (event) => {
    setIsOpenSelectionMenu(true);
    setSelectionMenuAnchor(event.currentTarget);
  };

  const handleCloseSelectionMenu = () => {
    setIsOpenSelectionMenu(false);
  };

  const handleSelectInTable = (items) => {
    if (tableOptions.onSelectInTable) {
      tableOptions.onSelectInTable(items);
    }
  };

  const handleSelectItem = (value) => {
    let itemsToSelect = [];
    if (selectedItems.includes(value)) {
      itemsToSelect = selectedItems.filter((item) => item !== value);
    } else {
      itemsToSelect = [...selectedItems, value];
    }
    setSelectedItems(itemsToSelect);
    // handleSelectInTable(itemsToSelect);
  };

  const handleSelectAll = () => {
    const itemsToSelect = filteredData.map((el) => el[selectionField]);
    setSelectedItems(itemsToSelect);
    // handleSelectInTable(itemsToSelect);
  };

  const handleUnSelectAll = () => {
    setSelectedItems([]);
    handleSelectInTable([]);
  };

  const handleUpdateFilteredData = (data) => {
    setFilteredData(data);
    if (tableOptions.captureTableData) {
      tableOptions.captureTableData(data);
    }
  };

  const renderSelectionAction = (value) => {
    return (
      <Tooltip title={selectedItems.includes(value) ? "Selected" : "Select"}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleSelectItem(value)}
        >
          <Checkbox
            key={`table-selection-${value}`}
            checked={selectedItems.includes(value)}
            color="primary"
          />
        </IconButton>
      </Tooltip>
    );
  };

  const columns = useMemo(() => {
    if (selectionField) {
      return [
        {
          title: "",
          field: selectionField,
          sortable: _.isUndefined(selectionFieldIsSortable) ? false : selectionFieldIsSortable,
          type: ColumnType.Numeric,
          filterable: false,
          lookup: {
            0: "Unselected",
            1: "Selected",
          },
          render: renderSelectionAction,
        },
        ...tableColumns,
      ];
    }
    return tableColumns || [];
  }, [tableColumns, tableOptions.tableColumns, selectedItems]);

  useEffect(() => {
    if (isResetPageAfterUpdateTableData) {
      setPage(0);
    }
    setSelectedItems([]);
    if (!_.isEmpty(tableData?.data)) {
      setFilteredData(tableData?.data);
    }
  }, [tableData]);

  useEffect(() => {
    handleSelectInTable(selectedItems);
  }, [selectedItems]);

  return (
    <Box>
      <ErrorBoundary>
        <Paper elevation={0} className={classes.root} id={tableId}>
          <Grid container direction="row">
            {tableTitle ? (
              <Grid item xs={12} className={classes.titleCell}>
                <Typography variant="h2" className={classes.title}>
                  {tableTitle}
                </Typography>
              </Grid>
            ) : null}
            {tableData.isFetching ? (
              <ElementLoader isOpen={tableData.isFetching} />
            ) : (
              <Grid item xs={tableXS}>
                <ResponsiveTable
                  columns={columns}
                  page={page}
                  title={tableTitle}
                  data={tableData.data}
                  count={tableData.data ? tableData.data.length : 0}
                  onRowDoubleClick={
                    tableOptions.onRowDoubleClick
                      ? tableOptions.onRowDoubleClick
                      : handleRowDoubleClick
                  }
                  TableProps={tableOptions.tableProps ? tableOptions.tableProps : tableProps}
                  TableContainerProps={
                    tableOptions.tableContainerProps
                      ? tableOptions.tableContainerProps
                      : tableContainerProps
                  }
                  ContextMenuProps={
                    tableOptions.contextMenuProps ? tableOptions.contextMenuProps : contextMenuProps
                  }
                  rowsPerPage={rowsPerPage}
                  rowsPerPageOptions={tableOptions.rowsPerPageOptions}
                  showPagination={tableOptions.showPagination}
                  TableHeadCellProps={tableHeadCellOptions}
                  TableMainCellProps={tableMainCellOptions}
                  TableBodyRowProps={
                    tableOptions.tableBodyRowProps ? tableOptions.tableBodyRowProps : null
                  }
                  TableSortLabelProps={
                    tableOptions.tableSortLabelProps
                      ? tableOptions.tableSortLabelProps
                      : tableSortLabelProps
                  }
                  onRowSelection={
                    tableOptions.onRowSelection ? tableOptions.onRowSelection : handleRowSelection
                  }
                  selectedRowId={tableOptions.selectedRowId || -1}
                  selectedRowIndex={tableOptions.selectedRowIndex || -1}
                  onChangePage={
                    tableOptions.onChangePage ? tableOptions.onChangePage : handleChangePage
                  }
                  onChangeRowsPerPage={
                    tableOptions.onChangeRowsPerPage
                      ? tableOptions.onChangeRowsPerPage
                      : handleChangeRowsPerPage
                  }
                  noContentText={
                    tableOptions.noContentText ? tableOptions.noContentText : noContentText
                  }
                  excludePrimaryFromDetails={
                    tableOptions.excludePrimaryFromDetails
                      ? tableOptions.excludePrimaryFromDetails
                      : excludePrimaryFromDetails
                  }
                  cellStyleProvider={getTableCellStyle}
                  applyFilters={tableOptions.applyFilters || false}
                  getCustomRowProps={getTableRowStyle}
                  filterRowStyle={tableOptions.filterRowStyle || defaultFilterRowStyle}
                  filterCellStyle={defaultFilterCellStyle}
                  capturePageData={tableOptions.capturePageData}
                  captureTableData={handleUpdateFilteredData}
                  contextMenuAction={
                    tableOptions.contextMenuAction ||
                    (tableOptions.selectionField && handleOpenSelectionMenu)
                  }
                  summary={tableOptions.summary}
                />
              </Grid>
            )}
          </Grid>
        </Paper>
      </ErrorBoundary>
      <SelectionMenu
        closeAction={handleCloseSelectionMenu}
        isDisabledSelectAll={tableOptions.isDisabledSelectAll || false}
        onSelectAllInTable={
          tableOptions.onSelectAllInTable ? tableOptions.onSelectAllInTable : handleSelectAll
        }
        onUnSelectAllInTable={
          tableOptions.onUnSelectAllInTable ? tableOptions.onUnSelectAllInTable : handleUnSelectAll
        }
        anchor={selectionMenuAnchor}
        openMenu={isOpenSelectionMenu}
      />
    </Box>
  );
};

export default StandardTable;
