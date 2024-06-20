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

import React, { useEffect, useState, useMemo, useCallback, useContext } from "react";
import _ from "lodash";
import Alert from "@mui/material/Alert";

import { useTranslation } from "react-i18next";
import { useParams, useHistory, generatePath, useLocation } from "react-router-dom";

import EditOutlinedIcon from "@mui/icons-material/EditOutlined";
import LayersOutlinedIcon from "@mui/icons-material/LayersOutlined";
import CloudDownloadOutlinedIcon from "@mui/icons-material/CloudDownloadOutlined";
import ArrowBackIcon from "@mui/icons-material/ArrowBack";

import { Box, Paper, Fade, Tab, Tabs, Typography } from "@mui/material";

import logger from "store/logger";
import CaptureLabelsTable from "components/CaptureLabelsTable";
import ControlPanel from "components/ControlPanel";
import LineChartWGL from "components/UIChartsD3/LineChartSegmentsWGL";
import DialogTableSelect from "components/UIDialogTableSelect";
import LabelColoredName from "components/LabelColoredName";
import TabPanel from "components/TabPanel";
import UIRenderParameters from "components/UIRenderParameters";
import { UIButtonConvertibleToShort } from "components/UIButtons";
import { ROUTES } from "routers";
import { ElementLoader } from "components/UILoaders";
import { UISnackBar } from "components/UISnackBar";
import { getColorFromDCLFormat, getFileExtention } from "utils";
import { useRouterSearchParams, useWindowResize } from "hooks";

import { DialogFormLabel } from "components/DialogFormLabel";

import useStyles from "./TheCaptureScreenStyles";
import CaptureLabelingPanel from "./components/CaptureLabelingPanel";

import { DataManagerContext } from "../context";

const MOVING_DUBLICATELABELS = 10;
const WIDTH_FOR_SHORT_TEXT = 1280;

const TheCaptureDetailsScreen = ({
  isDisabledByAutoSession,
  isReadOnlyMode,
  selectCapture,
  selectCaptureMetadataParams,
  selectDefaultCaptureLabels,
  captureLabels,
  sensorList,
  labels,
  selectedLabelUUID,
  selectedSessionUUID,
  selectedSession,
  selectLabelValues,
  getCaptureLabelsRequestData,
  isLoadingSensorData,
  isLoadingLabel,
  isShowSessionSelector = true,
  // actions
  loadCapture,
  loadCaptureLabels,
  clearCaptureLabels,
  createCaptureLabels,
  createSession,
  createLabelValue,
  updateCaptureLabels,
  deleteCaptureLabels,
  setHasUnsavedChanges,
  setSelectedLabel,
  updateCapturesStatisticsSegments,
}) => {
  const classes = useStyles();
  const routersHistory = useHistory();
  const [search] = useRouterSearchParams();

  const { onOpenSelectSessionDialog } = useContext(DataManagerContext);
  const locationPath = useLocation();
  const { projectUUID, captureUUID } = useParams();
  const { t } = useTranslation("data-manager");

  // state
  const [isShortBtnText, setIsShortBtnText] = useState(false);
  const [isOpenDialogFormLabel, setIsOpenDialogFormLabel] = useState(false);
  const [validationError, setValidationError] = useState("");

  const [activeLabelMetadataTab, setActiveLabelMetadataTab] = useState(0);
  const [selectedCapture, setSelectedCapture] = useState({});
  const [updatedLabelData, setUpdatedLabelData] = useState({});
  const [labelData, setLabelData] = useState([]);
  const [deletedLabels, setDeletedLabels] = useState([]);

  const [editedLabel, setEditedLabel] = useState({});
  const [newLabel, setNewLabel] = useState({});
  const [sensorData, setSensorData] = useState([]);

  const [changesValidationError, setChangesValidationError] = useState("");
  const [lastLabelValueUUID, setLastLabelValueUUID] = useState("");

  const [isOpenSelectLabelDialog, setIsOpenSelectLabelDialog] = useState(false);
  const [isUpdatingData, setIsUpdatingData] = useState(false);

  const [audioFile, setAudioFile] = useState();
  const [audioFileSampleRate, setAudioFileSampleRate] = useState();

  const labelDataToRender = useMemo(() => {
    if (!_.isEmpty(labelData)) {
      return labelData
        .filter((label) => !deletedLabels.includes(label.id))
        .map((label, index) => {
          if (updatedLabelData[label.id]) {
            return { ...label, sequence: index + 1, ...updatedLabelData[label.id] };
          }
          return label;
        });
    }
    return [];
  }, [labelData, updatedLabelData, deletedLabels]);

  const labelDataToRenderSorted = useMemo(() => {
    return labelDataToRender
      .sort((a, b) => a.start - b.start)
      .map((label, index) => ({ ...label, sequence: index + 1 }));
  }, [labelDataToRender]);

  const isLoadingData = useMemo(() => {
    return isUpdatingData || isLoadingSensorData || isLoadingLabel;
  }, [isUpdatingData, isLoadingSensorData, isLoadingLabel]);

  const chartDataToRender = useMemo(() => {
    const TRASH_HOLD_AMT = 100000;

    if (!_.isEmpty(sensorData)) {
      const scaleFactor =
        sensorData[0].length / TRASH_HOLD_AMT > 1
          ? Math.round(sensorData[0].length / TRASH_HOLD_AMT)
          : 1;
      const updatedData = sensorData.map((data) =>
        _.filter(data, (dataItem, index) => index % scaleFactor === 0),
      );

      return {
        data: updatedData,
      };
    }
    return { data: [[]], names: [] };
  }, [sensorData]);

  const isHasChanges = useMemo(() => {
    const isUpdated = !_.isEmpty(updatedLabelData) || !_.isEmpty(deletedLabels);
    setHasUnsavedChanges(isUpdated);
    return isUpdated;
  }, [updatedLabelData, deletedLabels]);

  const editingLabelIndex = useMemo(() => {
    if (_.isArray(labelData)) {
      return labelDataToRenderSorted.findIndex((el) => el.id === editedLabel.id);
    }
    return -1;
  }, [editedLabel, labelDataToRenderSorted]);

  const labelsToSelect = useMemo(() => {
    return labels.map((label) => ({
      ...label,
      isSelected: label.uuid === selectedLabelUUID,
    }));
  }, [labels, selectedLabelUUID]);

  const selectedLabel = useMemo(() => {
    return labels.find((label) => label.uuid === selectedLabelUUID) || {};
  }, [labels, selectedLabelUUID]);

  const isShowSelectLabel = useMemo(() => {
    return labels?.length > 1;
  }, [labels]);

  const labelValues = useMemo(() => {
    return selectLabelValues(selectedLabelUUID);
  }, [selectedLabelUUID]);

  const getLabelNamesToCheck = useCallback(() => {
    return labelValues.map((l) => _.toLower(l.name));
  }, [labelValues]);

  const validateLabelDuplicates = (id, color, start, end) => {
    const isUnique =
      labelDataToRender.findIndex(
        (el) => el.id !== id && el.color === color && el.start === start && el.end === end,
      ) === -1;
    if (!isUnique) {
      setChangesValidationError(t("capture-screen.error-label-dublicates"));
      return false;
    }
    return true;
  };

  const handleChangeActiveProjectTab = (_event, newValue) => {
    setActiveLabelMetadataTab(newValue);
  };

  const handleDiscardChanges = () => {
    setDeletedLabels([]);
    setEditedLabel({});
    setNewLabel({});
    setUpdatedLabelData({});
    setLabelData(selectDefaultCaptureLabels(selectedSessionUUID, selectedLabelUUID));
  };

  const handleChangeCapture = () => {
    routersHistory.push({
      pathname: generatePath(ROUTES.MAIN.DATA_MANAGER.child.CAPTURES_SCREEN.path, { projectUUID }),
    });
  };
  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < WIDTH_FOR_SHORT_TEXT);
  });

  const handleMoveLabel = (start, end, id) => {
    let selectedLabelData = updatedLabelData[id];
    if (_.isEmpty(selectedLabelData)) {
      selectedLabelData = labelData.find((el) => el.id === id);
    }

    const isValid = validateLabelDuplicates(id, selectedLabelData.color, start, end);

    selectedLabelData.start = isValid ? start : start + MOVING_DUBLICATELABELS;
    selectedLabelData.end = isValid ? end : end;

    setEditedLabel(selectedLabelData);
    setUpdatedLabelData((val) => {
      const updatedVal = { ...val };
      updatedVal[id] = { ...selectedLabelData };
      return updatedVal;
    });
  };

  const handleChangeEditedLabel = ({ id, name, color, labelValueUUID, start, end }) => {
    setLastLabelValueUUID(labelValueUUID);
    let selectedLabelData = updatedLabelData[id];
    if (_.isEmpty(selectedLabelData)) {
      selectedLabelData = labelData.find((el) => el.id === id);
    }

    const defaultStart = !_.isUndefined(start) ? start : selectedLabelData.start;
    const defaultEnd = !_.isUndefined(end) ? end : selectedLabelData.end;

    const isValid = validateLabelDuplicates(id, color, defaultStart, defaultEnd);

    const newStart = isValid ? defaultStart : selectedLabelData.start + MOVING_DUBLICATELABELS;
    const newEnd = isValid ? defaultEnd : selectedLabelData.end;

    if (!_.isEmpty(editedLabel) && editedLabel?.id === id) {
      setEditedLabel({
        ...editedLabel,
        color,
        labelValueUUID,
        start: newStart,
        end: newEnd,
      });
    }
    setUpdatedLabelData((val) => {
      const updatedVal = { ...val };
      updatedVal[id] = {
        ...selectedLabelData,
        name,
        color,
        labelValueUUID,
        ...(!_.isUndefined(newStart) && { start: newStart }), // doesn't update if undefined
        ...(!_.isUndefined(newEnd) && { end: newEnd }), // doesn't update if undefined
      };
      return updatedVal;
    });
  };

  const handleCreateLabel = () => {
    setNewLabel({ id: _.uniqueId(), isCreated: true });
    setEditedLabel({});
  };

  const handleMoveNewLabel = (start, end) => {
    setNewLabel((val) => {
      const updatedVal = { ...val, start, end };
      return updatedVal;
    });
  };

  const handleSaveNewLabel = (_newLabel) => {
    setLabelData((val) => {
      const updatedVal = [...val];
      updatedVal.push(_newLabel);
      return updatedVal;
    });
    setUpdatedLabelData((val) => {
      const updatedVal = { ...val };
      updatedVal[_newLabel.id] = { ..._newLabel };
      return updatedVal;
    });
    setNewLabel({});
    setEditedLabel(_newLabel);
  };

  // label creation

  const handleOpenCreateLabelDialog = () => {
    setIsOpenDialogFormLabel(true);
  };

  const handleCloseCreateLabelDialog = () => {
    setIsOpenDialogFormLabel(false);
  };

  const handleCrateLabelValue = async (value, color) => {
    setValidationError("");
    try {
      const newLabelValueUUID = await await createLabelValue(projectUUID, selectedLabelUUID, {
        value,
        color,
      });
      handleCloseCreateLabelDialog();
      handleChangeEditedLabel({
        id: editedLabel.id,
        name: value,
        color,
        labelValueUUID: newLabelValueUUID,
      });
    } catch (_error) {
      setValidationError(_error.message);
    }
  };

  const handleChangeNewLabel = ({ name, color, labelValueUUID }) => {
    setLastLabelValueUUID(labelValueUUID);
    const updatedVal = { ...newLabel, name, color, labelValueUUID };
    if (name && color && labelValueUUID) {
      handleSaveNewLabel(updatedVal);
    }
  };

  const handleDiscartNewLabel = () => {
    setNewLabel({});
  };

  const handleDeleteEditedLabel = (id) => {
    setEditedLabel({});
    setDeletedLabels([...deletedLabels, id]);
  };

  const handleDeleteLabels = (idList) => {
    setEditedLabel({});
    setDeletedLabels([...deletedLabels, ...idList]);
  };

  const handleSaveLabelChanges = async () => {
    setIsUpdatingData(true);
    const [requestDataToUpdate, requestDataToCreate, requestDataToDelete] =
      getCaptureLabelsRequestData(captureUUID, selectedLabelUUID, updatedLabelData, deletedLabels);
    try {
      if (!_.isEmpty(requestDataToUpdate)) {
        await updateCaptureLabels(projectUUID, selectedSessionUUID, requestDataToUpdate);
        setUpdatedLabelData({});
      }
      if (!_.isEmpty(requestDataToDelete)) {
        await deleteCaptureLabels(projectUUID, selectedSessionUUID, requestDataToDelete);
        setDeletedLabels([]);
      }
      if (!_.isEmpty(requestDataToCreate)) {
        await createCaptureLabels(projectUUID, selectedSessionUUID, requestDataToCreate);
        setNewLabel({});
      }
      handleDiscardChanges();
      const updatedLabels = await loadCaptureLabels(projectUUID, captureUUID);
      updateCapturesStatisticsSegments(captureUUID, updatedLabels?.length);
    } catch (err) {
      setChangesValidationError(err.message);
    }
    setIsUpdatingData(false);
  };

  const handleSetEditedLabel = (id) => {
    const selectedLabelData = labelData.find((el) => el.id === id);
    if (editedLabel?.id !== id) {
      setEditedLabel(selectedLabelData);
    }
  };

  const handleSetEditedLabelByIndex = (index) => {
    const selectedLabelData = labelDataToRenderSorted[index];
    if (editedLabel?.id !== selectedLabelData?.id) {
      setEditedLabel(selectedLabelData);
    }
  };

  const handleDownloadFilde = () => {
    const _selectedCapture = selectCapture(captureUUID);
    loadCapture(projectUUID, captureUUID, _selectedCapture?.name, true);
  };

  const handleOpenLabelDialog = () => {
    setIsOpenSelectLabelDialog(true);
  };

  const handleCloseLabelDialog = () => {
    setIsOpenSelectLabelDialog(false);
  };

  const handleSelectLabel = (_labelUUID) => {
    search.set("label", _labelUUID);
    routersHistory.replace({
      search: search.toString(),
    });
  };

  const handleOpenSessionDialog = () => {
    onOpenSelectSessionDialog();
  };

  useEffect(() => {
    if (!selectedSessionUUID) {
      createSession(projectUUID);
    }
  }, []);

  useEffect(() => {
    const loadData = async () => {
      const _selectedCapture = selectCapture(captureUUID);
      const [data, wavFile] = await loadCapture(projectUUID, captureUUID, _selectedCapture?.name);
      const maxSequence = data[0]?.length || data?.length || 1;
      setSensorData(data);
      setSelectedCapture({ max_sequence: maxSequence - 1, ..._selectedCapture });
      if (wavFile) {
        setAudioFile(wavFile.toDataURI());
        setAudioFileSampleRate(wavFile?.fmt?.sampleRate || 16000);
      }
      const _captureLabels = await loadCaptureLabels(projectUUID, captureUUID);
      logger.logInfo("", "open_capture", {
        total_samples: _captureLabels?.length || 0,
        extension: getFileExtention(_selectedCapture?.name),
        project_uuid: projectUUID,
        capture_uuid: captureUUID,
      });
    };
    loadData();
  }, []);

  useEffect(() => {
    if (
      !_.isEmpty(labelValues) &&
      (!lastLabelValueUUID || !labelValues.find((el) => el.uuid === lastLabelValueUUID))
    ) {
      setLastLabelValueUUID(labelValues[0]?.uuid);
    }
  }, [labelValues]);

  useEffect(() => {
    const searchLabel = search.get("label");
    if (searchLabel && searchLabel !== selectedLabelUUID) {
      setSelectedLabel(searchLabel);
      handleCloseLabelDialog(false);
    }
    handleDiscardChanges();
  }, [locationPath]);

  useEffect(() => {
    // watch captureLabels and set selectDefaultCaptureLabels whic has all needed values
    if (_.isEmpty(editedLabel)) {
      setLabelData(selectDefaultCaptureLabels(selectedSessionUUID, selectedLabelUUID));
    }
  }, [captureLabels, selectedLabelUUID, selectedSessionUUID]);

  useEffect(() => {
    return () => clearCaptureLabels();
  }, []);

  useEffect(() => {
    return () => setSensorData([]);
  }, []);

  return (
    <Box>
      <Box mb={2}>
        <ControlPanel
          title={t("capture-screen.panel-title", { captureName: selectedCapture.name })}
          onClickBack={isShortBtnText ? null : handleChangeCapture}
          turncateLenght={35}
          leftColumns={4}
          rightColumns={8}
          actionsBtns={
            <>
              {isShowSessionSelector ? (
                <UIButtonConvertibleToShort
                  variant={"outlined"}
                  color={"primary"}
                  disabled={false}
                  onClick={() => handleOpenSessionDialog()}
                  isShort={isShortBtnText}
                  tooltip={"Change the session"}
                  text={t("capture-screen.panel-btn-session")}
                  icon={<LayersOutlinedIcon />}
                />
              ) : null}
              {isShowSelectLabel ? (
                <UIButtonConvertibleToShort
                  variant={"outlined"}
                  color={"primary"}
                  disabled={false}
                  onClick={() => handleOpenLabelDialog()}
                  isShort={isShortBtnText}
                  tooltip={"Change the label group"}
                  text={t("capture-screen.panel-btn-label")}
                  icon={<EditOutlinedIcon />}
                />
              ) : null}
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                disabled={false}
                onClick={() => handleDownloadFilde()}
                isShort={isShortBtnText}
                tooltip={t("capture-screen.panel-btn-download")}
                text={t("capture-screen.panel-btn-download")}
                icon={<CloudDownloadOutlinedIcon />}
              />
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                disabled={false}
                onClick={() => handleChangeCapture()}
                isShort={isShortBtnText}
                tooltip={t("capture-screen.panel-btn-change")}
                text={t("capture-screen.panel-btn-change")}
                icon={<ArrowBackIcon />}
              />
            </>
          }
        />
      </Box>
      <Box mb={1}>
        <Paper elevation={0}>
          <Box className={classes.chartInformationWrapper}>
            <Box className={classes.chartInformation}>
              {isShowSelectLabel ? (
                <Typography variant="subtitle1">
                  <span className={classes.chartInformationHeader} color="primary">
                    {`${t("capture-screen.label-goup")}:`}
                  </span>
                  {`${selectedLabel?.name}`}
                </Typography>
              ) : null}
              <Typography variant="subtitle1">
                <span className={classes.chartInformationHeader} color="primary">
                  {`${t("capture-screen.session")}:`}
                </span>
                {selectedSession?.name}
              </Typography>
            </Box>
          </Box>
        </Paper>
        <Box mt={1} className={classes.chartInformationAlertWholeLine}>
          {isDisabledByAutoSession ? (
            <Alert severity="info">{t("capture-screen.alert-auto-session")}</Alert>
          ) : null}
        </Box>
      </Box>
      <Box mb={2}>
        <Paper
          elevation={0}
          style={{
            position: "relative",
            padding: "1em",
            display: "block",
          }}
        >
          <CaptureLabelingPanel
            isDisabledByAutoSession={isDisabledByAutoSession}
            isReadOnlyMode={isReadOnlyMode}
            isHasChanges={isHasChanges}
            lastLabelValueUUID={lastLabelValueUUID}
            editedLabel={editedLabel}
            editingLabelIndex={editingLabelIndex}
            labelsCount={labelDataToRenderSorted?.length}
            newLabel={newLabel}
            labeValueOptions={labelValues}
            onOpenCreateLabelDialog={handleOpenCreateLabelDialog}
            onSetEditedLabel={handleSetEditedLabelByIndex}
            onChangeEditedLabel={handleChangeEditedLabel}
            onDeleteEditedLabel={handleDeleteEditedLabel}
            //
            onSaveChanges={handleSaveLabelChanges}
            onDiscardChanges={handleDiscardChanges}
            //
            onChangeNewLabel={handleChangeNewLabel}
            onCreateLabel={handleCreateLabel}
            onDiscardNewLabel={handleDiscartNewLabel}
            onSaveNewLabel={handleSaveNewLabel}
          />

          {!_.isEmpty(chartDataToRender.data) ? (
            <>
              <LineChartWGL
                classes={classes}
                audioFile={audioFile}
                audioFileSampleRate={audioFileSampleRate}
                data={chartDataToRender.data}
                seriesNameList={sensorList}
                segmentData={labelDataToRender}
                newSegment={newLabel}
                editingSegment={editedLabel}
                strokeWidth={4}
                onSementMove={handleMoveLabel}
                onNewSegmentMove={handleMoveNewLabel}
                onSetEditedSegment={handleSetEditedLabel}
                isReadOnlyMode={isDisabledByAutoSession}
              />
            </>
          ) : null}
          <Fade in={isLoadingData}>
            <Box className={classes.loadingBox} height={700}>
              <ElementLoader isOpen={isLoadingData} />
            </Box>
          </Fade>
        </Paper>
      </Box>
      <Box>
        <Paper elevation={0}>
          <Box mb={2}>
            <Tabs
              id="captureDetailsLabelMetadataTabs"
              value={activeLabelMetadataTab}
              onChange={handleChangeActiveProjectTab}
              indicatorColor="primary"
              textColor="primary"
              variant="scrollable"
              scrollButtons="auto"
            >
              <Tab label={"Segments"} />
              <Tab label="Metadata" />
            </Tabs>
          </Box>
        </Paper>
        <TabPanel p={0} value={activeLabelMetadataTab} index={0}>
          {!_.isEmpty(labelDataToRender) ? (
            <CaptureLabelsTable
              key={labelDataToRender?.length} // update table when delete items
              selectedCapture={selectedCapture}
              labels={{
                data: labelDataToRenderSorted,
                isFetching: isLoadingData,
              }}
              editingSegment={editedLabel}
              labeValueOptions={labelValues}
              onChangeEditedLabel={handleChangeEditedLabel}
              onDeleteLabels={handleDeleteLabels}
              onRowSelection={(_data, el) => setEditedLabel({ ...el })}
              isDisabledByAutoSession={isDisabledByAutoSession}
              isReadOnlyMode={isReadOnlyMode}
            />
          ) : null}
        </TabPanel>
        <TabPanel p={0} value={activeLabelMetadataTab} index={1}>
          <Box className={classes.captureMetadataWrapper}>
            <UIRenderParameters parameters={selectCaptureMetadataParams(captureUUID)} />
          </Box>
        </TabPanel>
      </Box>
      <UISnackBar
        isOpen={Boolean(changesValidationError)}
        onClose={(_e) => setChangesValidationError("")}
        message={changesValidationError}
        variant={"error"}
        autoHideDuration={5000}
      />
      <DialogTableSelect
        title={t("dialog-select-label.title")}
        isOpen={isOpenSelectLabelDialog}
        data={labelsToSelect}
        columns={[
          { title: t("dialog-select-label.header-name"), field: "name" },
          {
            title: t("dialog-select-label.header-labels"),
            render: (row) =>
              row.label_values.map((lv) => (
                <LabelColoredName
                  name={lv?.value || ""}
                  color={getColorFromDCLFormat(lv?.color) || ""}
                />
              )),
          },
        ]}
        onClose={handleCloseLabelDialog}
        onSelect={(row) => handleSelectLabel(row.uuid)}
      />
      {isOpenDialogFormLabel ? (
        <DialogFormLabel
          isOpen={isOpenDialogFormLabel}
          title={t("capture-chart-panel.dialog-create-label-title")}
          getLabelNamesToCheck={getLabelNamesToCheck}
          onClose={handleCloseCreateLabelDialog}
          onSubmit={handleCrateLabelValue}
          validationError={validationError}
          defaultLabelGroup={selectedLabelUUID}
        />
      ) : null}
    </Box>
  );
};

export default TheCaptureDetailsScreen;
