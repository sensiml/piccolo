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
import Grid from "@mui/material/Grid";
import _isEqual from "lodash.isequal";
import { CellRenderer, LabelRenderer } from "./Renderer";
import ExpandableListItem from "./ExpandableListItem";
import NoContent from "./NoContent";
import Pagination from "./Pagination";

/* List with expandable items - mobile table analogue */
export default class DataList extends Component {
  shouldComponentUpdate(nextProps) {
    const { enableShouldComponentUpdate, data } = this.props;
    if (enableShouldComponentUpdate) {
      return !_isEqual(nextProps.data, data);
    }
    return true;
  }

  handleChangePage = (event, page) => this.props.onChangePage(event, page);

  getRowClass = (index) => {
    const { rowsClassArray } = this.props;
    return rowsClassArray && rowsClassArray[index] ? rowsClassArray[index] : "";
  };

  createListItemTitle = (columns, row, data) => {
    const primaryColumns = columns.filter((column) => column.primary);
    return primaryColumns.length === 0 ? (
      <CellRenderer column={columns[0]} row={row} data={data} />
    ) : (
      primaryColumns
        .map((column) => <CellRenderer key={column.field} column={column} row={row} data={data} />)
        .reduce((prev, next) => [prev, " ", next])
    ); // divide item headers by space
  };

  createListItemDescription = (columns, row, data, excludePrimary) => (
    <div>
      {columns
        .filter((column) => !excludePrimary || !column.primary)
        .map((column, index) => (
          <Grid key={`${column.title}-${index}`} container>
            <Grid item xs>
              <LabelRenderer column={column} data={data} />
            </Grid>
            <Grid item xs>
              <CellRenderer column={column} row={row} data={data} />
            </Grid>
          </Grid>
        ))}
    </div>
  );

  render() {
    const {
      columns,
      count,
      data,
      excludePrimaryFromDetails,
      noContentText,
      page,
      rowsPerPage,
      scrollToSelected,
      scrollOptions,
      showPagination,
      AccordionDetailsProps,
      AccordionDetailsTypographyProps,
      AccordionMoreIconProps,
      AccordionProps,
      AccordionSummaryProps,
      AccordionSummaryTypographyProps,
      SelectedExpansionPanelProps,
      TablePaginationProps,
    } = this.props;
    if (
      !Array.isArray(data) ||
      data.length === 0 ||
      !Array.isArray(columns) ||
      columns.length === 0
    ) {
      return <NoContent text={noContentText} />;
    }

    return (
      <div>
        {data.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row, index) => (
          <ExpandableListItem
            key={index}
            panelClass={this.getRowClass(index)}
            summary={this.createListItemTitle(columns, row, data)}
            details={this.createListItemDescription(columns, row, data, excludePrimaryFromDetails)}
            selected={row.selected}
            scrollToSelected={scrollToSelected}
            scrollOptions={scrollOptions}
            AccordionDetailsProps={AccordionDetailsProps}
            AccordionDetailsTypographyProps={AccordionDetailsTypographyProps}
            AccordionMoreIconProps={AccordionMoreIconProps}
            AccordionProps={AccordionProps}
            AccordionSummaryProps={AccordionSummaryProps}
            AccordionSummaryTypographyProps={AccordionSummaryTypographyProps}
            SelectedExpansionPanelProps={SelectedExpansionPanelProps}
          />
        ))}
        {showPagination && (
          <Pagination
            component="div"
            count={count}
            rowsPerPage={rowsPerPage}
            page={page}
            TablePaginationProps={TablePaginationProps}
            onChangePage={this.handleChangePage}
          />
        )}
      </div>
    );
  }
}
