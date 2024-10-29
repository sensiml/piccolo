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

/* eslint-disable indent */
import React, { Fragment, Component } from "react";
import _ from "lodash";
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableFooter from "@mui/material/TableFooter";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableSortLabel from "@mui/material/TableSortLabel";
import Tooltip from "@mui/material/Tooltip";
import Box from "@mui/material/Box";
import MoreHorizIcon from "@mui/icons-material/MoreHoriz";
import IconButton from "@mui/material/IconButton";
import FilterListIcon from "@mui/icons-material/FilterList";
import FilterRow from "./Filters/FilterRow";
import NoContent from "./NoContent";
import Pagination from "./Pagination";

import { CompareOperators, ColumnType } from "./Filters/FilterConstants";
import { filterComparer } from "./Filters/FilterUtils";
import { CellRenderer, LabelRenderer } from "./Renderer";

/* Simple read only table with header and body */
export default class DataTable extends Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedRowIndex: -1,
      orderBy: "",
      order: "asc",
      filters: {},
    };
  }

  componentDidMount() {
    const displayData = this.getDisplayData();
    if (this.props.captureTableData) {
      this.props.captureTableData(displayData);
    }
    if (this.props.capturePageData) {
      const pageData = this.getPageData(displayData, this.props.page);
      this.props.capturePageData(pageData);
    }
  }

  shouldComponentUpdate(nextProps) {
    const { enableShouldComponentUpdate, data } = this.props;
    if (enableShouldComponentUpdate) {
      return !_.isEqual(nextProps.data, data);
    }
    return true;
  }

  componentDidUpdate(prevProps) {
    const displayData = this.getDisplayData();
    const pageData = this.getPageData(displayData, this.props.page);

    if (
      ((_.isEmpty(prevProps.data) && !_.isEmpty(this.props.data)) ||
        prevProps.page !== this.props.page) &&
      this.props.capturePageData
    ) {
      this.props.capturePageData(pageData);
    }

    if (
      // prevProps.uuid === this.props.selectedRowId ||
      prevProps.selectedRowId !== this.props.selectedRowId ||
      prevProps.selectedRowIndex !== this.props.selectedRowIndex
    ) {
      // react on selected row from outside
      const selectedIndex = displayData.findIndex(
        (row, rowIndex) =>
          row.uuid === this.props.selectedRowId ||
          row.id === this.props.selectedRowId ||
          rowIndex === this.props.selectedRowIndex,
      );

      if (selectedIndex !== -1) {
        const selectedPage = Math.floor(selectedIndex / this.props.rowsPerPage);
        const displayPageData = this.getPageData(displayData, selectedPage);
        const selectedIndexPage = displayPageData.findIndex(
          (row) => row.id === this.props.selectedRowId || row.uuid === this.props.selectedRowId,
        );
        this.handleChangePage({}, selectedPage);
        // eslint-disable-next-line react/no-did-update-set-state
        this.setState({ selectedRowIndex: selectedIndexPage });
      }
    }
  }

  handleChangePage = (event, page) => {
    this.props.onChangePage(event, page);
  };

  handleChangeRowsPerPage = (event, page) => this.props.onChangeRowsPerPage(event, page);

  handleRowDoubleClick = (event, row, rowIndex) => {
    this.props.onRowDoubleClick(event, row, rowIndex);
  };

  handleRowSelection = (event, row, rowIndex) => {
    this.setState({ selectedRowIndex: rowIndex });
    this.props.onRowSelection(event, row);
  };

  handleRowSelection = (event, row, rowIndex) => {
    this.setState({ selectedRowIndex: rowIndex });
    this.props.onRowSelection(event, row);
  };

  handleRequestSort = (event, column) => {
    const isAsc = this.state.orderBy === column.field && this.state.order === "asc";
    this.setState({ order: isAsc ? "desc" : "asc", orderBy: column.field });
  };

  handleRequestFilterOnColumn = (event, column) => {
    // eslint-disable-next-line react/no-access-state-in-setstate
    const fs = this.state.filters;
    // eslint-disable-next-line no-param-reassign
    column.filterRequested = true;
    const existingColFs = fs[column.field];

    const filterValue = existingColFs ? existingColFs.value : undefined;
    fs[column.field] = { value: filterValue, col: column };
    this.setState({ filters: fs });
  };

  adjustFilters = (column, operator, filterValue) => {
    // eslint-disable-next-line react/no-access-state-in-setstate
    const fs = this.state.filters;
    // eslint-disable-next-line no-param-reassign
    column.filterValue = filterValue;
    // eslint-disable-next-line no-param-reassign
    column.filterOperator = operator;
    if (!column.filterOperator) {
      // eslint-disable-next-line no-param-reassign
      column.filterOperator =
        !column.type || column.type === ColumnType.Text
          ? CompareOperators.Contains
          : CompareOperators.Equals;
    }
    if (!filterValue || filterValue === "") {
      delete fs[column.field];
      // eslint-disable-next-line no-param-reassign
      column.filterValue = undefined;
      // eslint-disable-next-line no-param-reassign
      column.filterOperator = undefined;
    } else {
      fs[column.field] = { value: filterValue, col: column };
    }

    this.setState({ filters: fs });

    if (this.props.captureTableData) {
      this.props.captureTableData(this.getDisplayData());
    }
  };

  hanldeFilterChanged = (column, filterValue) => {
    this.adjustFilters(column, column ? column.filterOperator : undefined, filterValue);
  };

  hanldeFilterOperatorChanged = (column, operator) => {
    this.adjustFilters(column, operator, column ? column.filterValue : undefined);
  };

  getRowClass = (index) => {
    const { rowsClassArray } = this.props;
    return rowsClassArray && rowsClassArray[index] ? rowsClassArray[index] : "";
  };

  setIsSelected = (rowIndex) => {
    return this.state.selectedRowIndex === rowIndex;
  };

  descendingComparator = (a, b, orderBy, column) => {
    const aVal = this.getVal(column, a, orderBy);
    const bVal = this.getVal(column, b, orderBy);

    if (bVal < aVal) {
      return -1;
    }
    if (bVal > aVal) {
      return 1;
    }
    return 0;
  };

  getVal = (column, row, orderBy) => {
    if (!column) return row[orderBy];

    switch (column.type) {
      case "date":
        return new Date(row[orderBy]);
      case "numeric":
        return parseFloat(row[orderBy]) || Number.MIN_VALUE;
      default:
        return row[orderBy] !== null ? row[orderBy] : "";
    }
  };

  getComparator = (order, orderBy, column) => {
    return order === "desc"
      ? (a, b) => this.descendingComparator(a, b, orderBy, column)
      : (a, b) => -this.descendingComparator(a, b, orderBy, column);
  };

  filterData = (array) => {
    const filterProperties = Object.entries(this.state.filters);
    let retArray = array;
    if (filterProperties && filterProperties.length > 0) {
      retArray = retArray.filter((d) => {
        let match = true;
        filterProperties.forEach((f) => {
          match = match ? filterComparer(d[f[0]], f[1]) : match;
        });
        return match;
      });
    }
    return retArray;
  };

  stableSort = (array, comparator) => {
    if (this.state.orderBy === "") return array;
    const stabilizedThis = array.map((el, index) => [el, index]);
    stabilizedThis.sort((a, b) => {
      const order = comparator(a[0], b[0]);
      if (order !== 0) return order;
      return a[1] - b[1];
    });
    return stabilizedThis.map((el) => el[0]);
  };

  getDisplayData = () => {
    return this.stableSort(
      this.filterData(this.props.data),
      this.getComparator(
        this.state.order,
        this.state.orderBy,
        this.props.columns.find((c) => c.field === this.state.orderBy),
      ),
    );
  };

  getPageData = (displayData, page) => {
    const { rowsPerPage } = this.props;
    const rowCount = displayData?.length || 0;
    if (!_.isEmpty(displayData)) {
      return displayData.slice(
        rowCount < page * rowsPerPage ? 0 : page * rowsPerPage,
        page * rowsPerPage + rowsPerPage,
      );
    }
    return displayData;
  };

  render() {
    const {
      data,
      noContentText,
      page,
      rowsPerPage,
      rowsPerPageOptions,
      showPagination,
      TableBodyCellProps,
      TableBodyProps,
      TableBodyRowProps,
      TableHeadCellProps,
      TableHeadProps,
      TableHeadRowProps,
      TableSortLabelProps,
      TablePaginationProps,
      TableProps,
      TableContainerProps,
      ContextMenuProps,
      filterRowStyle,
      filterCellStyle,
      cellStyleProvider,
      applyFilters,
      getCustomRowProps,
      contextMenuAction,
    } = this.props;

    const { columns } = this.props;

    if (
      !Array.isArray(data) ||
      data.length === 0 ||
      !Array.isArray(columns) ||
      columns.length === 0
    ) {
      return <NoContent text={noContentText} />;
    }
    const displayData = this.getDisplayData();

    const rowCount = displayData.length;

    const pageData = this.getPageData(displayData, page);

    const shouldShowFilterRow = () => {
      if (!columns) return false;
      const filterableColumns = columns.filter(
        (column) =>
          column.filterable === true && (column.filterValue || column.filterRequested === true),
      );
      return filterableColumns && filterableColumns.length > 0;
    };

    return (
      <>
        <TableContainer {...TableContainerProps}>
          <Table {...TableProps}>
            <TableHead {...TableHeadProps}>
              <TableRow {...TableHeadRowProps}>
                {columns.map((column, index) => (
                  <TableCell key={`${column.title}-${index}`} {...TableHeadCellProps}>
                    <Box
                      style={
                        index === 0 && contextMenuAction
                          ? {
                              alignItems: "center",
                              display: "flex",
                              justifyContent: "flex-start",
                            }
                          : {}
                      }
                    >
                      {index === 0 && contextMenuAction ? (
                        <div {...ContextMenuProps}>
                          <Tooltip title="Open Menu ...">
                            <IconButton
                              variant="contained"
                              color="inherit"
                              size="small"
                              onClick={contextMenuAction}
                            >
                              <MoreHorizIcon />
                            </IconButton>
                          </Tooltip>
                        </div>
                      ) : null}
                      {column.sortable ? (
                        <TableSortLabel
                          active={this.state.orderBy === column.field}
                          direction={this.state.orderBy === column.field ? this.state.order : "asc"}
                          {...TableSortLabelProps}
                          onClick={(event) => this.handleRequestSort(event, column)}
                        >
                          <LabelRenderer column={column} data={data} />
                        </TableSortLabel>
                      ) : (
                        <LabelRenderer column={column} data={data} />
                      )}
                      {applyFilters &&
                      column.filterRequested !== true &&
                      column.filterValue === undefined &&
                      column.filterable === true ? (
                        <Tooltip title="Filter">
                          <FilterListIcon
                            style={{ verticalAlign: "bottom" }}
                            onClick={(event) => this.handleRequestFilterOnColumn(event, column)}
                          />
                        </Tooltip>
                      ) : null}
                    </Box>
                  </TableCell>
                ))}
              </TableRow>

              {applyFilters && shouldShowFilterRow(columns) && (
                <FilterRow
                  columns={columns.filter((columnDef) => !columnDef.hidden)}
                  columnFilters={this.state.filters}
                  icons={this.props.icons}
                  onFilterChanged={this.hanldeFilterChanged}
                  onFilterOperatorChanged={this.hanldeFilterOperatorChanged}
                  selection={false}
                  hasDetailPanel={false}
                  isTreeData={false}
                  filterCellStyle={filterCellStyle}
                  filterRowStyle={filterRowStyle}
                  hideFilterIcons={false}
                />
              )}
            </TableHead>
            <TableBody {...TableBodyProps}>
              {pageData.map((row, rowIndex) => (
                <TableRow
                  key={`${rowIndex}-${row?.id}`}
                  onClick={(event) => this.handleRowSelection(event, row, rowIndex)}
                  onDoubleClick={(event) => this.handleRowDoubleClick(event, row, rowIndex)}
                  className={this.getRowClass(rowIndex)}
                  selected={this.setIsSelected(rowIndex)}
                  {...{
                    ...TableBodyRowProps,
                    ...getCustomRowProps(row, rowIndex),
                  }}
                >
                  {this.props.columns.map((column, columnIndex) => {
                    return (
                      <TableCell
                        key={`${rowIndex}-${columnIndex}-${row?.id}`}
                        {...{
                          ...TableBodyCellProps,
                          ...cellStyleProvider(column, row),
                        }}
                      >
                        <CellRenderer column={column} row={row} />
                      </TableCell>
                    );
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        {showPagination && (
          <Table>
            <TableFooter>
              <TableRow>
                <Pagination
                  count={rowCount}
                  rowsPerPage={rowsPerPage}
                  rowsPerPageOptions={rowsPerPageOptions}
                  page={page}
                  TablePaginationProps={TablePaginationProps}
                  onChangePage={this.handleChangePage}
                  onChangeRowsPerPage={this.handleChangeRowsPerPage}
                />
              </TableRow>
            </TableFooter>
          </Table>
        )}
      </>
    );
  }
}
