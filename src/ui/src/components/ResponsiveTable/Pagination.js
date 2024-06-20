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
import TableCell from "@mui/material/TableCell";
import ExtendedTablePagination from "./ExtendedTablePagination";
import TablePaginationActions from "./TablePaginationActions";

export default class Pagination extends Component {
  handleChangePage = (event, page) => this.props.onChangePage(event, page);

  handleChangeRowsPerPage = (event, page) => this.props.onChangeRowsPerPage(event, page);

  handleLabelDisplayedRows = ({ from, to, count }) => {
    if (isNaN(from)) {
      return "";
    }
    return `${from}-${isNaN(to) ? count : to} of ${count !== -1 ? count : `more than ${to}`}`;
  };

  render() {
    const { component, count, rowsPerPage, rowsPerPageOptions, page, TablePaginationProps } =
      this.props;

    return (
      <ExtendedTablePagination
        {...TablePaginationProps}
        component={component || TableCell}
        count={count}
        rowsPerPage={rowsPerPage === count + 10 ? "All" : rowsPerPage}
        rowsPerPageOptions={rowsPerPageOptions || [rowsPerPage]}
        page={page}
        labelDisplayedRows={this.handleLabelDisplayedRows}
        onChangeRowsPerPage={this.handleChangeRowsPerPage}
        onChangePage={this.handleChangePage}
        ActionsComponent={TablePaginationActions}
      />
    );
  }
}
