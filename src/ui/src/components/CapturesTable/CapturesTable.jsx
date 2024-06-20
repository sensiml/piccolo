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

import React, { useEffect, useState, useMemo } from "react";
import _ from "lodash";
import { useTranslation } from "react-i18next";
import { useHistory } from "react-router-dom";

import DeleteIcon from "@mui/icons-material/Delete";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import LaunchOutlinedIcon from "@mui/icons-material/LaunchOutlined";

import PhotoFilter from "@mui/icons-material/PhotoFilter";
import EditIcon from "@mui/icons-material/Edit";

import { Box, IconButton, Tooltip } from "@mui/material";

import CaptureMetadataForm from "components/CaptureMetadataForm";
import StandardTable from "components/StandardTable";
import DrawerForm from "components/UIDrawerForm";

import { DialogConfirm } from "components/DialogConfirm";
import { ColumnType } from "components/StandardTable/StandardTableConstants";
import { UITablePanel } from "components/UIPanels";
import { ElementLoader } from "components/UILoaders";
import { TableLink } from "components/UILinks";

import { UIButtonResponsiveToShort } from "components/UIButtons";

import { filterFormatDate } from "filters";

import useCaptureStyles from "./CaptureStyles";

const CapturesTable = ({
  projectUUID,
  captures = [],
  isLoadingMetadata,
  metadataTableColumnData,

  loadCaptures,
  loadCapturesMetadata,
  getCaptureMetadataFormData,
  getCaptureConfigurationFormData,
  updateCapturesMetadata,
  deleteCapture,
  updateCapture,
  downloadCapture,
}) => {
  const { t } = useTranslation("components");
  const routersHistory = useHistory();
  const classes = useCaptureStyles();

  const [selectedFiles, setSelectedFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState("");

  const [captureMetadataFormData, setCaptureMetadataFormData] = useState([]);
  const [captureFromData, setCaptureFromData] = useState([]);

  const [isOpenDeleteConfirm, setIsOpenDeleteConfirm] = useState(false);
  const [isSubmitingCapture, setIsSubmitingCapture] = useState(false);
  const [submitingCaptureName, setSubmitingCaptureName] = useState("");

  const [updatedMetadataData, setUpdatedMetadataData] = useState({});
  const [updatedCaptureData, setUpdatedCaptureData] = useState({});
  const [metadataFormErrors, setMetadataFormErrors] = useState([]);

  const isDisableToBulkUpdate = useMemo(() => {
    return _.isEmpty(selectedFiles);
  }, [selectedFiles]);

  const selectedCaptureList = useMemo(() => {
    // fileter defined values
    return _.union(selectedFiles, [selectedFile]).filter((item) => item);
  }, [selectedFiles, selectedFile]);

  const capturesToRender = useMemo(() => {
    return {
      data: _.map(captures?.data, (captureItem) => captureItem),
      isFetching: captures?.isFetching || isLoadingMetadata || false,
    };
  }, [isLoadingMetadata, captures]);

  const handlseSelectInTable = (selectedUUIDs) => {
    setSelectedFiles(selectedUUIDs);
  };

  const handleOpenCaptureFile = (routerURL) => {
    routersHistory.push(routerURL);
  };

  // Editing Form

  const handleOpenEditForm = (captureUUID) => {
    setIsSubmitingCapture(false);
    if (captureUUID) {
      setSelectedFile(captureUUID);
    }
    setCaptureMetadataFormData(getCaptureMetadataFormData(captureUUID));
    setCaptureFromData(getCaptureConfigurationFormData(captureUUID));
  };

  const handleCloseEditForm = () => {
    if (!_.isEmpty(metadataFormErrors)) {
      setMetadataFormErrors([]);
    }
    setSelectedFile("");
    setCaptureMetadataFormData([]);
    setCaptureFromData([]);
    setUpdatedCaptureData({});
    setUpdatedMetadataData({});
  };

  const handleSubmitEditForm = async () => {
    const errorMessages = [];
    setIsSubmitingCapture(true);
    try {
      if (!_.isEmpty(updatedCaptureData)) {
        // eslint-disable-next-line no-restricted-syntax
        for (const captureUUID of selectedCaptureList) {
          const captureObj = capturesToRender.data.find((capture) => capture.uuid === captureUUID);
          setSubmitingCaptureName(captureObj.name);
          // eslint-disable-next-line no-await-in-loop
          await updateCapture(projectUUID, captureUUID, updatedCaptureData);
        }
      }
    } catch (error) {
      errorMessages.push(`${"Sensor Configuration: "} ${error.message}`);
    }
    try {
      await updateCapturesMetadata(projectUUID, selectedCaptureList, updatedMetadataData);
    } catch (error) {
      errorMessages.push(`${"Metadata: "} ${error.message}`);
    }
    if (_.isEmpty(errorMessages)) {
      loadCapturesMetadata(projectUUID);
      loadCaptures(projectUUID);
      handleCloseEditForm();
    } else {
      setMetadataFormErrors(errorMessages);
    }
    setIsSubmitingCapture(false);
    setSubmitingCaptureName("");
  };

  // Deleting Form

  const handleDownloadFile = (captureUUID, captureName) => {
    downloadCapture(captureUUID, captureName);
  };

  const handleOpenConfirmDelete = (captureUUID) => {
    setIsOpenDeleteConfirm(true);
    if (captureUUID) {
      setSelectedFile(captureUUID);
    }
  };

  const handleCloseConfirmDelete = () => {
    setIsOpenDeleteConfirm(false);
    setSelectedFile("");
  };

  const handleConfirmDelete = () => {
    selectedCaptureList.forEach((captureUUID) => {
      deleteCapture(projectUUID, captureUUID);
    });
    handleCloseConfirmDelete();
    setSelectedFiles([]);
  };
  //

  useEffect(() => {
    loadCapturesMetadata(projectUUID);
  }, []);

  const renderDownloadAction = (captureUUID, row) => {
    return (
      <Tooltip title={t("captures-table.tooltip-download")}>
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={() => handleDownloadFile(captureUUID, row.name)}
        >
          <CloudDownloadOutlinedIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const renderOpenAction = (value) => {
    return (
      <Tooltip title={t("captures-table.tooltip-open-file")}>
        <Box>
          <IconButton
            variant="contained"
            color="primary"
            size="small"
            onClick={(_e) => handleOpenCaptureFile(value)}
          >
            <LaunchOutlinedIcon />
          </IconButton>
        </Box>
      </Tooltip>
    );
  };

  const renderLinkOpenAction = (value, row) => {
    return (
      <TableLink
        color="primary"
        onClick={(_e) => handleOpenCaptureFile(row.openFileURL)}
        tooltipTitle={t("captures-table.tooltip-open-file")}
      >
        {value}
      </TableLink>
    );
  };

  const renderEditAction = (captureUUID) => {
    return (
      <Tooltip title={t("captures-table.tooltip-edit-metadata")}>
        <Box>
          <IconButton
            variant="contained"
            color="primary"
            size="small"
            onClick={() => handleOpenEditForm(captureUUID)}
            disabled={!isDisableToBulkUpdate}
          >
            <EditIcon />
          </IconButton>
        </Box>
      </Tooltip>
    );
  };

  const renderDeleteAction = (captureUUID) => {
    return (
      <span>
        <Tooltip title={t("captures-table.tooltip-delete-file")}>
          <Box>
            <IconButton
              variant="contained"
              color="primary"
              size="small"
              sx={{ input: { cursor: "pointer" } }}
              onClick={(_e) => handleOpenConfirmDelete(captureUUID)}
              disabled={!isDisableToBulkUpdate}
            >
              <DeleteIcon />
            </IconButton>
          </Box>
        </Tooltip>
      </span>
    );
  };

  const renderDate = (createdDate) => {
    return <>{filterFormatDate(createdDate)}</>;
  };

  const columns = [
    {
      title: t("captures-table.header-name"),
      field: "name",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
      render: renderLinkOpenAction,
    },

    {
      title: t("captures-table.header-segments"),
      field: "total_events",
      primary: true,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: t("captures-table.header-size"),
      field: "file_size_mb",
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: t("captures-table.header-created-date"),
      field: "created",
      sortable: true,
      type: ColumnType.Date,
      filterable: true,
      render: renderDate,
    },
    ...metadataTableColumnData,
    {
      title: "Open",
      field: "openFileURL",
      render: renderOpenAction,
    },
    {
      title: t("captures-table.header-export"),
      field: "uuid",
      render: renderDownloadAction,
    },
    { title: t("captures-table.header-metadata"), field: "uuid", render: renderEditAction },
    { title: t("captures-table.header-delete"), field: "uuid", render: renderDeleteAction },
  ];

  const title = t("captures-table.title");
  const options = {
    rowsPerPage: 25,
    rowsPerPageOptions: [10, 25, 50, 100, "All"],
    showPagination: true,
    applyFilters: true,
    isDarkHeader: true,
    selectionField: "uuid",
    onSelectInTable: handlseSelectInTable,
    isShowSelection: true,
    noContentText: t("captures-table.empty-content"),
  };

  const handleUpdateMetadataField = (name, value) => {
    if (!_.isEmpty(metadataFormErrors)) {
      setMetadataFormErrors([]);
    }
    setUpdatedMetadataData((prevVal) => {
      return {
        ...prevVal,
        [name]: value,
      };
    });
  };

  const handleUpdateCaptureField = (name, value) => {
    if (!_.isEmpty(metadataFormErrors)) {
      setMetadataFormErrors([]);
    }
    if (value) {
      setUpdatedCaptureData((prevVal) => {
        return {
          ...prevVal,
          [name]: value,
        };
      });
    }
  };

  return (
    <>
      <UITablePanel
        title={title}
        onRefresh={() => loadCaptures(projectUUID)}
        ActionComponent={
          <>
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              onClick={() => handleOpenEditForm()}
              className={classes.mr1}
              disabled={isDisableToBulkUpdate}
              tooltip={"Edit Selected Files Metadata"}
              text={"Metadata"}
              icon={<PhotoFilter />}
            />
            <UIButtonResponsiveToShort
              variant={"outlined"}
              color={"primary"}
              onClick={() => handleOpenConfirmDelete()}
              disabled={isDisableToBulkUpdate}
              tooltip={"Delete Selected Captures"}
              text={"Delete"}
              icon={<DeleteIcon />}
            />
          </>
        }
      />
      <StandardTable
        tableId="capturesTable"
        tableData={capturesToRender}
        tableColumns={columns}
        tableOptions={options}
        isResetPageAfterUpdateTableData={false}
      />
      <DialogConfirm
        isOpen={isOpenDeleteConfirm}
        title={t("captures-table.alert-deleting-title")}
        text={t("captures-table.alert-deleting-text")}
        onConfirm={handleConfirmDelete}
        onCancel={handleCloseConfirmDelete}
        cancelText={t("dialog-confirm-delete.cancel")}
        confirmText={t("dialog-confirm-delete.delete")}
      />
      <DrawerForm
        isOpen={!_.isEmpty(captureMetadataFormData)}
        title={"Change Metadata"}
        onClose={handleCloseEditForm}
        onSubmit={handleSubmitEditForm}
        isConfirmDisabled={isSubmitingCapture}
      >
        {isSubmitingCapture ? (
          <ElementLoader
            isOpen
            type="TailSpin"
            message={t("captures-table.updating-message", { name: submitingCaptureName })}
          />
        ) : (
          <CaptureMetadataForm
            validationErrors={metadataFormErrors}
            captureConfigurationFromData={captureFromData}
            captureMetadataFormData={captureMetadataFormData}
            onUpdateCaptureField={handleUpdateCaptureField}
            onUpdateMetadataField={handleUpdateMetadataField}
          />
        )}
      </DrawerForm>
    </>
  );
};

export default CapturesTable;
