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
/* eslint-disable no-unused-vars */
import React, { useState, useMemo, useEffect } from "react";
import _ from "lodash";
import { useTranslation } from "react-i18next";

import DeleteIcon from "@mui/icons-material/Delete";
import helper from "store/helper";

import ListIcon from "@mui/icons-material/List";
import EditIcon from "@mui/icons-material/Edit";

import { Button, IconButton, Tooltip } from "@mui/material";

import StandardTable from "components/StandardTable";
import DialogFormMetadata from "components/DialogFormMetadata";
import DialogFormMetadataValues from "components/DialogFormMetadataValues";

import { DialogConfirm } from "components/DialogConfirm";
import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { UITablePanel } from "components/UIPanels";

const MetadataTable = ({
  projectUUID,
  metadata,
  loadMetadata,

  createMetadata,
  updateMetadata,
  deleteMetadata,

  createMetadataValue,
  updateMetadataValue,
  deleteMetadataValue,
}) => {
  const { t } = useTranslation("components");

  const [isOpenCreateMetadataDialog, setIsCreateMetadataDialog] = useState(false);
  const [editedMetadataValuesUUID, setEditedMetadataValuesUUID] = useState("");

  const [editedMetadataUUID, setEditedMetadataUUID] = useState("");
  const [validationError, setValidationError] = useState("");
  const [deletingUUID, setDeletingUUID] = useState("");

  const metadataNames = useMemo(() => {
    if (!_.isEmpty(metadata?.data) && _.isArray(metadata?.data)) {
      return metadata.data.map((el) => el.name);
    }
    return [];
  }, [metadata]);

  const metadataValuesToEdit = useMemo(() => {
    if (!_.isEmpty(metadata?.data) && _.isArray(metadata?.data)) {
      const metadataObj = metadata?.data.find((el) => el.uuid === editedMetadataValuesUUID) || {};
      if (metadataObj?.label_values) {
        return metadataObj?.label_values.map((el) => ({ name: el.uuid, value: el.value }));
      }
    }
    return [];
  }, [editedMetadataValuesUUID, metadata]);

  const metadataEditedValuesName = useMemo(() => {
    if (!_.isEmpty(metadata?.data) && _.isArray(metadata?.data)) {
      return metadata?.data.find((el) => el.uuid === editedMetadataValuesUUID)?.name || "";
    }
    return "";
  }, [editedMetadataValuesUUID, metadata]);

  const metadataToEdit = useMemo(() => {
    if (!_.isEmpty(metadata?.data) && _.isArray(metadata?.data)) {
      return metadata?.data.find((el) => el.uuid === editedMetadataUUID);
    }
    return {};
  }, [editedMetadataUUID]);

  const deletingMetadataName = useMemo(() => {
    if (!_.isEmpty(metadata?.data) && _.isArray(metadata?.data)) {
      return metadata?.data.find((el) => el.uuid === deletingUUID)?.name || "";
    }
    return "";
  }, [deletingUUID, metadata]);

  const clearValidationErrors = () => {
    if (validationError) {
      setValidationError("");
    }
  };

  const handleDateRender = (value) => {
    if (value) {
      return helper.convertToLocalDateTime(value);
    }
    return "";
  };

  const handleOpenEditValues = (metadataUUID) => {
    setEditedMetadataValuesUUID(metadataUUID);
  };

  const renderEditAction = (metadataUUID) => {
    return (
      <Tooltip title={t("metadata.tooltip-edit")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => setEditedMetadataUUID(metadataUUID)}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderEditValuesAction = (metadataUUID) => {
    return (
      <Tooltip title={t("metadata.tooltip-edit")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleOpenEditValues(metadataUUID)}
        >
          <ListIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderDeleteAction = (metadataUUID) => {
    return (
      <Tooltip title={t("metadata.tooltip-delete")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => setDeletingUUID(metadataUUID)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const handleCloseCreateDialog = () => {
    setIsCreateMetadataDialog(false);
    clearValidationErrors();
  };

  const handleCloseEditDialog = () => {
    setEditedMetadataUUID(false);
    clearValidationErrors();
  };

  const handleCloseMetadataValuesDialog = () => {
    setEditedMetadataValuesUUID("");
  };

  const handleLoadMetadata = () => {
    loadMetadata(projectUUID);
  };

  const handleCreateMetadata = async (name, isDropdown) => {
    try {
      const data = await createMetadata(projectUUID, name, isDropdown);
      loadMetadata(projectUUID);
      handleCloseCreateDialog();
      if (isDropdown) {
        handleOpenEditValues(data?.uuid);
      }
    } catch (_error) {
      setValidationError(_error.message);
    }
  };

  const handleEditMetadata = async (name, isDropdown) => {
    try {
      await updateMetadata(projectUUID, editedMetadataUUID, name, isDropdown);
      loadMetadata(projectUUID);
      handleCloseEditDialog();
    } catch (_error) {
      setValidationError(_error.message);
    }
  };

  const handleConfirmDeleteMetadata = async () => {
    try {
      await deleteMetadata(projectUUID, deletingUUID);
      setDeletingUUID("");
      loadMetadata(projectUUID);
    } catch (_error) {
      setValidationError(_error.message);
    }
  };

  const handleCreateMetadataValues = async (value) => {
    await createMetadataValue(projectUUID, editedMetadataValuesUUID, value);
  };

  const handleUpdateMetadataValues = async (valueUUID, value) => {
    await updateMetadataValue(projectUUID, editedMetadataValuesUUID, valueUUID, value);
  };

  const handleDeleteMetadataValues = async (valueUUID) => {
    await deleteMetadataValue(projectUUID, editedMetadataValuesUUID, valueUUID);
  };

  const columns = [
    {
      title: t("metadata.header-name"),
      field: "name",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: t("metadata.header-created"),
      field: "created_at",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: handleDateRender,
    },
    {
      title: t("metadata.header-updated"),
      field: "last_modified",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: handleDateRender,
    },

    { title: t("metadata.header-values"), field: "uuid", render: renderEditValuesAction },
    { title: t("metadata.header-edit"), field: "uuid", render: renderEditAction },
    { title: t("metadata.header-delete"), field: "uuid", render: renderDeleteAction },
  ];

  const title = t("metadata.title");
  const options = {
    rowsPerPage: 20,
    showPagination: false,
    noContentText: t("metadata.empty-content"),
    excludePrimaryFromDetails: true,
    applyFilters: true,
    isDarkHeader: true,
  };

  return (
    <>
      <UITablePanel
        title={title}
        ActionComponent={
          <>
            <Button
              variant="outlined"
              color="primary"
              onClick={() => setIsCreateMetadataDialog(true)}
            >
              {t("metadata.panel-btn-add")}
            </Button>
          </>
        }
      />
      <StandardTable tableData={metadata} tableColumns={columns} tableOptions={options} />
      <DialogFormMetadata
        title={t("metadata.dialog-create-title")}
        isOpen={isOpenCreateMetadataDialog}
        metadataNames={metadataNames}
        validationError={validationError}
        onClose={handleCloseCreateDialog}
        onSubmit={handleCreateMetadata}
      />
      <DialogFormMetadata
        title={t("metadata.dialog-edit-title")}
        isOpen={Boolean(editedMetadataUUID)}
        metadataNames={metadataNames}
        validationError={validationError}
        defaultName={metadataToEdit?.name || ""}
        defaultIsDropDown={metadataToEdit?.is_dropdown}
        onClose={handleCloseEditDialog}
        onSubmit={handleEditMetadata}
      />
      <DialogFormMetadataValues
        title={t("metadata.dialog-values-edit-title")}
        description={t("metadata.dialog-values-edit-description", {
          name: metadataEditedValuesName,
        })}
        key={editedMetadataValuesUUID}
        isOpen={Boolean(editedMetadataValuesUUID)}
        defaultValues={metadataValuesToEdit}
        onClose={handleCloseMetadataValuesDialog}
        onLoadMetadata={handleLoadMetadata}
        onCreate={handleCreateMetadataValues}
        onUpdate={handleUpdateMetadataValues}
        onDelete={handleDeleteMetadataValues}
      />
      {deletingUUID ? (
        <DialogConfirm
          isOpen={Boolean(deletingUUID)}
          title={t("metadata.dialog-delete-alert-title")}
          text={t("metadata.dialog-delete-alert-description", { name: deletingMetadataName })}
          onConfirm={handleConfirmDeleteMetadata}
          onCancel={() => setDeletingUUID("")}
          cancelText={t("dialog-confirm-delete.cancel")}
          confirmText={t("dialog-confirm-delete.delete")}
        />
      ) : null}
    </>
  );
};

export default MetadataTable;
