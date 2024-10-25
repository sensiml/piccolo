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

/* eslint-disable max-len */
import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";

import { generatePath, useHistory } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Backdrop, CircularProgress, IconButton, Tooltip, Snackbar } from "@mui/material";

import DeleteIcon from "@mui/icons-material/Delete";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import MoreHorizOutlinedIcon from "@mui/icons-material/MoreHorizOutlined";

import StandardTable from "components/StandardTable";
import ToastMessage from "components/ToastMessage/ToastMessage";
import PipelineExportMenu from "components/PipelineExportMenu";
import helper from "store/helper";

import { UIButtonResponsiveToShort } from "components/UIButtons";

import { ROUTES } from "routers";

import { DialogConfirm } from "components/DialogConfirm";
import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { TableLink } from "components/UILinks";
import { UITablePanel } from "components/UIPanels";
import useStyles from "./PipelinesTableStyles";

const PipelinesTable = ({
  onUpdateProjectAction,
  selectedProject,
  pipelines,
  knowledgepacks,
  loadKnowledgepacks,
  deletePipeline,
  loadPipelines,
  exportPipeline,
}) => {
  const { t } = useTranslation("pipelines");
  const classes = useStyles();
  const routersHistory = useHistory();

  const [pipelineList, setPipelineList] = useState([]);
  const [open, setOpen] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackBarMessage, setSnackBarMessage] = useState("");
  const [snackBarVariant, setSnackBarVariant] = useState("success");

  const [deletingPipeline, setDeletingPipeline] = useState(false);

  const [selectedItems, setSelectedItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState("");

  const [selectedPipelineName, setSelectedPipelineName] = React.useState(null);
  const [numOfKnowledgePacksOnPipeline, setNumOfKnowledgePacksOnPipeline] = useState(0);

  const [anchorExportMenu, setAnchorExportMenu] = useState(null);
  const [exportingPipleineUUID, setExportingPipleineUUID] = useState();
  const isOpenExportMenu = Boolean(anchorExportMenu);

  const deletingText = useMemo(() => {
    const modelCountsText = `${t("table.dialog-delete-model-counts-text", {
      modelCounts: numOfKnowledgePacksOnPipeline,
    })} `;
    const baseText = selectedItems?.length
      ? t("table.dialog-delete-multi-text", { count: selectedItems?.length })
      : t("table.dialog-delete-text", { selectedPipelineName });

    return `${numOfKnowledgePacksOnPipeline ? modelCountsText : ""}${baseText}`;
  }, [numOfKnowledgePacksOnPipeline, selectedPipelineName, selectedItems]);

  const isDisableToBulkUpdate = useMemo(() => {
    return _.isEmpty(selectedItems);
  }, [selectedItems]);

  const selectedItemList = useMemo(() => {
    // fileter defined values
    return _.union(selectedItems, [selectedItem]).filter((item) => item);
  }, [selectedItems, selectedItem]);

  const handlseSelectInTable = (pipelinesUUID) => {
    setSelectedItems(pipelinesUUID);
  };

  const handleAction = (pipelineUUID) => {
    routersHistory.push(
      generatePath(ROUTES.MAIN.MODEL_BUILD.child.AUTOML_BUILDER_SCREEN.path, {
        projectUUID: selectedProject,
        pipelineUUID,
      }),
      { isOptimizeAutoMLParams: true },
    );
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpenSnackbar(false);
  };

  const handleOpenConfirmDelete = (uuid, name, kpCount) => {
    setNumOfKnowledgePacksOnPipeline(kpCount);
    setSelectedPipelineName(name);
    setSelectedItem(uuid);
    setOpen(true);
  };

  const handleCloseConfirmDelete = () => {
    setSelectedItem("");
    setOpen(false);
  };

  const renderDate = (value) => {
    return helper.convertToLocalDateTime(value);
  };

  const openSnackBarWithMsg = (variant, message) => {
    setSnackBarMessage(message);
    setSnackBarVariant(variant);
    setOpenSnackbar(true);
  };

  const handleDeletePipeline = async () => {
    const deletedItems = [];
    setDeletingPipeline(true);
    // eslint-disable-next-line no-restricted-syntax
    for (const pipelineUUID of selectedItemList) {
      // eslint-disable-next-line no-await-in-loop
      const response = await deletePipeline(selectedProject, pipelineUUID);
      if (response.status !== "success") {
        openSnackBarWithMsg("error", response.details);
      } else {
        deletedItems.push(pipelineUUID);
      }
    }

    if (deletedItems.includes(selectedItem)) {
      setSelectedItem("");
    }
    if (!_.isEmpty(selectedItems)) {
      setSelectedItems(selectedItems.filter((item) => !deletedItems.includes(item)));
    }
    loadPipelines(selectedProject);
    loadKnowledgepacks(selectedProject);

    if (onUpdateProjectAction) {
      onUpdateProjectAction();
    }
    if (deletedItems?.length) {
      openSnackBarWithMsg(
        "success",
        `Successfully deleted the Pipeline ${selectedPipelineName || ""}.`,
      );
    }
    handleCloseConfirmDelete();
    setDeletingPipeline(false);
  };

  const handleExportPipelines = async (downloadType) => {
    if (exportingPipleineUUID) {
      try {
        await exportPipeline(selectedProject, exportingPipleineUUID, downloadType);
      } catch (error) {
        openSnackBarWithMsg("error", error.message);
      }
      return;
    }
    // eslint-disable-next-line no-restricted-syntax
    for (const itemUUID of selectedItemList) {
      try {
        // eslint-disable-next-line no-await-in-loop
        await exportPipeline(selectedProject, itemUUID, downloadType);
      } catch (error) {
        openSnackBarWithMsg("error", error.message);
      }
    }
  };

  const handleCloseExportMenu = () => {
    setAnchorExportMenu(null);
    if (exportingPipleineUUID) {
      setExportingPipleineUUID(null);
    }
  };

  const renderLinkOpenAction = (value, row) => {
    return (
      <TableLink
        color="primary"
        onClick={(_e) => handleAction(row.uuid)}
        tooltipTitle={`Open ${value}`}
      >
        {value}
      </TableLink>
    );
  };

  const renderRunning = (value) => {
    return (
      <div>
        {value === true ? (
          <Tooltip title="Pipeline currently executing.">
            <AccessTimeIcon variant="contained" color="primary" size="small" />
          </Tooltip>
        ) : (
          <div />
        )}
      </div>
    );
  };

  const rendeCPUTime = (value) => {
    return (
      <Tooltip title={t("table.tooltip-cpu-time")}>
        <div>{(value / 60).toFixed(1)}</div>
      </Tooltip>
    );
  };

  const renderDownload = (_pipelineUUID, row) => {
    const handleOpenMenu = (e) => {
      setAnchorExportMenu(e.currentTarget);
      setExportingPipleineUUID(_pipelineUUID);
    };
    return (
      <Tooltip title={t("table.tooltip-download")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          // href={`data:text/json;charset=utf-8,${encodeURIComponent(getPipelineJSON(row))}`}
          onClick={(e) => handleOpenMenu(e)}
          download={`${row.name}.json`}
        >
          <MoreHorizOutlinedIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderDelete = (value, row) => {
    return (
      <Tooltip title="Delete Pipeline">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          disabled={!isDisableToBulkUpdate}
          onClick={() => handleOpenConfirmDelete(value, row.name, row.kpCount)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const columns = [
    {
      title: "Name",
      field: "name",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      render: renderLinkOpenAction,
    },
    {
      title: "Knowledge Pack Count",
      field: "kpCount",
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Created Date",
      field: "created_at",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: renderDate,
    },
    {
      title: "Modified Date",
      field: "last_modified",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: renderDate,
    },
    {
      title: "UUID",
      field: "uuid",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: "Running",
      field: "active",
      sortable: true,
      render: renderRunning,
      filterable: true,
    },
    {
      title: "CPU Usage (Minutes)",
      field: "cpu_clock_time",
      sortable: true,
      render: rendeCPUTime,
      filterable: true,
    },
    { title: "Export", field: "uuid", render: renderDownload },
    { title: "Delete", field: "uuid", render: renderDelete },
  ];

  useEffect(() => {
    if (pipelines && pipelines.data && knowledgepacks && knowledgepacks.data) {
      pipelines.data.forEach((p) => {
        // TODO assign
        // eslint-disable-next-line no-param-reassign
        p.kpCount = knowledgepacks.data.filter((kp) => kp.sandbox_uuid === p.uuid).length;
      });
    }
    // Default Sort for Pipelnes is desc by last modified date
    // TODO assign
    // eslint-disable-next-line no-param-reassign
    pipelines.data = helper.sortObjects(pipelines.data || [{}], "last_modified", false, "dsc");
    setPipelineList(pipelines);
  }, [pipelines, knowledgepacks]);

  const options = {
    rowsPerPage: 25,
    rowsPerPageOptions: [5, 10, 25, 50, 100, "All"],
    showPagination: true,
    applyFilters: true,
    isDarkHeader: true,
    isShowSelection: true,
    selectionField: "uuid",
    onSelectInTable: handlseSelectInTable,
    noContentText: "No Pipelines",
  };
  return (
    <>
      <UITablePanel
        title={t("table.title")}
        onRefresh={() => loadPipelines(selectedProject)}
        ActionComponent={
          <>
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              onClick={() => handleOpenConfirmDelete()}
              ml={2}
              tooltip={t("Delete")}
              disabled={isDisableToBulkUpdate}
              text={t("Delete")}
              icon={<DeleteIcon />}
              className={classes.mr1}
            />
            <UIButtonResponsiveToShort
              color="primary"
              variant={"outlined"}
              icon={<CloudDownloadOutlinedIcon />}
              endIcon={<ArrowDropDownIcon />}
              onClick={(e) => setAnchorExportMenu(e.currentTarget)}
              disabled={isDisableToBulkUpdate}
              text={t("Export")}
            />
          </>
        }
      />
      <StandardTable
        tableId="pipelinesTable"
        tableColumns={columns}
        tableData={pipelineList}
        tableOptions={options}
      />
      <DialogConfirm
        isOpen={open}
        title={t("table.dialog-delete-title")}
        text={deletingText}
        onConfirm={handleDeletePipeline}
        onCancel={handleCloseConfirmDelete}
        cancelText={t("dialog-confirm-delete.cancel")}
        confirmText={t("dialog-confirm-delete.delete")}
        isLoading={deletingPipeline}
      />
      <Snackbar
        anchorOrigin={{
          vertical: "top",
          horizontal: "right",
        }}
        open={openSnackbar}
        autoHideDuration={2000}
        onClose={handleCloseSnackbar}
      >
        <ToastMessage
          onClose={handleCloseSnackbar}
          variant={snackBarVariant}
          message={snackBarMessage}
        />
      </Snackbar>
      <Backdrop className={classes.backdrop} open={deletingPipeline}>
        <CircularProgress size={100} />
      </Backdrop>
      <PipelineExportMenu
        archorEl={anchorExportMenu}
        isOpen={isOpenExportMenu}
        onClose={handleCloseExportMenu}
        onDownloadPipeline={handleExportPipelines}
      />
    </>
  );
};

export default PipelinesTable;
