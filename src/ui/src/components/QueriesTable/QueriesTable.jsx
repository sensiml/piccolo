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

/* eslint-disable no-use-before-define */
/* eslint-disable no-param-reassign */
import React, { useState, useEffect, useMemo } from "react";
import _ from "lodash";
import { useTranslation } from "react-i18next";

import { generatePath, useHistory } from "react-router-dom";
import { Backdrop, CircularProgress, IconButton, Snackbar, Tooltip } from "@mui/material";

import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import AutorenewIcon from "@mui/icons-material/Autorenew";
import StandardTable from "components/StandardTable";
import ToastMessage from "components/ToastMessage/ToastMessage";
import QueryCacheStatus from "components/QueryCacheStatus";
import helper from "store/helper";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { DialogConfirm } from "components/DialogConfirm";
import { TableLink } from "components/UILinks";

import { ROUTES } from "routers";
import { useInterval } from "hooks";
import { CACHE_STATUSES } from "store/queries/const";
import { UITablePanel } from "components/UIPanels";

import { UIButtonResponsiveToShort } from "components/UIButtons";

import useStyles from "./QueriesTableStyles";

const QueriesTable = ({
  onUpdateProjectAction,
  queries,
  selectedProject,
  queryCacheStatusData,
  // actions
  loadQueries,
  deleteQuery,
  setSelectedQuery,
  buildQueryCache,
  loadQueryCacheStatus,
  clearQueryCacheStatus,
}) => {
  const { t } = useTranslation("queries");
  const classes = useStyles();
  const routersHistory = useHistory();

  const [queryList, setQueryList] = useState([]);
  const [open, setOpen] = useState(false);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [snackBarMessage, setSnackBarMessage] = useState("");
  const [snackBarVariant, setSnackBarVariant] = useState("success");
  const [deletingQuery, setDeletingQuery] = useState(false);

  const [selectedItems, setSelectedItems] = useState([]);
  const [selectedItem, setSelectedItem] = useState("");

  const [selectedQueryName, setSelectedQueryName] = useState(null);

  const [queryCacheBuildingUUID, setIsQueryCacheBuildingUUID] = useState("");

  const deletingText = useMemo(() => {
    return selectedItems?.length
      ? t("table.dialog-delete-multi-text", { count: selectedItems?.length })
      : t("table.dialog-delete-text", { selectedQueryName });
  }, [selectedQueryName, selectedItems]);

  const isDisableToBulkUpdate = useMemo(() => {
    return _.isEmpty(selectedItems);
  }, [selectedItems]);

  const selectedItemList = useMemo(() => {
    // fileter defined values
    return _.union(selectedItems, [selectedItem]).filter((item) => item);
  }, [selectedItems, selectedItem]);

  useEffect(() => {
    if (queries.data && queries.data.length > 0) {
      queries.data.forEach((query) => {
        query.columnList = query.columns.join(" ");
        query.query_segments =
          query?.summary_statistics == null ? "" : query.summary_statistics.total_segments;
      });
    }
    // Default Sort for Queries is desc by last modified date
    if (!queryCacheBuildingUUID) {
      queries.data = helper.sortObjects(queries.data || [{}], "last_modified_at", false, "dsc");
    }
    setQueryList(queries);
  }, [queries]);

  useInterval(
    async () => {
      await loadQueryCacheStatus(selectedProject, queryCacheBuildingUUID);
    },
    queryCacheBuildingUUID ? 5000 : null,
  );

  useEffect(() => {
    if (
      queryCacheStatusData.build_status !== undefined &&
      queryCacheStatusData.build_status !== CACHE_STATUSES.BUILDING &&
      queryCacheStatusData.build_status !== CACHE_STATUSES.NOT_BUILT
    ) {
      setIsQueryCacheBuildingUUID("");
      loadQueries(selectedProject);
    }
  }, [queryCacheStatusData]);

  useEffect(() => {
    loadQueries(selectedProject);
    return () => clearQueryCacheStatus();
  }, []);

  const handlseSelectInTable = (pipelinesUUID) => {
    setSelectedItems(pipelinesUUID);
  };

  const handleAction = (event, queryUuid) => {
    setSelectedQuery(queryUuid);
    routersHistory.push(
      generatePath(ROUTES.MAIN.DATA_EXPLORER.child.QUERY_DETAILS_SCREEN.path, {
        projectUUID: selectedProject,
        queryUUID: queryUuid,
      }),
    );
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setOpenSnackbar(false);
  };

  const handleOpenConfirmDelete = (_event, uuid, name) => {
    setSelectedQueryName(name);
    setSelectedItem(uuid);
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleDeleteQuery = async () => {
    const deletedItems = [];
    setDeletingQuery(true);
    setOpen(false);
    // eslint-disable-next-line no-restricted-syntax
    for (const queryUUID of selectedItemList) {
      // eslint-disable-next-line no-await-in-loop
      const response = await deleteQuery(selectedProject, queryUUID);
      if (response.status === "error") {
        openSnackBarWithMsg("error", response.details);
        setDeletingQuery(false);
      } else {
        deletedItems.push(queryUUID);
      }
    }
    if (deletedItems.includes(selectedItem)) {
      setSelectedItem("");
    }
    if (!_.isEmpty(selectedItems)) {
      setSelectedItems(selectedItems.filter((item) => !deletedItems.includes(item)));
    }
    setDeletingQuery(false);
    loadQueries(selectedProject);
    onUpdateProjectAction();
    if (!_.isEmpty(deletedItems)) {
      openSnackBarWithMsg(
        "success",
        t("table.msg-success-delete", { count: deletedItems?.length }),
      );
    }
  };

  const handleRebuildCache = async (e, uuid) => {
    try {
      await buildQueryCache(selectedProject, uuid);
      setIsQueryCacheBuildingUUID(uuid);
    } catch (error) {
      openSnackBarWithMsg("error", error.message);
    }
  };

  const openSnackBarWithMsg = (variant, message) => {
    setSnackBarMessage(message);
    setSnackBarVariant(variant);
    setOpenSnackbar(true);
  };

  const customRender = (value) => {
    return (
      <Tooltip title="Manage Query">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={(e) => handleAction(e, value)}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderLinkOpenAction = (value, row) => {
    return (
      <TableLink
        color="primary"
        onClick={(e) => handleAction(e, row.uuid)}
        tooltipTitle={`Open ${value}`}
      >
        {value}
      </TableLink>
    );
  };

  const cacheRender = (_value, row) => {
    return <QueryCacheStatus cacheStatus={row.task_status} />;
  };

  const renderDate = (value) => {
    return helper.convertToLocalDateTime(value);
  };

  const renderCreateDate = (value) => {
    if (!value.includes("z") || !value.includes("Z")) {
      return renderDate(`${value}z`);
    }
    return renderDate(value);
  };

  const customBuildCache = (queryUUID, _row) => {
    return (
      <Tooltip title="Build Cache">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={(e) => handleRebuildCache(e, queryUUID)}
          disabled={Boolean(queryCacheBuildingUUID)}
        >
          <AutorenewIcon
            className={queryCacheBuildingUUID && queryUUID === queryCacheBuildingUUID}
          />
        </IconButton>
      </Tooltip>
    );
  };

  const customDelete = (value, row) => {
    return (
      <Tooltip title="Delete Query">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          disabled={!isDisableToBulkUpdate}
          onClick={(e) => handleOpenConfirmDelete(e, value, row.name)}
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
      title: "Columns",
      field: "columnList",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: "Filter",
      field: "metadata_filter",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },

    {
      title: "Segments",
      field: "query_segments",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: "Last Modified",
      field: "last_modified",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: renderDate,
    },
    {
      title: "Created Date",
      field: "created_at",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: renderCreateDate,
    },
    {
      title: "UUID",
      field: "uuid",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: "Status",
      field: "task_status",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      render: cacheRender,
    },
    { title: "Rebuild", field: "uuid", render: customBuildCache },
    { title: "Manage", field: "uuid", render: customRender },
    { title: "Delete", field: "uuid", render: customDelete },
  ];

  const options = {
    rowsPerPage: 25,
    rowsPerPageOptions: [5, 10, 25, 50, 100, "All"],
    showPagination: true,
    applyFilters: true,
    isShowSelection: true,
    selectionField: "uuid",
    onSelectInTable: handlseSelectInTable,
    noContentText: "No Queries",
    excludePrimaryFromDetails: true,
    isDarkHeader: true,
  };
  return (
    <>
      <UITablePanel
        title={t("table.title")}
        onRefresh={() => loadQueries(selectedProject)}
        ActionComponent={
          <>
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              onClick={() => handleOpenConfirmDelete()}
              tooltip={t("Delete Query")}
              text={t("Delete")}
              icon={<DeleteIcon />}
              disabled={isDisableToBulkUpdate}
              className={classes.mr1}
            />
          </>
        }
      />
      <StandardTable
        tableId="queriesTable"
        tableColumns={columns}
        tableData={queryList}
        tableOptions={options}
      />
      <DialogConfirm
        isOpen={open}
        title={t("table.dialog-delete-title")}
        text={deletingText}
        onConfirm={handleDeleteQuery}
        onCancel={handleClose}
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
      <Backdrop className={classes.backdrop} open={deletingQuery}>
        <CircularProgress size={100} />
      </Backdrop>
    </>
  );
};

export default QueriesTable;
