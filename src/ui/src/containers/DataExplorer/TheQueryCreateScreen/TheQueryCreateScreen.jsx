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

import React, { useState, useEffect, useRef } from "react";
import SaveIcon from "@mui/icons-material/Save";

import { useParams, useHistory, generatePath } from "react-router-dom";
import { ROUTES } from "routers";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import { Box, Button, FormControl, Grid, Paper, Tooltip } from "@mui/material";
import helper from "store/helper";

import QueryFilter from "components/QueryFilter";
import ErrorBoundary from "components/ErrorBoundary";
import ControlPanel from "components/ControlPanel";
import SelectForm from "components/FormElements/SelectForm";
import SelectMultiChip from "components/FormElements/SelectMultiChip";
import TextFieldForm from "components/FormElements/TextFieldForm";

import { UIButtonResponsiveToShort } from "components/UIButtons";
import { useMainContext } from "hooks";

import useStyles from "./TheQueryCreateScreenStyles";

const TheQueryCreateScreen = ({
  selectedProject,
  queries,
  sessions,
  labels,
  metadata,
  sources,
  // actions
  addOrUpdateQuery,
  setHasUnsavedChanges,
}) => {
  const { projectUUID } = useParams();
  const routersHistory = useHistory();
  const classes = useStyles();
  const emptyQuery = {
    query: "",
    name: "",
    session: "",
    label: "",
    metadata: ["segment_uuid"],
    source: [],
    plot: "",
  };

  const newQueryNameRef = useRef();
  // TODO should be refactored with redux action
  const [DataExplorer, setDataExplorer] = useState(emptyQuery);
  const [metadataList, setMetadataList] = useState([]);
  const { showMessageSnackbar } = useMainContext();

  const setUnSavedStatus = (status) => {
    setHasUnsavedChanges(status);
  };

  const handleChange = (_name, _value) => {
    const isDirty = DataExplorer[_name] !== _value;
    setDataExplorer({ ...DataExplorer, [_name]: _value });
    setUnSavedStatus(isDirty);
  };

  const handleQueryFilterChange = (queryFilter) => {
    const isDirty = DataExplorer.metadata_filter !== queryFilter;
    setDataExplorer({
      ...DataExplorer,
      metadata_filter: queryFilter || "",
    });
    setUnSavedStatus(isDirty);
  };

  const handleSave = async () => {
    if (!selectedProject) {
      showMessageSnackbar("error", "Project has to be selected to create a query.");
      return;
    }

    if (!DataExplorer.name || DataExplorer.name.trim() === "") {
      showMessageSnackbar("error", "Please enter a name for the query.");
      return;
    }
    if (
      queries &&
      queries.filter((e) => e.name.trim().toUpperCase() === DataExplorer.name.trim().toUpperCase())
        .length > 0
    ) {
      showMessageSnackbar(
        "error",
        `Query with the name '${DataExplorer.name}' already exists. Please enter a new name.`,
      );
      return;
    }

    if (!DataExplorer.session) {
      showMessageSnackbar("error", "Session is required to create a query.");
      return;
    }

    if (!DataExplorer.label) {
      showMessageSnackbar("error", "Label is required to create a query.");
      return;
    }

    if (!DataExplorer.source || DataExplorer.source.length === 0) {
      showMessageSnackbar("error", "Source columns are required to create a query.");
      return;
    }

    if (!DataExplorer.metadata || DataExplorer.metadata.length === 0) {
      showMessageSnackbar("error", "Metadata are required to create a query.");
      return;
    }

    setUnSavedStatus(false);

    addOrUpdateQuery(
      projectUUID,
      DataExplorer.query,
      DataExplorer.name,
      DataExplorer.source,
      DataExplorer.metadata,
      DataExplorer.session,
      DataExplorer.metadata_filter,
      DataExplorer.label,
    )
      .then((status) => {
        if (status.isSuccessFull) {
          routersHistory.push({
            pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_DETAILS_SCREEN.path, {
              projectUUID: selectedProject,
              queryUUID: status.newUuid,
            }),
          });
        } else {
          showMessageSnackbar("error", status.errorMessage);
        }
      })
      .catch((response) => {
        const errMsg =
          response.error.response.status === 403
            ? "Your account does not have permission to create or save a Query."
            : response.error;
        showMessageSnackbar("error", errMsg);
      });
  };

  useEffect(() => {
    setDataExplorer({ ...emptyQuery });
  }, [selectedProject]);

  useEffect(() => {
    if (metadata.filter((m) => m.name === "capture_uuid").length === 0) {
      metadata.push({ name: "capture_uuid" });
    }

    if (metadata.filter((m) => m.name === "segment_uuid").length === 0) {
      metadata.push({ name: "segment_uuid" });
    }
    setMetadataList(helper.sortObjects(metadata, "name", true));
  }, [metadata]);

  const handleCancelCreateQuery = () => {
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path, { projectUUID }),
    });
  };

  return (
    <ErrorBoundary>
      <Box mb={2}>
        <ControlPanel
          title={"Create Query"}
          onClickBack={handleCancelCreateQuery}
          truncateLength={35}
          leftColumns={4}
          rightColumns={8}
          actionsBtns={
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              text="CANCEL"
              tooltip="CANCEL"
              onClick={handleCancelCreateQuery}
              icon={<ExitToAppIcon />}
            />
          }
        />
      </Box>
      <Grid container spacing={2} justifyContent="flex-start">
        <Grid item xs={12} lg={7} xl={6}>
          <Paper elevation={0}>
            <Box p={2}>
              <Box mb={2}>
                <TextFieldForm
                  label="Query Name"
                  id="queryInput"
                  name="name"
                  inputRef={newQueryNameRef}
                  isObserveDefaultValue={true}
                  isUpdateWithDefault={false}
                  onChange={handleChange}
                />
              </Box>

              <Box mb={2}>
                <SelectForm
                  id="sessions"
                  labelId="sessionsLabel"
                  name="session"
                  label="Session"
                  onChange={handleChange}
                  isUpdateWithDefault={false}
                  isObserveDefaultValue={true}
                  defaultValue={DataExplorer.session}
                  options={
                    sessions &&
                    sessions
                      .filter((l) => l.name !== "SegmentID")
                      .map((session) => ({ name: session.name, value: session.id }))
                  }
                />
              </Box>

              <Box mb={2}>
                <SelectForm
                  id="labelsList"
                  labelId="labels"
                  name="label"
                  label="Label"
                  onChange={handleChange}
                  isUpdateWithDefault={false}
                  isObserveDefaultValue={true}
                  defaultValue={DataExplorer.label}
                  options={
                    labels &&
                    labels
                      .filter((l) => l.name !== "SegmentID")
                      .map((label) => ({ name: label.name, value: label.name }))
                  }
                />
              </Box>

              <Box mb={2}>
                <SelectMultiChip
                  id="metadataList"
                  labelId="metadataLabelId"
                  name="metadata"
                  label="Metadata"
                  isUpdateWithDefault={false}
                  isObserveDefaultValue={true}
                  defaultValue={DataExplorer.metadata || []}
                  options={
                    metadataList && metadataList.map((m) => ({ name: m.name, value: m.name }))
                  }
                  onChange={handleChange}
                  disabledOptions={["segment_uuid"]}
                />
              </Box>

              <Box mb={2}>
                <SelectMultiChip
                  id="sourcesList"
                  labelId="sourcesListId"
                  name="source"
                  label="Source"
                  isUpdateWithDefault={false}
                  isObserveDefaultValue={true}
                  defaultValue={DataExplorer.source || []}
                  options={sources && sources.map((source) => ({ name: source, value: source }))}
                  onChange={handleChange}
                />
              </Box>

              <Box mb={2}>
                <QueryFilter
                  value={DataExplorer.metadata_filter || ""}
                  onChange={handleQueryFilterChange}
                  queryMetada={DataExplorer.metadata}
                  queryLabel={DataExplorer.label}
                  isDisabled={true}
                />
              </Box>
              <FormControl fullWidth={true} className={classes.formControl}>
                <Box className={classes.buttonWrapper}>
                  <FormControl fullWidth={true}>
                    <Tooltip title="Save">
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                        startIcon={<SaveIcon />}
                      >
                        Save
                      </Button>
                    </Tooltip>
                  </FormControl>
                </Box>
              </FormControl>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </ErrorBoundary>
  );
};

export default TheQueryCreateScreen;
