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

import React, { useState, useMemo, useEffect } from "react";
import _ from "lodash";
import PropTypes from "prop-types";

import { useTranslation } from "react-i18next";

import DeleteIcon from "@mui/icons-material/Delete";
import EditIcon from "@mui/icons-material/Edit";

import { DialogConfirm } from "components/DialogConfirm";
import { Alert, Button, Box, IconButton, Tooltip, Checkbox } from "@mui/material";

import StandardTable from "components/StandardTable";
import LabelColoredName from "components/LabelColoredName";
import SelectForm from "components/FormElements/SelectForm";
import InputNumberForm from "components/FormElements/InputNumberForm";
import DrawerForm from "components/UIDrawerForm";

import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { UITablePanel } from "components/UIPanels";

import useCaptureStyles from "./CaptureLabelsTableStyles";

const LABEL_SELECTED = "labelSelected";

const CaptureLabelsTable = ({
  selectedCapture,
  labels = [],
  editingSegment,
  onChangeEditedLabel,
  onDeleteLabels,
  onRowSelection,
  labeValueOptions,
  isReadOnlyMode = false,
  isDisabledByAutoSession = false,
}) => {
  const classes = useCaptureStyles();
  const { t } = useTranslation("components");

  const [selectedLabelList, setSelectedLabelList] = useState([]);
  const [selectedLabel, setSelectedLabel] = useState("");
  const [selectedLabelIndex, setSelectedLabelIndex] = useState(-1);

  const [updatedLabelData, setUpdatedLabelData] = useState({});
  const [isOpenEditForm, setIsOpenEditForm] = useState(false);
  const [isOpenDeleteConfirm, setIsOpenDeleteConfirm] = useState(false);
  const [labelFormValidationError, setLabelFormValidationError] = useState("");
  const [filteredData, setFilteredData] = useState([]);

  const editedLabelFormData = useMemo(() => {
    return labels.data.find((label) => label.id === selectedLabel) || {};
  }, [selectedLabel, labels]);

  const isDisableToBulkUpdate = useMemo(() => {
    return _.isEmpty(selectedLabelList) || isReadOnlyMode;
  }, [selectedLabelList, isReadOnlyMode]);

  const isDisabledDeleting = useMemo(() => {
    return isReadOnlyMode || isDisabledByAutoSession;
  }, [isReadOnlyMode, isDisabledByAutoSession]);

  const isShowCordinatesForm = useMemo(() => {
    return _.isEmpty(selectedLabelList) && !isDisabledByAutoSession;
  }, [isOpenEditForm, selectedLabelList, isDisabledByAutoSession]);

  const selectedLabelListToAction = useMemo(() => {
    if (!_.isEmpty(selectedLabelList)) {
      return selectedLabelList;
    }
    return [selectedLabel];
  }, [selectedLabelList, selectedLabel]);

  const labelsToRender = useMemo(() => {
    return {
      data: _.map(labels?.data, (labelItem) => {
        return {
          [LABEL_SELECTED]: selectedLabelList.includes(labelItem.id) ? 1 : 0,
          ...labelItem,
        };
      }),
      isFetching: labels?.isFetching || false,
    };
  }, [selectedLabelList, labels]);

  const handleRowSelection = (row) => {
    if (selectedLabelList.includes(row?.id)) {
      setSelectedLabelList(selectedLabelList.filter((labelID) => labelID !== row.id));
    } else {
      setSelectedLabelList([...selectedLabelList, row.id]);
    }
  };

  const handleSelectAll = () => {
    setSelectedLabelList(filteredData.map((el) => el.id));
  };

  const handleUnSelectAll = () => {
    setSelectedLabelList([]);
  };

  // Editing Form

  const validateUpdatingLabel = (start, end) => {
    if (!isShowCordinatesForm) {
      return true;
    }
    if (start > end) {
      setLabelFormValidationError(t("label-table.lalel-form-error-stat-greater-end"));
      return false;
    }
    if (start < 0) {
      setLabelFormValidationError(t("label-table.lalel-form-error-stat-less-0"));
      return false;
    }
    if (end > selectedCapture.max_sequence) {
      setLabelFormValidationError(t("label-table.lalel-form-error-end-greater-max"));
      return false;
    }
    if (
      labels.data.find(
        (label) => label.start === start && label.end === end && label.id !== selectedLabel,
      )
    ) {
      setLabelFormValidationError(t("label-table.lalel-form-error-dublicates"));
      return false;
    }
    return true;
  };

  const handleOpenEditForm = (labelID) => {
    if (labelID) {
      setSelectedLabel(labelID);
    }
    setIsOpenEditForm(true);
  };

  const handleCloseEditForm = () => {
    setIsOpenEditForm(false);
    setSelectedLabel("");
  };

  const handleUpdateEditLabel = (name, value) => {
    setUpdatedLabelData((val) => {
      const prevVal = { ...val };
      prevVal[name] = value;
      return prevVal;
    });
  };

  const handleUpdateEditLabelValueUUID = (_name, labelValueUUID) => {
    const { color, name, uuid } = labeValueOptions.find(
      (labelValue) => labelValue.uuid === labelValueUUID,
    );
    setUpdatedLabelData({ ...updatedLabelData, name, color, uuid, labelValueUUID });
  };

  const handleSaveUpdatedLabelData = () => {
    setLabelFormValidationError("");
    const { name, color, labelValueUUID, start, end } = updatedLabelData;
    if (validateUpdatingLabel(start, end)) {
      selectedLabelListToAction.forEach((labelID) => {
        onChangeEditedLabel({ id: labelID, name, color, labelValueUUID, start, end });
      });
      handleCloseEditForm();
      setSelectedLabelList([]);
    }
  };

  // Deleting Form

  const handleOpenConfirmDelete = (labelID) => {
    setIsOpenDeleteConfirm(true);
    if (labelID) {
      setSelectedLabel(labelID);
    }
  };

  const handleCloseConfirmDelete = () => {
    setIsOpenDeleteConfirm(false);
    setSelectedLabel("");
  };

  const handleConfirmDelete = () => {
    onDeleteLabels(selectedLabelListToAction);
    setSelectedLabelList([]);
    handleCloseConfirmDelete();
  };
  //

  useEffect(() => {
    setSelectedLabel(editingSegment.id);
  }, [editingSegment]);

  useEffect(() => {
    const activeLabelIndex = labels.data.findIndex((el) => el.id === editingSegment.id);
    setSelectedLabelIndex(activeLabelIndex);
  }, [labels]);

  const renderLabel = (_value, row) => {
    return <LabelColoredName name={row?.name || ""} color={row?.color || ""} />;
  };

  const renderSelectionAction = (value, row) => {
    return (
      <Tooltip
        title={
          selectedLabelList.includes(row?.id)
            ? t("label-table.tooltip-label-selected")
            : t("label-table.tooltip-label-not-selected")
        }
      >
        <IconButton variant="contained" color="primary" size="small">
          <Checkbox
            key={`capture-label-selection-${row?.id}`}
            checked={selectedLabelList.includes(row?.id)}
            onClick={() => handleRowSelection(row)}
            color="primary"
          />
        </IconButton>
      </Tooltip>
    );
  };

  const renderLength = (_labelID, row) => {
    return _.subtract(row.end + 1, row.start);
  };

  const renderEditAction = (labelID) => {
    return (
      <Tooltip title={t("label-table.tooltip-label-edit-label")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleOpenEditForm(labelID)}
          disabled={!isDisableToBulkUpdate || isReadOnlyMode}
        >
          <EditIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderDeleteAction = (labelID) => {
    return (
      <Tooltip title={t("label-table.tooltip-label-delete-label")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleOpenConfirmDelete(labelID)}
          disabled={!isDisableToBulkUpdate || isDisabledDeleting}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  // eslint-disable-next-line no-unused-vars
  const renderId = (sequence) => {
    return sequence || "";
  };

  const columns = [
    {
      title: " ",
      field: LABEL_SELECTED,
      sortable: true,
      type: ColumnType.Numeric,
      lookup: {
        0: t("label-table.header-unselected"),
        1: t("label-table.header-selected"),
      },
      render: renderSelectionAction,
    },
    {
      title: t("label-table.header-id"),
      field: "sequence",
      sortable: true,
      type: ColumnType.Numeric,
      render: renderId,
    },

    {
      title: t("label-table.header-name"),
      field: "name",
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      render: renderLabel,
    },
    {
      title: t("label-table.header-start"),
      field: "start",
      sortable: true,
      type: ColumnType.Numeric,
    },
    {
      title: t("label-table.header-end"),
      field: "end",
      sortable: true,
      type: ColumnType.Numeric,
    },
    {
      title: t("label-table.header-length"),
      field: "length",
      sortable: true,
      type: ColumnType.Numeric,
      render: renderLength,
    },

    { title: t("label-table.header-edit"), field: "id", render: renderEditAction },

    { title: t("label-table.header-delete"), field: "id", render: renderDeleteAction },
  ];

  const title = t("label-table.title");
  const options = {
    rowsPerPage: 30,
    showPagination: true,
    noContentText: t("label-table.empty-content"),
    excludePrimaryFromDetails: true,
    applyFilters: true,
    onRowSelection,
    selectedRowId: selectedLabel,
    selectedRowIndex: selectedLabelIndex,
    isShowSelection: true,
    onSelectAllInTable: handleSelectAll,
    onUnSelectAllInTable: handleUnSelectAll,
    captureTableData: (data) => setFilteredData(data),
  };

  return (
    <>
      <UITablePanel
        title={title}
        ActionComponent={
          <>
            <Button
              startIcon={<EditIcon />}
              variant="outlined"
              color="primary"
              className={classes.mr1}
              disabled={isDisableToBulkUpdate}
              onClick={() => handleOpenEditForm()}
            >
              {t("label-table.panel-btn-edit")}
            </Button>
            <Button
              startIcon={<DeleteIcon />}
              variant="outlined"
              color="primary"
              className={classes.mr1}
              disabled={isDisableToBulkUpdate || isDisabledDeleting}
              onClick={() => handleOpenConfirmDelete()}
            >
              {t("label-table.panel-btn-delete")}
            </Button>
          </>
        }
      />
      <StandardTable
        tableId="lableTable"
        tableData={labelsToRender}
        tableColumns={columns}
        tableOptions={options}
      />
      <DrawerForm
        isOpen={isOpenEditForm}
        title={t("label-table.form-edit-title")}
        onClose={handleCloseEditForm}
        onSubmit={handleSaveUpdatedLabelData}
      >
        {!_.isEmpty(labelFormValidationError) ? (
          <Alert severity={"error"}>{labelFormValidationError}</Alert>
        ) : null}
        <Box className={classes.formControl}>
          <SelectForm
            className={classes.labelSelector}
            id={"select_label"}
            fullWidth
            name={"labelValueUUID"}
            key={editedLabelFormData.id}
            label={t("label-table.form-edit-label-label")}
            defaultValue={editedLabelFormData?.labelValueUUID}
            options={labeValueOptions.map((el) => ({
              name: <LabelColoredName name={el?.name} color={el?.color} />,
              value: el?.uuid,
            }))}
            onChange={handleUpdateEditLabelValueUUID}
          />
        </Box>
        {isShowCordinatesForm ? (
          <Box className={classes.formControl}>
            <Box className={classes.boxStartEndWrapper}>
              <Box className={classes.boxStartEndWrap}>
                <InputNumberForm
                  id="start"
                  name="start"
                  label={t("label-table.form-edit-label-start")}
                  defaultValue={editedLabelFormData.start}
                  onChange={handleUpdateEditLabel}
                  fullWidth
                />
              </Box>
              <Box className={classes.boxStartEndWrap}>
                <InputNumberForm
                  id="end"
                  name="end"
                  label={t("label-table.form-edit-label-end")}
                  defaultValue={editedLabelFormData.end}
                  onChange={handleUpdateEditLabel}
                  fullWidth
                />
              </Box>
            </Box>
          </Box>
        ) : null}
      </DrawerForm>
      <DialogConfirm
        isOpen={isOpenDeleteConfirm}
        title={t("label-table.alert-deleting-title")}
        text={t("label-table.alert-deleting-text")}
        onConfirm={handleConfirmDelete}
        onCancel={handleCloseConfirmDelete}
        cancelText={t("dialog-confirm-delete.cancel")}
        confirmText={t("dialog-confirm-delete.delete")}
      />
    </>
  );
};

CaptureLabelsTable.propTypes = {
  onChangeEditedLabel: PropTypes.func,
  onDeleteLabels: PropTypes.func,
  labeValueOptions: PropTypes.array.isRequired,
};

CaptureLabelsTable.defaultProps = {
  onChangeEditedLabel: () => {},
  onDeleteLabels: () => {},
};

export default CaptureLabelsTable;
