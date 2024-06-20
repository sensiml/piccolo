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

import React, { useState, useMemo, useEffect, useCallback } from "react";
import _ from "lodash";
import { useTranslation } from "react-i18next";

import DeleteIcon from "@mui/icons-material/Delete";
import helper from "store/helper";

import EditIcon from "@mui/icons-material/Edit";

import { Button, IconButton, Tooltip } from "@mui/material";

import StandardTable from "components/StandardTable";
import LabelColoredName from "components/LabelColoredName";

import { DialogConfirm } from "components/DialogConfirm";
import { DialogFormLabel } from "components/DialogFormLabel";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { UITablePanel } from "components/UIPanels";

const LabelTable = ({
  projectUUID,
  labelValues,
  labels,
  defaultLabel,
  createLabel,
  updateLabel,
  deleteLabel,
}) => {
  const { t } = useTranslation("components");

  const [isCreateLabel, setIsCreateLabel] = useState(false);
  const [deletedLabelUUID, setDeletedLabelUUID] = useState("");
  const [editingLabelValue, setEditingLabelValue] = useState({});

  const [editingLabelUUID, setEditingLabelUUID] = useState("");
  const [validationError, setValidationError] = useState("");

  const isShowLabelGroup = useMemo(() => {
    return labels?.length > 1 || false;
  }, [labels]);

  const labelGroupOptions = useMemo(() => {
    if (!_.isEmpty(labels)) {
      return labels.map((label) => ({ name: label.name, value: label.uuid }));
    }
    return [];
  }, [labels]);

  const getLabelNamesToCheck = useCallback(
    (_labelGroupUUID) => {
      if (!_.isEmpty(labelValues.data)) {
        return labelValues.data
          .filter((label) => label.labelUUID === _labelGroupUUID)
          .map((label) => _.toLower(label.name));
      }
      return [];
    },
    [labelValues],
  );

  const labelToDelete = useMemo(() => {
    if (!_.isEmpty(labelValues.data)) {
      return labelValues.data.find((label) => label.uuid === deletedLabelUUID);
    }
    return {};
  }, [deletedLabelUUID]);

  const handleOpenEditForm = (labelUUID) => {
    const labelToEdit = labelValues.data.find((label) => label.uuid === labelUUID);
    setEditingLabelValue(labelToEdit);
  };

  const handleCloseEditForm = () => {
    setEditingLabelValue({});
  };

  const handleUpdateLabel = async (value, color, labelGroupUUID) => {
    try {
      await updateLabel(projectUUID, labelGroupUUID || editingLabelUUID, editingLabelValue.uuid, {
        value,
        color,
      });
      handleCloseEditForm();
    } catch (_error) {
      setValidationError(_error.message);
    }
  };

  const handleCloseCreateForm = () => {
    setIsCreateLabel(false);
  };

  const handleOpenCreateForm = () => {
    setIsCreateLabel(true);
  };

  const handleCrateLabel = async (value, color, labelGroupUUID) => {
    try {
      await createLabel(projectUUID, labelGroupUUID || editingLabelUUID, { value, color });
      if (labelGroupUUID) {
        setEditingLabelUUID(labelGroupUUID);
      }
      handleCloseCreateForm();
    } catch (_error) {
      setValidationError(_error.message);
    }
  };

  const renderLabel = (_value, row) => {
    return <LabelColoredName name={row?.name || ""} color={row?.color || ""} />;
  };

  const handleDateRender = (value) => {
    if (value) {
      return helper.convertToLocalDateTime(value);
    }
    return "";
  };

  // deleting
  const handleOpenConfirmDelete = (labelUUID) => {
    setDeletedLabelUUID(labelUUID);
  };

  const handleCloseConfirmDelete = () => {
    handleOpenConfirmDelete("");
  };

  const handleConfirmDelete = () => {
    deleteLabel(projectUUID, labelToDelete?.labelUUID, labelToDelete?.uuid);
    handleCloseConfirmDelete();
  };

  useEffect(() => {
    setValidationError("");
  }, [editingLabelValue, isCreateLabel]);

  useEffect(() => {
    setEditingLabelUUID(defaultLabel?.uuid);
  }, []);

  useEffect(() => {
    return () => setEditingLabelUUID("");
  }, []);

  const renderEditAction = (labelUUID) => {
    return (
      <Tooltip title={t("label-values-table.tooltip-edit-label")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleOpenEditForm(labelUUID)}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderDeleteAction = (labelUUID) => {
    return (
      <Tooltip title={t("label-values-table.tooltip-delete-label")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleOpenConfirmDelete(labelUUID)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const columns = [
    {
      title: t("label-values-table.header-name"),
      field: "name",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      render: renderLabel,
    },
    isShowLabelGroup && {
      title: t("label-values-table.header-label-group-name"),
      field: "label",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: t("label-values-table.header-created"),
      field: "created",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: handleDateRender,
    },
    {
      title: t("label-values-table.header-updated"),
      field: "updated",
      sortable: true,
      type: ColumnType.DateTime,
      filterable: true,
      render: handleDateRender,
    },
    { title: t("label-values-table.header-edit"), field: "uuid", render: renderEditAction },
    { title: t("label-values-table.header-delete"), field: "uuid", render: renderDeleteAction },
  ];

  const title = t("label-values-table.title");
  const options = {
    rowsPerPage: 20,
    showPagination: false,
    noContentText: t("label-values-table.empty-content"),
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
            <Button variant="outlined" color="primary" onClick={() => handleOpenCreateForm()}>
              {t("label-values-table.panel-btn-add")}
            </Button>
          </>
        }
      />
      <StandardTable tableData={labelValues} tableColumns={columns} tableOptions={options} />
      {!_.isEmpty(editingLabelValue) ? (
        <DialogFormLabel
          isOpen={!_.isEmpty(editingLabelValue)}
          title={t("label-values-table.dialog-edit-title")}
          getLabelNamesToCheck={getLabelNamesToCheck}
          labelName={editingLabelValue.name}
          defaultLabelColor={editingLabelValue.color}
          labelGroupOptions={labelGroupOptions}
          defaultLabelGroup={editingLabelValue.labelUUID}
          onClose={handleCloseEditForm}
          onSubmit={handleUpdateLabel}
          validationError={validationError}
        />
      ) : null}
      {isCreateLabel ? (
        <DialogFormLabel
          isOpen={isCreateLabel}
          title={t("label-values-table.dialog-create-title")}
          getLabelNamesToCheck={getLabelNamesToCheck}
          labelGroupOptions={labelGroupOptions}
          defaultLabelGroup={editingLabelUUID}
          onClose={handleCloseCreateForm}
          onSubmit={handleCrateLabel}
          validationError={validationError}
        />
      ) : null}
      {deletedLabelUUID ? (
        <DialogConfirm
          isOpen={Boolean(deletedLabelUUID)}
          title={t("label-values-table.alert-deleting-title")}
          text={t("label-values-table.alert-deleting-text", { labelName: labelToDelete?.name })}
          onConfirm={handleConfirmDelete}
          onCancel={handleCloseConfirmDelete}
          cancelText={t("dialog-confirm-delete.cancel")}
          confirmText={t("dialog-confirm-delete.delete")}
        />
      ) : null}
    </>
  );
};

export default LabelTable;
