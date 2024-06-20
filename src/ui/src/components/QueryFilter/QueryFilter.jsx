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
import { FormControl, InputAdornment, TextField, Tooltip } from "@mui/material";
import IconButton from "@mui/material/IconButton";
import FilterListIcon from "@mui/icons-material/FilterList";
import ErrorBoundary from "components/ErrorBoundary";

import QueryBuilder from "./QueryBuilder";
import useStyles from "./QueryFilterStyles";

const QueryFilter = ({ value, onChange, isDisabled, queryMetada, queryLabel }) => {
  const [open, setOpen] = useState(false);
  const [queryFilter, setQueryFilter] = useState(value);
  const classes = useStyles();
  const handleQueryFilterChange = (event) => {
    onChange(event);
  };

  useEffect(() => {
    onChange(queryFilter);
  }, [queryFilter]);

  useEffect(() => {
    setQueryFilter(value);
  }, [value]);

  return (
    <ErrorBoundary>
      <FormControl fullWidth>
        <TextField
          id="metadata_filter"
          label="Query Filter"
          name="metadata_filter"
          value={queryFilter}
          onChange={handleQueryFilterChange}
          disabled={isDisabled}
          classes={{
            root: classes.root, // class name, e.g. `root-x`
            disabled: classes.disabled, // class name, e.g. `disabled-x`
          }}
          InputLabelProps={{
            classes: { disabled: classes.queryFilterTextField },
          }}
          InputProps={{
            classes: { disabled: classes.queryFilterTextField },
            endAdornment: (
              <InputAdornment>
                <Tooltip title={queryFilter}>
                  <IconButton id="queryFilterBtn" onClick={() => setOpen(true)} size="large">
                    <FilterListIcon />
                  </IconButton>
                </Tooltip>
              </InputAdornment>
            ),
          }}
        />
      </FormControl>

      <QueryBuilder
        value={queryFilter}
        open={open}
        setOpen={setOpen}
        setQueryFilter={setQueryFilter}
        queryMetada={queryMetada}
        queryLabel={queryLabel}
      />
    </ErrorBoundary>
  );
};

export default React.memo(QueryFilter);
