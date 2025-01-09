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

import React, { useState, useEffect, useMemo, useContext } from "react";
import _ from "lodash";

import { useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";

import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import LayersOutlinedIcon from "@mui/icons-material/LayersOutlined";

import makeStyles from "@mui/styles/makeStyles";
import { Box, Typography } from "@mui/material";
import { useIsShortText } from "hooks";

import { UIButtonResponsiveToShort } from "components/UIButtons";

import DialogInformation from "components/DialogInformation/DialogInformation";
import ControlPanel from "components/ControlPanel";
import CapturesTable from "components/CapturesTable";
import CaptureImportForm from "components/CaptureImportForm";

import { DataManagerContext } from "../context";

const useStyles = () =>
  makeStyles((theme) => ({
    ...theme.common,
    createDialogTitle: {
      marginBottom: theme.spacing(2),
      textAlign: "center",
    },
    chartInformationHeader: {
      color: theme.palette.primary.main,
      fontWeight: 500,
      marginRight: theme.spacing(1),
    },
  }))();

const TheCapturesScreen = ({
  selectedSessionUUID,
  selectedSession,
  loadCapturesMetadata,
  updateCapturesMetadata,
  uploadCapture,
  updateCapture,
  getCaptureMetadataFormData,
  getCaptureConfigurationFormData,
  getSampleRate,
  captures,
  metadataTableColumnData,
  isLoadingMetadata,
  // eslint-disable-next-line no-unused-vars
  loadCapture,
  loadCapturesStatistics,
  loadSources,
  deleteCapture,
  createDefaultMetadata,
  onShowInformation,
}) => {
  const classes = useStyles();
  const { projectUUID } = useParams();
  const { t } = useTranslation("data-manager");

  const [isOpenImport, setIsOpenImport] = useState(false);

  // eslint-disable-next-line no-unused-vars
  const { onOpenSelectSessionDialog } = useContext(DataManagerContext);
  const isShortText = useIsShortText();

  const handleSubmitFile = (file, name) => {
    return uploadCapture(projectUUID, file, name);
  };

  const loadCaptureData = async () => {
    await loadCapturesStatistics(projectUUID, selectedSessionUUID);
  };

  const loadDataAfterUpload = () => {
    loadCaptureData();
    loadSources(projectUUID);
  };

  const handleCloseImportForm = () => {
    setIsOpenImport(false);
  };

  const handleOpenImportForm = () => {
    setIsOpenImport(true);
  };

  const handleSubmitCaptureForm = async (
    uploadedCaptureUUID,
    updatedCaptureData,
    updatedMetadataData,
  ) => {
    const errorMessages = [];
    try {
      await updateCapture(projectUUID, uploadedCaptureUUID, updatedCaptureData);
    } catch (error) {
      errorMessages.push(`${"Sensor Configuration: "} ${error.message}`);
    }
    try {
      await updateCapturesMetadata(projectUUID, [uploadedCaptureUUID], updatedMetadataData);
    } catch (error) {
      errorMessages.push(`${"Metadata: "} ${error.message}`);
    }
    loadCapturesMetadata(projectUUID);
    setIsOpenImport(false);
    if (_.isEmpty(errorMessages)) {
      loadCaptureData();
    } else {
      // setMetadataFormErrors(errorMessages);
    }
  };

  const captureNames = useMemo(() => {
    if (!_.isEmpty(captures?.data)) {
      return captures.data.map((capture) => capture.name);
    }
    return [];
  }, [captures]);

  const handleDownloadCapture = async (captureUUID, captureFileName) => {
    await loadCapture(projectUUID, captureUUID, captureFileName, true);
  };

  useEffect(() => {
    const loadData = async () => {
      if (_.isEmpty(captures?.data)) {
        await loadCaptureData();
      }
      if (_.isEmpty(metadataTableColumnData)) {
        await loadCapturesMetadata(projectUUID);
      }
    };
    loadData();
  }, []);

  useEffect(() => {
    loadCaptureData();
  }, [selectedSessionUUID]);

  return (
    <>
      <Box mb={2}>
        <ControlPanel
          title={<>Data Manager</>}
          subtitle={
            isShortText ? (
              ""
            ) : (
              <Typography variant="subtitle1">
                <span className={classes.chartInformationHeader} color="primary">
                  {`${t("capture-screen.session")}:`}
                </span>
                {selectedSession?.name}
              </Typography>
            )
          }
          actionsBtns={
            <>
              <UIButtonResponsiveToShort
                variant={"outlined"}
                color={"primary"}
                onClick={() => onOpenSelectSessionDialog()}
                tooltip={t("capture-screen.panel-btn-session")}
                text={t("capture-screen.panel-btn-session")}
                icon={<LayersOutlinedIcon />}
              />
              <UIButtonResponsiveToShort
                variant={"outlined"}
                color={"primary"}
                onClick={() => handleOpenImportForm()}
                tooltip={t("capture-screen.panel-btn-import-tooltip")}
                text={t("capture-screen.panel-btn-import-text")}
                icon={<CloudUploadOutlinedIcon />}
              />
            </>
          }
          onShowInformation={onShowInformation}
        />
      </Box>
      <DialogInformation isOpen={isOpenImport} onClose={handleCloseImportForm}>
        <Typography variant="h2" className={classes.createDialogTitle}>
          {t("Import capture file")}
        </Typography>
        <CaptureImportForm
          projectUUID={projectUUID}
          onSubmitFile={handleSubmitFile}
          updateCapturesMetadata={updateCapturesMetadata}
          updateCapture={updateCapture}
          onSubmitCaptureForm={handleSubmitCaptureForm}
          loadCaptures={loadCaptureData}
          loadCapturesMetadata={loadCapturesMetadata}
          loadDataAfterUpload={loadDataAfterUpload}
          onClose={handleCloseImportForm}
          captureNames={captureNames}
          getCaptureMetadataFormData={getCaptureMetadataFormData}
          getCaptureConfigurationFormData={getCaptureConfigurationFormData}
          getSampleRate={getSampleRate}
          createDefaultMetadata={createDefaultMetadata}
        />
      </DialogInformation>
      <CapturesTable
        updateCapturesMetadata={updateCapturesMetadata}
        deleteCapture={deleteCapture}
        updateCapture={updateCapture}
        loadCaptures={loadCaptureData}
        loadCapturesMetadata={loadCapturesMetadata}
        projectUUID={projectUUID}
        getCaptureMetadataFormData={getCaptureMetadataFormData}
        getCaptureConfigurationFormData={getCaptureConfigurationFormData}
        captures={captures}
        isLoadingMetadata={isLoadingMetadata}
        downloadCapture={handleDownloadCapture}
        metadataTableColumnData={metadataTableColumnData}
      />
    </>
  );
};

export default TheCapturesScreen;
