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

import React, { Component } from "react";

import withStyles from "@mui/styles/withStyles";

import DataTable from "./DataTable";

const styles = {
  root: {},
};

/**
 * Responsive read-only table (desktop devices)
 * <-> read-only expandable list (tablet/mobile devices) for material-ui 1.0-beta.
 */
class ResponsiveTable extends Component {
  handleChangePage = (event, page) => this.props.onChangePage(event, page);

  handleChangeRowsPerPage = (event, page) => this.props.onChangeRowsPerPage(event, page);

  handleRowDoubleClick = (event, row, rowIndex) =>
    this.props.onRowDoubleClick(event, row, rowIndex);

  handleRowSelection = (event, row) => this.props.onRowSelection(event, row);

  handleIsRowSelection = (rowIndex) => this.props.handleIsRowSelection(rowIndex);

  render() {
    const {
      classes,
      columns,
      count,
      data,
      rowsClassArray,
      noContentText,
      page,
      rowsPerPage,
      rowsPerPageOptions,
      showPagination,
      capturePageData,
      captureTableData,
      TableBodyCellProps,
      TableBodyProps,
      TableBodyRowProps,
      TableHeadCellProps,
      TableMainCellProps,
      TableHeadProps,
      TableHeadRowProps,
      TableSortLabelProps,
      TablePaginationProps,
      TableProps,
      TableContainerProps,
      ContextMenuProps,
      enableShouldComponentUpdate,
      cellStyleProvider,
      applyFilters,
      getCustomRowProps,
      filterRowStyle,
      filterCellStyle,
      contextMenuAction,
      summary,
    } = this.props;
    return (
      <div className={classes.root}>
        {/* DESKTOP BIG TABLE */}

        <DataTable
          enableShouldComponentUpdate={enableShouldComponentUpdate}
          columns={columns}
          count={count}
          data={data}
          capturePageData={capturePageData}
          captureTableData={captureTableData}
          rowsClassArray={rowsClassArray}
          noContentText={noContentText}
          page={page}
          rowsPerPage={rowsPerPage}
          rowsPerPageOptions={rowsPerPageOptions}
          showPagination={showPagination}
          TableBodyCellProps={TableBodyCellProps}
          TableBodyProps={TableBodyProps}
          TableBodyRowProps={TableBodyRowProps}
          TableHeadCellProps={TableHeadCellProps}
          TableMainCellProps={TableMainCellProps}
          TableHeadProps={TableHeadProps}
          TableHeadRowProps={TableHeadRowProps}
          TableSortLabelProps={TableSortLabelProps}
          TablePaginationProps={TablePaginationProps}
          TableProps={TableProps}
          TableContainerProps={TableContainerProps}
          ContextMenuProps={ContextMenuProps}
          onChangePage={this.handleChangePage}
          onChangeRowsPerPage={this.handleChangeRowsPerPage}
          onRowDoubleClick={this.handleRowDoubleClick}
          onRowSelection={this.handleRowSelection}
          selectedRowId={this.props.selectedRowId}
          selectedRowIndex={this.props.selectedRowIndex}
          isSelected={this.handleIsRowSelection}
          cellStyleProvider={cellStyleProvider}
          applyFilters={applyFilters}
          getCustomRowProps={getCustomRowProps}
          filterRowStyle={filterRowStyle}
          filterCellStyle={filterCellStyle}
          contextMenuAction={contextMenuAction}
          summary={summary}
        />
      </div>
    );
  }
}
export default withStyles(styles)(ResponsiveTable);
