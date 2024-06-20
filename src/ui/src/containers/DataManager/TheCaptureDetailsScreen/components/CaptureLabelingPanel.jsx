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

/* eslint-disable no-unused-vars */
import React, { useMemo, useState } from "react";
import _ from "lodash";
import Alert from "@mui/material/Alert";
import PropTypes from "prop-types";

import SaveIcon from "@mui/icons-material/Save";
import DeleteIcon from "@mui/icons-material/Delete";
import UndoIcon from "@mui/icons-material/Undo";
import ArrowBack from "@mui/icons-material/ArrowBack";
import ArrowForward from "@mui/icons-material/ArrowForward";
import AddIcon from "@mui/icons-material/Add";

import { useTranslation } from "react-i18next";
import { Box, Button, Paper } from "@mui/material";

import LabelColoredName from "components/LabelColoredName";
import SelectForm from "components/FormElements/SelectForm";

import { IconButtonRounded, UIButtonConvertibleToShort } from "components/UIButtons";
import { useWindowResize } from "hooks";

import useStyles from "../TheCaptureScreenStyles";

const WIDTH_FOR_SHORT_TEXT = 1850;

const CaptureLabelingPanel = ({
  isDisabledByAutoSession,
  isReadOnlyMode,
  isHasChanges,
  editedLabel,
  editingLabelIndex,
  labelsCount,
  newLabel,
  lastLabelValueUUID,
  labeValueOptions,
  onSetEditedLabel,
  onOpenCreateLabelDialog,
  onChangeEditedLabel,
  onDeleteEditedLabel,
  onSaveChanges,
  onDiscardChanges,
  onChangeNewLabel,
  onCreateLabel,
  onDiscardNewLabel,
}) => {
  const classes = useStyles();

  const { t } = useTranslation("data-manager");

  const [isShortBtnText, setIsShortBtnText] = useState(false);

  const labelToRenderCoordinates = useMemo(() => {
    if (editedLabel?.start && editedLabel?.end) {
      return editedLabel;
    }
    if (newLabel?.start && newLabel?.end) {
      return newLabel;
    }
    return {};
  }, [editedLabel, newLabel]);

  const isDisabledPrevButton = useMemo(() => {
    return editingLabelIndex === 0;
  }, [editingLabelIndex]);

  const isDisabledNextButton = useMemo(() => {
    return editingLabelIndex === labelsCount - 1;
  }, [editedLabel, editingLabelIndex, labelsCount]);

  const activeSegmentLength = useMemo(() => {
    return Number(labelToRenderCoordinates.end) + 1 - Number(labelToRenderCoordinates.start);
  }, [labelToRenderCoordinates]);

  const handleSetEditedLabel = (index) => {
    onSetEditedLabel(index);
  };

  const handleChangeNewLabel = (id, labelValueUUID) => {
    const { color, name, uuid } =
      labeValueOptions.find((labelValue) => labelValue.uuid === labelValueUUID) || {};
    onChangeNewLabel({ name, color, uuid, labelValueUUID });
  };

  const handleChangeEditedLabel = (id, labelValueUUID) => {
    const { color, name, uuid } =
      labeValueOptions.find((labelValue) => labelValue.uuid === labelValueUUID) || {};
    onChangeEditedLabel({ id, name, color, uuid, labelValueUUID });
  };

  const handleDeleteLabel = () => {
    onDeleteEditedLabel(editedLabel.id);
  };

  const handleDiscardChanges = () => {
    onDiscardChanges();
  };

  const handleCreateLabel = () => {
    onCreateLabel();
  };

  const handleCancelCreationLabel = () => {
    onDiscardNewLabel();
  };

  useWindowResize((data) => {
    setIsShortBtnText(data.innerWidth < WIDTH_FOR_SHORT_TEXT);
  });

  return (
    <>
      <Box className={classes.segmentsChartPanelWrapper}>
        {!_.isEmpty(labelToRenderCoordinates) ? (
          <Box
            display={"flex"}
            justifyContent={"center"}
            className={classes.segmentsChartPanelCenterWrap}
          >
            <IconButtonRounded
              disabled={isDisabledPrevButton}
              onClick={(_e) => handleSetEditedLabel(editingLabelIndex - 1)}
            >
              <ArrowBack />
            </IconButtonRounded>
            <Box className={classes.cordinateWrap}>
              <Box>
                {labelToRenderCoordinates?.start.toLocaleString()} -{" "}
                {labelToRenderCoordinates?.end.toLocaleString()}
              </Box>
              <Box>{activeSegmentLength}</Box>
            </Box>
            <IconButtonRounded
              disabled={isDisabledNextButton}
              onClick={(_e) => handleSetEditedLabel(editingLabelIndex + 1)}
            >
              <ArrowForward />
            </IconButtonRounded>
          </Box>
        ) : null}
        {!_.isEmpty(newLabel) ? (
          newLabel?.start ? (
            <Box className={classes.labelWrapper}>
              <SelectForm
                className={classes.labelSelector}
                id={"select_label"}
                fullWidth
                name={newLabel.id}
                key={newLabel.id}
                label="Selected label"
                variant="outlined"
                addBtnText={t("capture-chart-panel.btn-add-label")}
                onClickAdd={onOpenCreateLabelDialog}
                defaultValue={newLabel?.labelValueUUID || lastLabelValueUUID}
                isObserveDefaultValue
                options={labeValueOptions.map((el) => ({
                  name: <LabelColoredName name={el?.name} color={el?.color} />,
                  value: el?.uuid,
                }))}
                onChange={handleChangeNewLabel}
                isUpdateWithDefault={true}
                disabled={isReadOnlyMode}
              />
            </Box>
          ) : (
            <Box className={classes.segmentsAlterWrapper}>
              <Alert severity="info">{t("capture-chart-panel.alert-info-editing-label")}</Alert>
            </Box>
          )
        ) : !_.isEmpty(editedLabel) ? (
          <Box className={classes.labelWrapper}>
            <SelectForm
              className={classes.labelSelector}
              id={"select_query"}
              fullWidth
              labelId={"select_query_label"}
              name={editedLabel.id}
              variant="outlined"
              label=""
              addBtnText={t("capture-chart-panel.btn-add-label")}
              onClickAdd={onOpenCreateLabelDialog}
              defaultValue={editedLabel?.labelValueUUID || lastLabelValueUUID}
              isObserveDefaultValue
              options={labeValueOptions.map((el) => ({
                name: <LabelColoredName name={el?.name} color={el?.color} />,
                value: el?.uuid,
              }))}
              onChange={handleChangeEditedLabel}
              isUpdateWithDefault={false}
              disabled={isReadOnlyMode}
            />
          </Box>
        ) : (
          <Box className={classes.segmentsAlterWrapper}>
            <Alert severity="info">{t("capture-chart-panel.alert-info-creating-label")}</Alert>
          </Box>
        )}

        <Box className={classes.labelingPanelActionWrapper}>
          {_.isEmpty(newLabel) ? (
            <>
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                size={"large"}
                disabled={isDisabledByAutoSession || isReadOnlyMode}
                onClick={handleCreateLabel}
                isShort={isShortBtnText}
                tooltip={t("capture-chart-panel.btn-create-label-tooltip")}
                text={t("capture-chart-panel.btn-create-label")}
                icon={<AddIcon />}
              />
              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                size={"large"}
                disabled={_.isEmpty(editedLabel) || isDisabledByAutoSession || isReadOnlyMode}
                onClick={handleDeleteLabel}
                isShort={isShortBtnText}
                tooltip={t("capture-chart-panel.btn-delete-label-tooltip")}
                text={t("capture-chart-panel.btn-delete-label")}
                icon={<DeleteIcon />}
              />

              <UIButtonConvertibleToShort
                variant={"outlined"}
                color={"primary"}
                size={"large"}
                disabled={!isHasChanges || isReadOnlyMode}
                onClick={handleDiscardChanges}
                isShort={isShortBtnText}
                tooltip={t("capture-chart-panel.btn-discard-tooltip")}
                text={t("capture-chart-panel.btn-discard")}
                icon={<UndoIcon />}
              />

              <UIButtonConvertibleToShort
                variant={"contained"}
                color={"primary"}
                size={"large"}
                disabled={!isHasChanges || isReadOnlyMode}
                onClick={onSaveChanges}
                isShort={isShortBtnText}
                tooltip={t("capture-chart-panel.btn-save-tooltip")}
                text={t("capture-chart-panel.btn-save")}
                icon={<SaveIcon />}
              />
            </>
          ) : (
            <>
              <Button variant={"outlined"} color={"primary"} onClick={handleCancelCreationLabel}>
                {t("capture-chart-panel.btn-create-cancel")}
              </Button>
            </>
          )}
        </Box>
      </Box>
    </>
  );
};

CaptureLabelingPanel.propTypes = {
  onChangeEditedLabel: PropTypes.func,
  labeValueOptions: PropTypes.array.isRequired,
  editedLabel: PropTypes.object.isRequired,
};

CaptureLabelingPanel.defaultProps = {
  onChangeEditedLabel: () => {},
};

export default CaptureLabelingPanel;
