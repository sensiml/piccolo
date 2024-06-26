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

/* eslint-disable react/require-default-props */
import * as React from "react";
import PropTypes from "prop-types";
// eslint-disable-next-line import/no-extraneous-dependencies
import { chainPropTypes } from "@mui/utils";
import clsx from "clsx";
import withStyles from "@mui/styles/withStyles";
import { InputBase, MenuItem, Select, TableCell, Toolbar, Typography } from "@mui/material";

export const styles = (theme) => ({
  /* Styles applied to the root element. */
  root: {
    color: theme.palette.text.primary,
    fontSize: theme.typography.pxToRem(14),
    overflow: "auto",
    // Increase the specificity to override TableCell.
    "&:last-child": {
      padding: 0,
    },
  },
  /* Styles applied to the Toolbar component. */
  toolbar: {
    minHeight: 24,
    paddingRight: 2,
  },
  /* Styles applied to the spacer element. */
  spacer: {
    flex: "1 1 100%",
  },
  /* Styles applied to the caption Typography components if `variant="caption"`. */
  caption: {
    flexShrink: 0,
  },
  /* Styles applied to the Select component root element. */
  selectRoot: {
    // `.selectRoot` should be merged with `.input` in v5.
    marginRight: 32,
    marginLeft: 8,
  },
  /* Styles applied to the Select component `select` class. */
  select: {
    paddingLeft: 8,
    paddingRight: 24,
    textAlign: "right",
    textAlignLast: "right", // Align <select> on Chrome.
  },
  // TODO v5: remove
  /* Styles applied to the Select component `icon` class. */
  selectIcon: {},
  /* Styles applied to the `InputBase` component. */
  input: {
    color: "inherit",
    fontSize: "inherit",
    flexShrink: 0,
  },
  /* Styles applied to the MenuItem component. */
  menuItem: {},
  /* Styles applied to the internal `TablePaginationActions` component. */
  actions: {
    flexShrink: 0,
    marginLeft: 20,
  },
});

const defaultLabelDisplayedRows = ({ from, to, count }) =>
  `${from}-${to === -1 ? count : to} of ${count !== -1 ? count : `more than ${to}`}`;
const defaultRowsPerPageOptions = [10, 25, 50, 100];

/**
 * A `TableCell` based component for placing inside `TableFooter` for pagination.
 */
const ExtendedTablePagination = React.forwardRef(function ExtendedTablePagination(props, ref) {
  const {
    ActionsComponent,
    backIconButtonProps,
    backIconButtonText = "Previous page",
    classes,
    className,
    colSpan: colSpanProp,
    component: Component = TableCell,
    count,
    labelDisplayedRows = defaultLabelDisplayedRows,
    labelRowsPerPage = "Rows per page:",
    nextIconButtonProps,
    nextIconButtonText = "Next page",
    onChangePage,
    onChangeRowsPerPage,
    page,
    rowsPerPage,
    rowsPerPageOptions = defaultRowsPerPageOptions,
    SelectProps = {},
    ...other
  } = props;

  let colSpan;

  if (Component === TableCell || Component === "td") {
    colSpan = colSpanProp || 1000; // col-span over everything
  }

  const MenuItemComponent = SelectProps.native ? "option" : MenuItem;

  return (
    <Component className={clsx(classes.root, className)} colSpan={colSpan} ref={ref} {...other}>
      <Toolbar className={classes.toolbar}>
        <div className={classes.spacer} />
        {rowsPerPageOptions.length > 1 && (
          <Typography color="inherit" variant="body2" className={classes.caption}>
            {labelRowsPerPage}
          </Typography>
        )}
        {rowsPerPageOptions.length > 1 && (
          <Select
            classes={{
              select: classes.select,
              icon: classes.selectIcon,
            }}
            input={<InputBase className={clsx(classes.input, classes.selectRoot)} />}
            value={rowsPerPage}
            onChange={onChangeRowsPerPage}
            {...SelectProps}
          >
            {rowsPerPageOptions.map((rowsPerPageOption) => (
              <MenuItemComponent
                className={classes.menuItem}
                key={rowsPerPageOption.value ? rowsPerPageOption.value : rowsPerPageOption}
                value={rowsPerPageOption.value ? rowsPerPageOption.value : rowsPerPageOption}
              >
                {rowsPerPageOption.label ? rowsPerPageOption.label : rowsPerPageOption}
              </MenuItemComponent>
            ))}
          </Select>
        )}
        <Typography color="inherit" variant="body2" className={classes.caption}>
          {labelDisplayedRows({
            from: count === 0 ? 0 : Math.min(count, page * rowsPerPage + 1),
            to: count !== -1 ? Math.min(count, (page + 1) * rowsPerPage) : (page + 1) * rowsPerPage,
            count,
            page,
          })}
        </Typography>
        <ActionsComponent
          className={classes.actions}
          backIconButtonProps={{
            title: backIconButtonText,
            "aria-label": backIconButtonText,
            ...backIconButtonProps,
          }}
          count={count}
          nextIconButtonProps={{
            title: nextIconButtonText,
            "aria-label": nextIconButtonText,
            ...nextIconButtonProps,
          }}
          onChangePage={onChangePage}
          page={page}
          rowsPerPage={rowsPerPage}
        />
      </Toolbar>
    </Component>
  );
});

ExtendedTablePagination.propTypes = {
  /**
   * The component used for displaying the actions.
   * Either a string to use a DOM element or a component.
   */
  ActionsComponent: PropTypes.elementType,
  /**
   * Props applied to the back arrow [`IconButton`](/api/icon-button/) component.
   */
  backIconButtonProps: PropTypes.object,
  /**
   * Text label for the back arrow icon button.
   *
   * For localization purposes, you can use the provided [translations](/guides/localization/).
   */
  backIconButtonText: PropTypes.string,
  /**
   * Override or extend the styles applied to the component.
   * See [CSS API](#css) below for more details.
   */
  classes: PropTypes.object.isRequired,
  /**
   * @ignore
   */
  className: PropTypes.string,
  /**
   * @ignore
   */
  colSpan: PropTypes.number,
  /**
   * The component used for the root node.
   * Either a string to use a DOM element or a component.
   */
  component: PropTypes.elementType,
  /**
   * The total number of rows.
   *
   * To enable server side pagination for an unknown number of items, provide -1.
   */
  count: PropTypes.number.isRequired,
  /**
   * Customize the displayed rows label. Invoked with a `{ from, to, count, page }`
   * object.
   *
   * For localization purposes, you can use the provided [translations](/guides/localization/).
   */
  labelDisplayedRows: PropTypes.func,
  /**
   * Customize the rows per page label.
   *
   * For localization purposes, you can use the provided [translations](/guides/localization/).
   */
  labelRowsPerPage: PropTypes.node,
  /**
   * Props applied to the next arrow [`IconButton`](/api/icon-button/) element.
   */
  nextIconButtonProps: PropTypes.object,
  /**
   * Text label for the next arrow icon button.
   *
   * For localization purposes, you can use the provided [translations](/guides/localization/).
   */
  nextIconButtonText: PropTypes.string,
  /**
   * Callback fired when the page is changed.
   *
   * @param {object} event The event source of the callback.
   * @param {number} page The page selected.
   */
  onChangePage: PropTypes.func.isRequired,
  /**
   * Callback fired when the number of rows per page is changed.
   *
   * @param {object} event The event source of the callback.
   */
  onChangeRowsPerPage: PropTypes.func,
  /**
   * The zero-based index of the current page.
   */
  page: chainPropTypes(PropTypes.number.isRequired, (props) => {
    const { count, page, rowsPerPage } = props;

    if (count === -1) {
      return null;
    }

    const newLastPage = Math.max(0, Math.ceil(count / rowsPerPage) - 1);
    if (page < 0 || page > newLastPage) {
      return new Error(
        "Material-UI: the page prop of a TablePagination is out of range " +
          `(0 to ${newLastPage}, but page is ${page}).`,
      );
    }
    return null;
  }),
  /**
   * The number of rows per page.
   */
  // rowsPerPage: PropTypes.number.isRequired,
  /**
   * Customizes the options of the rows per page select field. If less than two options are
   * available, no select field will be displayed.
   */
  rowsPerPageOptions: PropTypes.array,
  /**
   * Props applied to the rows per page [`Select`](/api/select/) element.
   */
  SelectProps: PropTypes.object,
};

export default withStyles(styles, { name: "MuiTablePagination" })(ExtendedTablePagination);
