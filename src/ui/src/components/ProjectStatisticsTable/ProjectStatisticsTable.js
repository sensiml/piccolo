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

/* eslint-disable object-shorthand */
/* eslint-disable no-useless-return */
/* eslint-disable no-param-reassign */
/* eslint-disable func-names */
/* eslint-disable camelcase */
/* eslint-disable no-use-before-define */
/* eslint-disable no-return-assign */
import React, { useState, useEffect, Fragment } from "react";
import _ from "lodash";
import Plot from "react-plotly.js";
import helper from "store/helper";

import CheckBoxOutlineBlankIcon from "@mui/icons-material/CheckBoxOutlineBlank";
import CheckBoxIcon from "@mui/icons-material/CheckBox";
import LibraryBooksIcon from "@mui/icons-material/LibraryBooks";
import TableChartIcon from "@mui/icons-material/TableChart";
import StopIcon from "@mui/icons-material/Stop";
import PlayArrowIcon from "@mui/icons-material/PlayArrow";

import { Button, IconButton, Tooltip, Typography } from "@mui/material";

import StandardTable from "components/StandardTable";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { UITablePanel } from "components/UIPanels";
import { UIButtonResponsiveToShort } from "components/UIButtons";

import useStyles from "./ProjectStatisticsTableStyles";
import CapturesContextMenu from "./CapturesContextMenu";

const dialLayout = {
  width: 55,
  height: 55,
  margin: { t: 0, b: 0, l: 0, r: 0 },
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
};
const dialData = {
  domain: { x: [0, 1], y: [0, 1] },
  value: 0,
  type: "indicator",
  mode: "gauge+number",
  gauge: { borderwidth: 0.2, axis: { visible: false, range: [0, 100] } },
};

const getMetDataColumnIfExists = (metaDataList, columnName) => {
  let lookupDict = null;

  if (!metaDataList) return lookupDict;

  const metaDataItem = metaDataList.find((m) => m.name === columnName);

  if (metaDataItem && metaDataItem.is_dropdown === true && metaDataItem.label_values) {
    lookupDict = {};
    metaDataItem.label_values.forEach((lv) => (lookupDict[lv.value] = lv.value));
  }

  return lookupDict;
};

const CAPTURE_UUID = "uuid";
const CAPTURE_NAME = "name";
const CAPTURES_HEADER = "Capture Files";
const CAPTURE_SELECTED = "captureSelected";
const HAS_BEEN_RUN = "captureHasBeenRun";
const ACCURACY = "accuracy";
const PIPELINE_ID = "pipelineId";
const MODEL_ID = "modelId";
const ACCURACY_NA = "NA";
const ACCURACY_EMPTY = "rgb(0,0,0)";
const ACCURACY_GOOD = "rgb(75,152,26)";
const ACCURACY_BAD = "rgb(230,70,70)";
const ACCURACY_EMPTY_TOOLTIP = "Capture does'nt have Ground Truth. Accuracy could not be computed";
const ACCURACY_LIMIT = 80;

const TABLE_HEADERS = {
  total_events: "Segments",
  file_size_mb: "Size(MB)",
};

const ProjectStatisticsTable = ({
  capturesStatistics,
  reRender,
  headerText,
  metadata,
  onRowSelectionAction,
  onRowsSelectionAction,
  showResultsAction,
  recognizingSignal,
  onRefresh,
  getResultFromcache,
  isInTestModel,
  selectedPipeline,
  selectedModel,
  activeSession,
  handleClassifierRun,
  handleComputeSummary,
  handleStopClassierRun,
  classiferIsRunning,
}) => {
  const classes = useStyles();
  const [filteredData, setFilteredData] = useState([]);
  const [openContextMenu, setOpenContextMenu] = useState(false);
  const [menuAnchor, setMenuAnchor] = useState(null);
  const [projectStatistics, setProjectStatistics] = useState([]);
  const [inTestModel, setInTestModel] = useState(false);
  const [dynamicColumns, setDynamicColumns] = useState([]);
  const [currentSession, setCurrentSession] = useState(activeSession);

  const setTableDataSet = (data) => {
    if (data) {
      setFilteredData(data.map((el) => el.uuid));
    }
  };

  const showCustomRowColor = (row, rowIndex, stClasses) => {
    if (!row[HAS_BEEN_RUN]) return "";
    if (!row[ACCURACY]) return stClasses.tableRowGrey;
    return row[ACCURACY] >= ACCURACY_LIMIT ? stClasses.tableRowGreen : stClasses.tableRowRed;
  };

  const handleRowSelection = (event, row) => {
    if (inTestModel === true) {
      if (
        event.target.id === "show_capture_results" ||
        (event.target.parentNode !== undefined &&
          event.target.parentNode.id === "show_capture_results")
      ) {
        return;
      }
      if (recognizingSignal() === true) return;
      updateCaptureSelection(row.uuid);
      onRowSelectionAction(event, row);
    }
  };

  const updateCaptureSelection = (captureUuid) => {
    if (projectStatistics && projectStatistics.data) {
      const selectedRow = projectStatistics.data.find((ps) => ps[CAPTURE_UUID] === captureUuid);
      if (selectedRow) {
        selectedRow[CAPTURE_SELECTED] = selectedRow[CAPTURE_SELECTED] === 1 ? 0 : 1;
      }
    }
  };

  const drawLabel = (column) => {
    return <Typography variant="button">{column.title.toUpperCase()}</Typography>;
  };

  const captureSelectionRender = (value, row) => {
    return getCaptureSelectionIcon(row[CAPTURE_SELECTED], row[CAPTURE_UUID]);
  };

  const captureCacheStatusRender = (value, row) => {
    return getCacheStatusButton(
      row[HAS_BEEN_RUN],
      row[PIPELINE_ID],
      row[MODEL_ID],
      row[CAPTURE_UUID],
    );
  };

  const getCacheStatusIcon = (statusId) => {
    return statusId === 1 ? (
      <Tooltip title={"Cached Capture Classifications"}>
        <IconButton variant="contained" color="primary" size="small">
          <LibraryBooksIcon color="primary" size="small" />
        </IconButton>
      </Tooltip>
    ) : null;
  };

  const getCacheStatusButton = (statusId, pipeline_id, model_id, capture_uuid) => {
    return statusId === 1 ? (
      <Tooltip title={"Click here to show results"}>
        <Button
          size="small"
          id={`show_capture_results`}
          variant="contained"
          color="primary"
          startIcon={<LibraryBooksIcon />}
          onClick={(_e) => {
            showResultsAction(pipeline_id, model_id, capture_uuid);
          }}
        >
          Results
        </Button>
      </Tooltip>
    ) : null;
  };
  const getCaptureSelectionIcon = (statusId, captureuuid) => {
    return statusId === 1 ? (
      <Tooltip title={captureuuid ? "Capture Is Selected" : "Captures Selected"}>
        <IconButton variant="contained" color="primary" size="small">
          <CheckBoxIcon color="primary" captureuuid={captureuuid} />
        </IconButton>
      </Tooltip>
    ) : (
      <Tooltip title={captureuuid ? "Click to Select Capture" : "Captures Not Selected"}>
        <IconButton variant="contained" color="primary" size="small">
          <CheckBoxOutlineBlankIcon color="disabled" captureuuid={captureuuid} />
        </IconButton>
      </Tooltip>
    );
  };

  const changeTableSelection = (event, isSelect) => {
    setProjectStatistics((pevObj) => {
      const data = pevObj.data.map((obj) => ({
        ...obj,
        [CAPTURE_SELECTED]: isSelect ? (filteredData.includes(obj.uuid) ? 1 : 0) : 0,
      }));
      onRowsSelectionAction(event, data);
      return { isFetching: false, data };
    });
  };

  const contextMenuActions = {
    unSelectAllInTable: function (event) {
      changeTableSelection(event, false);
    },

    selectAllInTable: function (event) {
      changeTableSelection(event, true);
    },
  };

  useEffect(() => {
    updateFileRunStatus();
  }, [reRender]);

  const updateFileRunStatus = () => {
    if (isInTestModel && projectStatistics && projectStatistics.data) {
      const ps = projectStatistics;
      ps.data.forEach((p) => {
        const cachedResult = getResultFromcache(p[CAPTURE_UUID]);
        p[PIPELINE_ID] = selectedPipeline;
        p[MODEL_ID] = selectedModel;
        p[HAS_BEEN_RUN] = cachedResult ? 1 : 0;
        p[ACCURACY] = cachedResult ? cachedResult.accuracy[currentSession] : null;
      });
      setProjectStatistics(ps);
    }
  };

  const accuracyDialRender = (value, row) => {
    if (!row[HAS_BEEN_RUN]) return null;
    const chartData = { ...dialData, value: row[ACCURACY] || ACCURACY_NA };
    let barColor = ACCURACY_EMPTY;
    let toolTip = ACCURACY_EMPTY_TOOLTIP;
    if (row[ACCURACY]) {
      barColor = parseInt(row[ACCURACY], 10) >= ACCURACY_LIMIT ? ACCURACY_GOOD : ACCURACY_BAD;
      toolTip = `${row[ACCURACY]} %`;
    }
    chartData.gauge = {
      ...chartData.gauge,
      bar: { color: barColor, thickness: 1 },
    };
    return (
      <Tooltip title={toolTip}>
        <div>
          <Plot
            data={[chartData]}
            layout={dialLayout}
            useResizeHandler={true}
            config={{ displayModeBar: false, responsive: true }}
          />
        </div>
      </Tooltip>
    );
  };

  useEffect(() => {
    const columns = dynamicColumns;
    setCurrentSession(activeSession);
    const addColumnIfNotExits = (newCol, prepend = false) => {
      if (columns.filter((c) => c.field === newCol.field).length !== 0) return;
      if (prepend) columns.unshift(newCol);
      else columns.push(newCol);
    };

    let ps = [];
    const dynaCols = [HAS_BEEN_RUN, ACCURACY, CAPTURE_SELECTED];
    if (capturesStatistics && capturesStatistics.data && capturesStatistics.data.length > 0) {
      ps = capturesStatistics.data;
      const keys = _.keys(ps[0]);
      [
        "name",
        "uuid",
        "total_events",
        "file_size_mb",
        "created",
        "capture_uuid",
        "capture_configuration_uuid",
        ...keys,
      ].forEach(function (key) {
        if (!["Id", PIPELINE_ID, MODEL_ID].includes(key)) {
          // Add Accuraacy in place of Capture UUID for Test Model
          if (isInTestModel === true && key === CAPTURE_UUID) {
            addColumnIfNotExits({
              title: "Accuracy",
              field: ACCURACY,
              sortable: true,
              type: ColumnType.Numeric,
              filterable: true,
              filterHasIcons: true,
              renderLabel: drawLabel,
              render: accuracyDialRender,
            });
            return;
          }

          // Add remaining columns
          if (!dynaCols.includes(key)) {
            const colDefinition = {
              title: TABLE_HEADERS[key] || key,
              field: key,
              primary: key === CAPTURE_NAME,
              sortable: true,
              type:
                helper.isNumber(ps[0][key]) || key === "file_size_mb"
                  ? ColumnType.Numeric
                  : ColumnType.Text,
              filterable: true,
              renderLabel: drawLabel,
            };

            const lookupList = getMetDataColumnIfExists(metadata, key);
            if (lookupList) colDefinition.lookup = lookupList;

            addColumnIfNotExits(colDefinition);
          }

          // Add the Capture UUID and Results Columns after the Total Events count for test model
          if (isInTestModel === true && key === "file_size_mb") {
            addColumnIfNotExits({
              title: "Results",
              field: HAS_BEEN_RUN,
              sortable: true,
              type: ColumnType.Numeric,
              filterable: true,
              filterHasIcons: true,
              lookup: {
                0: "",
                1: getCacheStatusIcon(1),
              },
              renderLabel: drawLabel,
              render: captureCacheStatusRender,
            });
          }
        }
      });
    }
    if (isInTestModel === true) {
      addColumnIfNotExits(
        {
          title: " ",
          field: CAPTURE_SELECTED,
          sortable: true,
          type: ColumnType.Numeric,
          filterable: true,
          filterHasIcons: true,
          lookup: {
            0: "Unselected",
            1: "Selected",
          },
          renderLabel: drawLabel,
          render: captureSelectionRender,
        },
        true,
      );
    }
    if (isInTestModel && _.isArray(ps)) {
      ps.forEach((p) => {
        const cachedResult = getResultFromcache(p[CAPTURE_UUID]);
        p[PIPELINE_ID] = selectedPipeline;
        p[MODEL_ID] = selectedModel;
        p[CAPTURE_SELECTED] = 0;
        p[HAS_BEEN_RUN] = cachedResult ? 1 : 0;
        p[ACCURACY] = cachedResult ? cachedResult.accuracy[activeSession] : 0;
      });
    }
    setProjectStatistics({
      data: ps,
      isFetching: capturesStatistics.isFetching,
    });
    setTableDataSet(ps);
    setDynamicColumns(columns);
  }, [capturesStatistics, activeSession, metadata]);

  useEffect(() => {
    setInTestModel(isInTestModel);
  }, [isInTestModel]);

  useEffect(() => {
    updateFileRunStatus();
  }, [selectedModel, selectedPipeline]);

  const title = headerText || "";

  const openMenu = (event) => {
    setOpenContextMenu(true);
    setMenuAnchor(event.currentTarget);
  };

  const closeMenu = (_event) => {
    setOpenContextMenu(false);
  };

  const options = {
    rowsPerPage: 10,
    showPagination: true,
    noContentText: `No ${headerText || CAPTURES_HEADER}`,
    excludePrimaryFromDetails: true,
    onRowSelection: handleRowSelection,
    rowsPerPageOptions: [5, 10, 25, 50, 100, "All"],
    applyFilters: true,
    getCustomRowProps: isInTestModel ? showCustomRowColor : null,
    contextMenuAction: isInTestModel ? openMenu : null,
    captureTableData: setTableDataSet,
    isDarkHeader: true,
  };

  return (
    <>
      <UITablePanel
        title={title}
        onRefresh={onRefresh}
        ActionComponent={
          <>
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              className={classes.mr1}
              disabled={classiferIsRunning}
              onClick={() => handleClassifierRun()}
              tooltip={"Test the model against the File Data using Emulation"}
              text={"Recognize"}
              icon={<PlayArrowIcon />}
            />
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              className={classes.mr1}
              disabled={classiferIsRunning}
              onClick={() => handleComputeSummary()}
              tooltip={"Summarize the Results across all selected Files"}
              text={"Summarize"}
              icon={<TableChartIcon />}
            />
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              disabled={false}
              onClick={() => handleStopClassierRun}
              tooltip={"Stop The Currently Executing Test"}
              text={"Stop"}
              icon={<StopIcon />}
              className={classes.mr1}
            />
          </>
        }
      />
      <StandardTable
        tableId="projectStatisticsTable"
        tableColumns={dynamicColumns}
        tableData={projectStatistics}
        tableOptions={options}
      />
      <CapturesContextMenu
        closeAction={closeMenu}
        openMenu={openContextMenu}
        menuActions={contextMenuActions}
        anchor={menuAnchor}
      />
    </>
  );
};

export default ProjectStatisticsTable;
