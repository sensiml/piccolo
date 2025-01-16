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

import React, { useState, useEffect, useMemo, useCallback } from "react";
import _ from "lodash";

import SaveIcon from "@mui/icons-material/Save";
import CancelIcon from "@mui/icons-material/Cancel";
import { useParams, useHistory, generatePath } from "react-router-dom";
import { ROUTES } from "routers";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";
import { Box, Button, FormControl, Grid, Paper, Tooltip } from "@mui/material";
import helper from "store/helper";
import QueryStatisticsChart from "components/QueryStatisticsChart";
import QuerySegmentChart from "components/QuerySegmentChart";
import QueryFilter from "components/QueryFilter";
import ErrorBoundary from "components/ErrorBoundary";
import QueryCacheAlert from "components/QueryCacheAlert";
import ControlPanel from "components/ControlPanel";
import SelectForm from "components/FormElements/SelectForm";
import SelectMultiChip from "components/FormElements/SelectMultiChip";

import { useWindowResize, useMainContext } from "hooks";

import { RESPONSIVE } from "consts";
import { UIButtonConvertibleToShort } from "components/UIButtons";

import { AppLoader } from "components/UILoaders";

import useStyles from "./TheQueryDetailScreenStyles";

const TheQueryDetailScreen = ({
  selectedProject,
  selectedQuery,
  queryCacheStatusData,
  queries,
  sessions,
  labels,
  metadata,
  sources,
  queryDetails,
  hasUnsavedChanges,
  selectLabelValuesColors,
  // actions
  loadQuery,
  setSelectedQuery,
  setPlot,
  buildQueryCache,
  clearQueryCacheStatus,
  addOrUpdateQuery,
  loadQueries,
  setHasUnsavedChanges,
  resetFeatureStats,
  onShowInformation,
}) => {
  const { projectUUID } = useParams();
  const { queryUUID } = useParams();
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

  // TODO should be refactored with redux action
  const [DataExplorer, setDataExplorer] = useState(
    queryDetails && queryDetails.data && queryDetails.data.length > 0
      ? queryDetails.data
      : emptyQuery,
  );
  const [loadingQueryData, setLoadingQueryData] = useState(false);
  const [metadataList, setMetadataList] = useState([]);

  const [isShortBtnText, setIsShortBtnText] = useState(false);
  const { showMessageSnackbar } = useMainContext();

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < RESPONSIVE.WIDTH_FOR_SHORT_TEXT);
  });

  const reportError = (message) => {
    setLoadingQueryData(false);
    showMessageSnackbar("error", message);
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path, {
        projectUUID: selectedProject,
      }),
    });
  };

  const loadQueryAndSetState = async () => {
    resetFeatureStats();

    loadQuery(projectUUID, queryUUID)
      .then((status) => {
        if (status.isSuccessFull === false && !helper.isNullOrEmpty(status.errorMessage)) {
          reportError(status.errorMessage);
        }
        setPlot("segment");
      })
      .catch((error) => {
        if (error) reportError(error.error.message);
      });
  };

  const setUnSavedStatus = (status) => {
    setHasUnsavedChanges(status);
  };

  const handleClickCancel = () => {
    if (DataExplorer && DataExplorer.query && DataExplorer.query !== "") {
      loadQueryAndSetState(DataExplorer.query);
    } else if (queries && queries.length > 0) {
      loadQueryAndSetState(queries[0].uuid);
    } else {
      setDataExplorer(emptyQuery);
    }
    setUnSavedStatus(false);
    showMessageSnackbar("warning", "Your changes have been reverted.");
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

    if (!DataExplorer.session) {
      showMessageSnackbar("error", "Session is required to create a query.");
      return;
    }

    if (!DataExplorer.label) {
      showMessageSnackbar("error", "Label is required to create a query.");
      return;
    }

    if (
      !DataExplorer.source ||
      DataExplorer.source.length === 0 ||
      !DataExplorer.metadata ||
      DataExplorer.metadata.length === 0
    ) {
      showMessageSnackbar("error", "Metadata and source columns are required to create a query.");
      return;
    }

    setLoadingQueryData(true);
    resetFeatureStats();
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
          setLoadingQueryData(false);
          showMessageSnackbar("success", `Query '${DataExplorer.name}' saved successfully.`);
          setUnSavedStatus(false);
        } else {
          reportError(status.errorMessage);
        }
      })
      .catch((response) => {
        setDataExplorer({
          ...DataExplorer,
          query: helper.isNullOrEmpty(DataExplorer.query)
            ? selectedQuery || ""
            : DataExplorer.query,
        });
        setLoadingQueryData(false);
        const errMsg =
          response.error.response.status === 403
            ? "Your account does not have permission to create or save a Query."
            : response.error;
        showMessageSnackbar("error", errMsg);
      });
  };

  const handleBuildCache = () => {
    buildQueryCache(projectUUID, queryUUID);
  };

  const chartLabelColors = useMemo(() => {
    const colors = selectLabelValuesColors(DataExplorer.label);
    return _.keys(DataExplorer.segment_statistics).map((labelName) => {
      return colors[labelName] || "";
    });
  }, [DataExplorer, labels]);

  const chartLabelStatisticColors = useCallback(
    (chartType = "segmentsCharts") => {
      const colors = selectLabelValuesColors(DataExplorer.label);
      return _.keys(DataExplorer[chartType]).map((labelName) => {
        return colors[labelName] || "";
      });
    },
    [DataExplorer, labels],
  );

  useEffect(() => {
    if (projectUUID !== selectedProject) {
      loadQueries(projectUUID);
    }
  }, []);

  useEffect(() => {
    setLoadingQueryData(queryDetails.isFetching);
    if (queryDetails && queryDetails.data && queryDetails.data.name === "") return;
    setDataExplorer({ ...queryDetails.data });
    setLoadingQueryData(queryDetails.isFetching);
    setUnSavedStatus(false);
  }, [queryDetails]);

  useEffect(() => {
    setDataExplorer({ ...emptyQuery });
  }, [selectedProject]);

  useEffect(() => {
    setSelectedQuery(queryUUID);
    loadQueryAndSetState(queryUUID);
    return () => clearQueryCacheStatus();
  }, []);

  useEffect(() => {
    if (metadata.filter((m) => m.name === "capture_uuid").length === 0) {
      metadata.push({ name: "capture_uuid" });
    }

    if (metadata.filter((m) => m.name === "segment_uuid").length === 0) {
      metadata.push({ name: "segment_uuid" });
    }
    setMetadataList(helper.sortObjects(metadata, "name", true));
  }, [metadata]);

  const handleChangeQueries = () => {
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_SCREEN.path, { projectUUID }),
    });
  };

  return (
    <ErrorBoundary>
      <Box mb={2}>
        <ControlPanel
          title={`Name: ${DataExplorer.name}`}
          onClickBack={isShortBtnText ? null : handleChangeQueries}
          truncateLength={
            isShortBtnText
              ? RESPONSIVE.TRUNCATE_NAME_OVER_SHORT_TEXT
              : RESPONSIVE.TRUNCATE_NAME_OVER
          }
          onShowInformation={onShowInformation}
          leftColumns={4}
          rightColumns={8}
          actionsBtns={
            <>
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                onClick={() => handleChangeQueries()}
                isShort={isShortBtnText}
                tooltip={"Change Query"}
                text={"Change Query"}
                icon={<ArrowBackIcon />}
              />
            </>
          }
        />
      </Box>

      <Grid container spacing={2}>
        <Grid item xs={12} lg={6} xl={6}>
          <Paper elevation={0}>
            <Box p={2} className={classes.queryBox}>
              <Box mb={2}>
                <QueryCacheAlert
                  queryData={DataExplorer}
                  isNewQuery={false}
                  selectedQuery={queryUUID}
                  queryCacheStatusData={queryCacheStatusData || {}}
                  loadQuery={() => loadQuery(projectUUID, queryUUID)}
                  onBuildCache={handleBuildCache}
                />
              </Box>
              <Box className={classes.queryForms}>
                <Box mb={2}>
                  <SelectForm
                    id="sessionsList"
                    labelId="sessions"
                    name="session"
                    label="Session"
                    onChange={handleChange}
                    isUpdateWithDefault={false}
                    isObserveDefaultValue={true}
                    defaultValue={DataExplorer.session}
                    options={
                      sessions &&
                      sessions.map((session) => ({ name: session.name, value: session.id }))
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
              </Box>
              <FormControl fullWidth={true} className={classes.formControlButtons}>
                <Box className={classes.buttonWrapper}>
                  <FormControl fullWidth={true}>
                    <Tooltip title="Save Changes">
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={handleSave}
                        startIcon={<SaveIcon />}
                        disabled={!hasUnsavedChanges}
                      >
                        Save Changes
                      </Button>
                    </Tooltip>
                  </FormControl>

                  <FormControl fullWidth={true}>
                    <Tooltip title="Cancel Changes">
                      <Button
                        variant="contained"
                        color="primary"
                        onClick={handleClickCancel}
                        startIcon={<CancelIcon />}
                        disabled={!hasUnsavedChanges}
                      >
                        Cancel
                      </Button>
                    </Tooltip>
                  </FormControl>
                </Box>
              </FormControl>
              <AppLoader isOpen={loadingQueryData} />
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} lg={6} xl={6}>
          <Paper elevation={0}>
            <Box p={2} className={classes.queryBox}>
              <ErrorBoundary>
                <QuerySegmentChart queryData={DataExplorer} chartLabelColors={chartLabelColors} />
              </ErrorBoundary>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} xl={6}>
          <Paper elevation={0}>
            <Box>
              <Box className={classes.chartGrid}>
                <ErrorBoundary>
                  <QueryStatisticsChart
                    queryData={DataExplorer}
                    selectedPlotType="segment"
                    chartLabelColors={chartLabelStatisticColors("segmentsCharts")}
                  />
                </ErrorBoundary>
              </Box>
            </Box>
          </Paper>
        </Grid>
        <Grid item xs={12} xl={6}>
          <Paper elevation={0}>
            <Box>
              <Box className={classes.chartGrid}>
                <ErrorBoundary>
                  <QueryStatisticsChart
                    queryData={DataExplorer}
                    selectedPlotType="samples"
                    chartLabelColors={chartLabelStatisticColors("samplesCharts")}
                  />
                </ErrorBoundary>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </ErrorBoundary>
  );
};

export default TheQueryDetailScreen;
