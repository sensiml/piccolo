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

/* eslint-disable consistent-return */
/* eslint-disable indent */
import * as React from "react";
import PropTypes from "prop-types";
import Box from "@mui/material/Box";
import TableCell from "@mui/material/TableCell";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import FormControl from "@mui/material/FormControl";
import Select from "@mui/material/Select";
import Input from "@mui/material/Input";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Checkbox from "@mui/material/Checkbox";
import ListItemText from "@mui/material/ListItemText";
import InputAdornment from "@mui/material/InputAdornment";
import FilterListIcon from "@mui/icons-material/FilterList";

import { LocalizationProvider } from "@mui/x-date-pickers/LocalizationProvider";
import { DatePicker, DateTimePicker, TimePicker } from "@mui/x-date-pickers";
import { AdapterDayjs } from "@mui/x-date-pickers/AdapterDayjs";

import FiterOptions from "./FiterOptions";
import { ColumnType } from "./FilterConstants";

const DD_MAX_LENGTH = 20;
const DD_MAX_ENDING = "...";
const ITEM_HEIGHT = 48;
const ITEM_PADDING_TOP = 8;
const MenuProps = {
  PaperProps: {
    style: {
      maxHeight: ITEM_HEIGHT * 4.5 + ITEM_PADDING_TOP,
      width: 250,
    },
  },
};

class FilterRow extends React.Component {
  getLocalizationData = () => ({
    ...FilterRow.defaultProps.localization,
    ...this.props.localization,
  });

  getLocalizedFilterPlaceHolder = (columnDef) =>
    columnDef.filterPlaceholder || this.getLocalizationData().filterPlaceHolder || "";

  LookupFilter = ({ columnDef, existingValue }) => {
    const [selectedFilter, setSelectedFilter] = React.useState(existingValue || []);

    React.useEffect(() => {
      setSelectedFilter(existingValue || []);
    }, [existingValue]);

    const getSelectedValues = (selecteds) => {
      const selectedValues = selecteds.map((selected) => columnDef.lookup[selected]);
      if (columnDef.filterHasIcons === true) {
        return <div> {selectedValues}</div>;
      }
      const displayText = selectedValues.join(", ");

      return displayText.length > DD_MAX_LENGTH
        ? displayText.substring(0, DD_MAX_LENGTH - DD_MAX_ENDING.length) + DD_MAX_ENDING
        : displayText;
    };

    return (
      <FormControl style={{ width: "100%" }}>
        <InputLabel htmlFor="select-multiple-checkbox" style={{ marginTop: -16 }}>
          {this.getLocalizedFilterPlaceHolder(columnDef)}
        </InputLabel>
        <Select
          multiple
          value={selectedFilter}
          onClose={() => {
            this.props.onFilterChanged(columnDef, selectedFilter);
          }}
          IconComponent={FilterListIcon}
          onChange={(event) => {
            this.props.onFilterChanged(columnDef, event.target.value);
            setSelectedFilter(event.target.value);
          }}
          input={<Input id="select-multiple-checkbox" />}
          renderValue={(selecteds) => getSelectedValues(selecteds)}
          MenuProps={MenuProps}
          style={{ marginTop: 0 }}
        >
          {Object.keys(columnDef.lookup).map((key) => (
            <MenuItem key={key} value={key}>
              <Checkbox checked={selectedFilter.indexOf(key.toString()) > -1} />
              <ListItemText primary={columnDef.lookup[key]} />
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    );
  };

  renderFilterComponent = (columnDef) =>
    React.createElement(columnDef.filterComponent, {
      columnDef,
      onFilterChanged: this.props.onFilterChanged,
    });

  renderBooleanFilter = (columnDef, existingFilter) => (
    <Checkbox
      indeterminate={existingFilter === undefined}
      checked={existingFilter === "checked"}
      onChange={() => {
        let val;
        if (existingFilter === undefined) {
          val = "checked";
        } else if (existingFilter === "checked") {
          val = "unchecked";
        }

        this.props.onFilterChanged(columnDef, val);
      }}
    />
  );

  renderDefaultFilter = (columnDef, existingFilter) => {
    return (
      <TextField
        type={columnDef.type === ColumnType.Numeric ? "number" : "search"}
        value={existingFilter || ""}
        placeholder={this.getLocalizedFilterPlaceHolder(columnDef)}
        onChange={(event) => {
          this.props.onFilterChanged(columnDef, event.target.value);
        }}
        inputProps={{ "aria-label": `filter data by ${columnDef.title}` }}
        // eslint-disable-next-line react/jsx-no-duplicate-props
        InputProps={
          this.props.hideFilterIcons || columnDef.hideFilterIcon
            ? undefined
            : {
                startAdornment: (
                  <InputAdornment position="start">
                    <FiterOptions
                      column={columnDef}
                      onChange={(operator) => {
                        this.props.onFilterOperatorChanged(columnDef, operator);
                      }}
                    />
                  </InputAdornment>
                ),
              }
        }
      />
    );
  };

  renderDateTypeFilter = (columnDef, existingFilter) => {
    const onDateInputChange = (date) => this.props.onFilterChanged(columnDef, date);
    const pickerProps = {
      value: existingFilter || null,
      onChange: onDateInputChange,
      label: this.getLocalizedFilterPlaceHolder(columnDef),
      clearable: true,
      slotProps: {
        actionBar: { actions: ["clear"] },
        textField: {
          inputFormat: columnDef.type === "datetime" ? "MM/dd/yyyy hh:mm:ss a" : "MM/dd/yyyy",
        },
      },
    };

    let dateInputElement = null;
    if (columnDef.type === "date") {
      dateInputElement = (
        <Box style={{ display: "flex", alignItems: "center" }}>
          {this.props.hideFilterIcons || columnDef.hideFilterIcon ? null : (
            <InputAdornment position="start">
              <FiterOptions
                column={columnDef}
                onChange={(operator) => {
                  this.props.onFilterOperatorChanged(columnDef, operator);
                }}
              />
            </InputAdornment>
          )}
          <DatePicker {...pickerProps} />
        </Box>
      );
    } else if (columnDef.type === "datetime") {
      dateInputElement = <DateTimePicker {...pickerProps} />;
    } else if (columnDef.type === "time") {
      dateInputElement = <TimePicker {...pickerProps} />;
    }
    return (
      <LocalizationProvider
        dateAdapter={AdapterDayjs}
        locale={this.props.localization.dateTimePickerLocalization}
      >
        {dateInputElement}
      </LocalizationProvider>
    );
  };

  // eslint-disable-next-line react/sort-comp
  getComponentForColumn(columnDef, columnFilters) {
    if (!columnDef.filterable || columnDef.filterable === false) {
      return null;
    }

    if (
      (!columnDef.filterRequested || columnDef.filterRequested === false) &&
      !columnDef.filterValue
    ) {
      return null;
    }

    const existingFilter = columnFilters[columnDef.field]
      ? columnFilters[columnDef.field].value
      : null;

    if (columnDef.field || columnDef.customFilterAndSearch) {
      if (columnDef.filterComponent) {
        return this.renderFilterComponent(columnDef, existingFilter);
      }
      if (columnDef.lookup) {
        return <this.LookupFilter columnDef={columnDef} existingFilter={existingFilter} />;
      }
      if (columnDef.type === "boolean") {
        return this.renderBooleanFilter(columnDef, existingFilter);
      }
      if (["date", "datetime", "time"].includes(columnDef.type)) {
        return this.renderDateTypeFilter(columnDef, existingFilter);
      }
      return this.renderDefaultFilter(columnDef, existingFilter);
    }
  }

  render() {
    const columns = this.props.columns.map((columnDef, index) => (
      <TableCell
        key={`${columnDef.field}-${index}`}
        style={{
          ...this.props.filterCellStyle,
          ...columnDef.filterCellStyle,
        }}
      >
        {this.getComponentForColumn(columnDef, this.props.columnFilters)}
      </TableCell>
    ));

    if (this.props.hasActions) {
      if (this.props.actionsColumnIndex === -1) {
        columns.push(<TableCell key="key-action-column" />);
      } else {
        let endPos = 0;
        if (this.props.selection) {
          endPos = 1;
        }
        columns.splice(
          this.props.actionsColumnIndex + endPos,
          0,
          <TableCell key="key-action-column" id={`hasActions`} />,
        );
      }
    }

    return <TableRow style={{ height: 5, ...this.props.filterRowStyle }}>{columns}</TableRow>;
  }
}

FilterRow.defaultProps = {
  hasActions: false,
  localization: {
    filterTooltip: "Filter",
  },
  hideFilterIcons: false,
  filterCellStyle: {},
  filterRowStyle: {},
  actionsColumnIndex: 0,
};

FilterRow.propTypes = {
  columns: PropTypes.array.isRequired,
  columnFilters: PropTypes.object.isRequired,
  hasDetailPanel: PropTypes.bool.isRequired,
  isTreeData: PropTypes.bool.isRequired,
  onFilterChanged: PropTypes.func.isRequired,
  onFilterOperatorChanged: PropTypes.func.isRequired,
  filterCellStyle: PropTypes.object,
  filterRowStyle: PropTypes.object,
  selection: PropTypes.bool.isRequired,
  actionsColumnIndex: PropTypes.number,
  hasActions: PropTypes.bool,
  localization: PropTypes.object,
  hideFilterIcons: PropTypes.bool,
};

export default FilterRow;
