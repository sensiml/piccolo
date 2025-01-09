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

import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";
import { useTranslation } from "react-i18next";
import { generatePath, useHistory } from "react-router-dom";

import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import CloudDownloadIcon from "@mui/icons-material/CloudDownload";
import ExploreIcon from "@mui/icons-material/Explore";
import PlaylistAddCheckIcon from "@mui/icons-material/PlaylistAddCheck";

import { Backdrop, CircularProgress, Tooltip, IconButton, Snackbar } from "@mui/material";

import StandardTable from "components/StandardTable";
import ToastMessage from "components/ToastMessage/ToastMessage";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { UITablePanel } from "components/UIPanels";
import { UIButtonResponsiveToShort } from "components/UIButtons";
import { DialogConfirm } from "components/DialogConfirm";

import helper from "store/helper";
import { ROUTES } from "routers";

import { DialogModelRename } from "components/DialogModel";
import { TableLink } from "components/UILinks";

import useStyles from "./KnowledgepacksTableStyles";

const KnowledgepacksTable = ({
  tableTitle,
  knowledgepacks,
  selectedProject,
  deleteModel,
  clearModel,
  loadKnowledgepacks,
  renameModel,
  openRouterRedirect,
  openTitle,
}) => {
  const { t } = useTranslation("models");

  const routersHistory = useHistory();

  const classes = useStyles();
  const [knowledgepacksList, setKnowledgepacksList] = useState([]);
  const [selectedKnowledgepackUuid, setSelectedKnowledgepackUuid] = useState(null);
  const [selectedSandboxUuid, setSelectedSandboxUuid] = useState(null);
  const [newKnowledgepackName, setNewKnowledgepackName] = useState(null);
  const [deletingKnowledgepackName, setDeletingKnowledgepackName] = useState(null);

  const [selectedItem, setSelectedItem] = useState(null);
  const [selectedItems, setSelectedItems] = useState([]);

  const [isUpdating, setIsUpdating] = useState(false);

  const [isOpenedDeleteConfirm, setIsOpenedDeleteConfirm] = useState(false);

  const [open, setOpen] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackBarMessage, setSnackBarMessage] = useState("");
  const [snackBarVariant, setSnackBarVariant] = useState("success");
  const [savingKnowledgepack, setSavingKnowledgepack] = useState(false);

  const deletingText = useMemo(() => {
    return !_.isEmpty(selectedItems)
      ? t("model-table.dialog-delete-multi-text", { count: selectedItems?.length })
      : t("model-table.dialog-delete-text", { name: deletingKnowledgepackName });
  }, [deletingKnowledgepackName, selectedItems]);

  const isDisableToBulkUpdate = useMemo(() => {
    return _.isEmpty(selectedItems);
  }, [selectedItems]);

  const selectedItemList = useMemo(() => {
    // fileter defined values
    return _.union(selectedItems, [selectedItem]).filter((item) => item);
  }, [selectedItems, selectedItem]);

  useEffect(() => {
    // Default Sort for KnowledgePacks is desc by created date
    // TODO CHANG Assign
    // eslint-disable-next-line no-param-reassign
    knowledgepacks.data = helper.sortObjects(
      knowledgepacks.data || [{}],
      "created_at",
      false,
      "dsc",
    );
    setKnowledgepacksList(knowledgepacks);
  }, [knowledgepacks]);

  const openSnackBarWithMsg = (variant, message) => {
    setSnackBarMessage(message);
    setSnackBarVariant(variant);
    setOpenSnackbar(true);
  };

  const handleRefresh = () => {
    loadKnowledgepacks(selectedProject);
  };

  const handleSelectInTable = (selectedUUIDs) => {
    setSelectedItems(selectedUUIDs);
  };

  const renderDate = (value) => {
    return helper.convertToLocalDateTime(value);
  };

  // eslint-disable-next-line no-confusing-arrow
  const handleAccuracyData = (data) =>
    !data || Number.isNaN(data) || data === "" ? data : `${Number(data).toFixed(2)} %`;

  const handleAction = (path, pipelineUUID, modelUUID) => {
    clearModel();
    routersHistory.push(
      generatePath(path, { projectUUID: selectedProject, pipelineUUID, modelUUID }),
    );
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpenSnackbar(false);
  };

  const handleRename = (event, uuid, currentname, sandboxUuid) => {
    setSelectedSandboxUuid(sandboxUuid);
    setSelectedKnowledgepackUuid(uuid);
    setNewKnowledgepackName(currentname);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleSave = async (kpsToRename) => {
    setSavingKnowledgepack(true);
    setOpen(false);
    try {
      const response = await renameModel(
        selectedProject,
        selectedSandboxUuid,
        selectedKnowledgepackUuid,
        kpsToRename,
      );
      if (response.status === "error") {
        openSnackBarWithMsg("warning", response.details);
        setSavingKnowledgepack(false);
        loadKnowledgepacks(selectedProject);
        return;
      }
    } catch (err) {
      openSnackBarWithMsg("error", err.message);
      setSavingKnowledgepack(false);
      return;
    }
    loadKnowledgepacks(selectedProject);
    openSnackBarWithMsg("success", "Successfully renamed the Knowledgepack.");
    setSavingKnowledgepack(false);
  };

  const handleOpenConfirmDelete = (modelUUID, name) => {
    setSelectedItem(modelUUID);
    setDeletingKnowledgepackName(name);
    setIsOpenedDeleteConfirm(true);
  };

  const handleCloseConfirmDelete = () => {
    setIsOpenedDeleteConfirm(false);
  };

  const handleDeleteModel = async () => {
    const deletedItems = [];
    setIsUpdating(true);

    // eslint-disable-next-line no-restricted-syntax
    for (const kpUUID of selectedItemList) {
      try {
        // eslint-disable-next-line no-await-in-loop
        await deleteModel(kpUUID);
        deletedItems.push(kpUUID);
      } catch (error) {
        openSnackBarWithMsg("error", error.message);
      }
    }
    if (deletedItems.includes(selectedItem)) {
      setSelectedItem("");
    }
    if (!_.isEmpty(selectedItems)) {
      setSelectedItems(selectedItems.filter((item) => !deletedItems.includes(item)));
    }
    if (deletedItems?.length) {
      openSnackBarWithMsg("success", t("model-table.msg-success-delete"));
    }
    setIsUpdating(false);
    handleCloseConfirmDelete();
    loadKnowledgepacks(selectedProject);
    setDeletingKnowledgepackName(null);
  };

  const renderLinkOpenAction = (value, row) => {
    const redirectPath = openRouterRedirect || ROUTES.MAIN.MODEL_EXPLORE.path;
    const title = openTitle || "Explore model";

    return (
      <TableLink
        color="primary"
        tooltipTitle={`${title}: ${value}`}
        onClick={() => handleAction(redirectPath, row.sandbox_uuid, row.uuid)}
      >
        {value}
      </TableLink>
    );
  };

  const customRenderTest = (value, row) => {
    return (
      <Tooltip title="Test Model">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleAction(ROUTES.MAIN.MODEL_TEST.path, row.sandbox_uuid, value)}
        >
          <PlaylistAddCheckIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const customRenderDownload = (value, row) => {
    return (
      <Tooltip title="Download Knowledge Pack">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleAction(ROUTES.MAIN.MODEL_DOWNLOAD.path, row.sandbox_uuid, value)}
        >
          <CloudDownloadIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const customRenderExplore = (value, row) => {
    return (
      <Tooltip title="Explore Model">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleAction(ROUTES.MAIN.MODEL_EXPLORE.path, row.sandbox_uuid, value)}
        >
          <ExploreIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const customRenderRename = (value, row) => {
    return (
      <Tooltip title="Rename Knowledgepack">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={(e) => handleRename(e, value, row.name, row.sandbox_uuid)}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const customRenderDelete = (modeUUID, row) => {
    return (
      <Tooltip title={t("model-table.tooltip-delete")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          disabled={!isDisableToBulkUpdate}
          onClick={(_e) => handleOpenConfirmDelete(modeUUID, row?.name)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const getDropDownLookup = (dataList, columnName) => {
    let lookupDict = null;

    if (!dataList || dataList.isFetching || !dataList.data || !dataList.data.length === 0) {
      return lookupDict;
    }

    lookupDict = {};
    // TODO assign
    // eslint-disable-next-line no-return-assign
    dataList.data.forEach((lv) => (lookupDict[lv[columnName]] = lv[columnName]));

    return lookupDict;
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
      title: "Classifier",
      field: "classifier_name",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      lookup: getDropDownLookup(knowledgepacksList, "classifier_name"),
    },
    {
      title: "Accuracy",
      field: "accuracy",
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
      render: handleAccuracyData,
    },
    {
      title: "Model Size (Bytes)",
      field: "model_size",
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Feature Count",
      field: "features_count",
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Pipeline",
      field: "sandbox_name",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      lookup: getDropDownLookup(knowledgepacksList, "sandbox_name"),
    },
    {
      title: "Created Date",
      field: "created_at",
      render: renderDate,
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
    },
    {
      title: "UUID",
      field: "uuid",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    { title: "Explore", field: "uuid", render: customRenderExplore },
    { title: "Test", field: "uuid", render: customRenderTest },
    { title: "Download", field: "uuid", render: customRenderDownload },
    { title: "Rename", field: "uuid", render: customRenderRename },
    { title: t("model-table.title-delete"), field: "uuid", render: customRenderDelete },
  ];

  const options = {
    rowsPerPage: 25,
    rowsPerPageOptions: [10, 25, 50, 100, "All"],
    showPagination: true,
    applyFilters: true,
    noContentText: "No Knowledge Packs",
    excludePrimaryFromDetails: true,
    isDarkHeader: true,
    selectionField: "uuid",
    isShowSelection: true,
    onSelectInTable: handleSelectInTable,
  };
  return (
    <>
      <UITablePanel
        title={tableTitle || t("model-table.title")}
        onRefresh={handleRefresh}
        ActionComponent={
          <>
            <UIButtonResponsiveToShort
              icon={<DeleteIcon />}
              variant="outlined"
              color="primary"
              disabled={isDisableToBulkUpdate}
              onClick={() => handleOpenConfirmDelete()}
              text={t("Delete")}
            />
          </>
        }
      />
      <StandardTable
        tableId="knowledgePackTable"
        tableColumns={columns}
        tableData={knowledgepacksList}
        tableOptions={options}
      />

      <DialogModelRename
        modelName={newKnowledgepackName}
        isOpen={open}
        onClose={handleClose}
        modelList={knowledgepacksList?.data || []}
        selectedModel={selectedKnowledgepackUuid}
        selectedPipeline={selectedSandboxUuid}
        onSave={handleSave}
      />

      <DialogConfirm
        isOpen={isOpenedDeleteConfirm}
        title={t("model-table.dialog-delete-title")}
        text={deletingText}
        isLoading={isUpdating}
        onConfirm={() => handleDeleteModel()}
        onCancel={() => handleCloseConfirmDelete()}
        cancelText={t("dialog-confirm-delete.cancel")}
        confirmText={t("dialog-confirm-delete.delete")}
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
      <Backdrop className={classes.backdrop} open={savingKnowledgepack}>
        <CircularProgress size={100} />
      </Backdrop>
    </>
  );
};

export default KnowledgepacksTable;
