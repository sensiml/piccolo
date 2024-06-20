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

import React, { useState } from "react";
import { Button, Box, InputAdornment, TextField, Tooltip } from "@mui/material";
import RefreshIcon from "@mui/icons-material/Refresh";
import IconButton from "@mui/material/IconButton";
import SearchIcon from "@mui/icons-material/Search";
import ErrorBoundary from "components/ErrorBoundary";
import useStyles from "./ProjectSearchStyles";

const ProjectSearch = ({ setSearchText, resetHandler }) => {
  const [searchValue, setSearchValue] = useState("");
  const classes = useStyles();

  const handleRefresh = () => {
    setSearchValue("");
    resetHandler();
  };

  const handleTextChange = (event) => {
    setSearchValue(event.target.value);
    setSearchText(event.target.value);
  };

  return (
    <ErrorBoundary>
      <Box className={classes.searchWrapper}>
        <TextField
          variant="outlined"
          id="txtProjectSearch"
          className={classes.searchTextField}
          label="Project Search"
          onChange={handleTextChange}
          value={searchValue}
          InputProps={{
            endAdornment: (
              <InputAdornment position="end">
                <IconButton size="large">
                  <SearchIcon />
                </IconButton>
              </InputAdornment>
            ),
          }}
        />
        <Tooltip title="Refresh Projects">
          <Button
            className={classes.refreshButton}
            variant="contained"
            color="primary"
            size="medium"
            onClick={handleRefresh}
          >
            <RefreshIcon />
          </Button>
        </Tooltip>
      </Box>
    </ErrorBoundary>
  );
};

export default ProjectSearch;
