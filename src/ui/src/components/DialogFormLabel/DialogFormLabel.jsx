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
import PropTypes from "prop-types";

import { Box, DialogContentText, Button, TextField } from "@mui/material";
import { useTranslation } from "react-i18next";

import InputColorPicker from "components/FormElements/InputColorPicker";
import SelectForm from "components/FormElements/SelectForm";
import UIDialogForm from "components/UIDialogFormMedium";

import { getColorByIndex, DEFAULT_COLORS, DEFALULT_LABEL } from "store/labels/domain";
import { ElementLoader } from "components/UILoaders";

const DialogFormLabel = ({
  isOpen,
  title,
  description,
  labelName,
  defaultLabelColor,
  getLabelNamesToCheck,
  labelGroupOptions,
  defaultLabelGroup,
  onClose,
  onSubmit,
  validationError,
}) => {
  const { t } = useTranslation("components");

  const [name, setName] = useState();
  const [color, setColor] = useState();
  const [error, setError] = useState();

  const [labelGroupUUID, setLabelGroupUUID] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const labelNameToCheck = useMemo(() => {
    return getLabelNamesToCheck(labelGroupUUID || defaultLabelGroup).filter(
      (elName) => elName !== _.toLower(labelName) && elName !== _.toLower(DEFALULT_LABEL.value),
    );
  }, [labelGroupUUID, defaultLabelGroup, labelName, getLabelNamesToCheck]);

  const labelColor = useMemo(() => {
    return color || defaultLabelColor || getColorByIndex(labelNameToCheck.length);
  }, [color, labelNameToCheck, defaultLabelColor]);

  const validateName = (_name) => {
    if (!_name) {
      setError(t("dialog-form-label.validation-error-empty"));
      return false;
    }
    if (labelNameToCheck.includes(_.toLower(_name))) {
      setError(t("dialog-form-label.validation-error-duplicate", { labelName: _name }));
      return false;
    }
    return true;
  };

  const handleChangeName = (e) => {
    setError("");
    setName(e?.target?.value);
  };

  const handleUpdateColor = (selectedColor) => {
    setColor(selectedColor);
  };

  const handleChangeLabelGroup = (_name, _value) => {
    setError("");
    setLabelGroupUUID(_value);
  };

  const handleClose = () => {
    onClose();
  };

  const handleSubmit = () => {
    if (validateName(name)) {
      setIsLoading(true);
      onSubmit(name, labelColor, labelGroupUUID);
    }
  };

  const clearComponent = () => {
    setIsLoading(false);
    setError("");
    setName("");
  };

  useEffect(() => {
    if (validationError) {
      setIsLoading(false);
      setError(validationError);
    }
  }, [validationError]);

  useEffect(() => {
    setName(labelName);
  }, [labelName]);

  useEffect(() => {
    if (!isOpen) {
      clearComponent();
    }
  }, [isOpen]);

  useEffect(() => {
    return () => clearComponent();
  }, []);

  return (
    <UIDialogForm
      disableEscapeKeyDown
      isOpen={isOpen}
      onClose={handleClose}
      title={title}
      actionsComponent={
        <>
          <Button onClick={handleClose} color="primary" variant="outlined" fullWidth>
            {t("Cancel")}
          </Button>
          <Button onClick={handleSubmit} color="primary" variant="contained" fullWidth>
            {t("Save")}
          </Button>
        </>
      }
    >
      <>
        {isLoading ? (
          <ElementLoader isOpen={true} />
        ) : (
          <>
            <DialogContentText id="form-dialog-content">{description}</DialogContentText>
            {labelGroupOptions?.length > 1 && !labelName ? (
              /* hide label group select if label is being edited or if there is only one label
                 group */
              <Box mb={2}>
                <SelectForm
                  id="select_label"
                  name="select_label"
                  label={t("dialog-form-label.label-group")}
                  options={labelGroupOptions}
                  variant={"outlined"}
                  margin="dense"
                  defaultValue={defaultLabelGroup}
                  onChange={handleChangeLabelGroup}
                />
              </Box>
            ) : null}
            <Box marginBottom={2}>
              <TextField
                error={Boolean(error)}
                helperText={error}
                autoFocus
                margin="dense"
                id="DialogFormlabelName"
                label={t("dialog-form-label.label-name")}
                required
                defaultValue={labelName}
                onChange={handleChangeName}
                fullWidth
                variant="outlined"
              />
            </Box>
            <Box marginBottom={2}>
              <InputColorPicker
                presetColors={DEFAULT_COLORS}
                defautColor={labelColor}
                label={t("dialog-form-label.label-color")}
                onUpdate={handleUpdateColor}
              />
            </Box>
          </>
        )}
      </>
    </UIDialogForm>
  );
};

DialogFormLabel.propTypes = {
  onSubmit: PropTypes.func,
  onClose: PropTypes.func,
};

DialogFormLabel.defaultProps = {
  onSubmit: () => {},
  onClose: () => {},
};

export default DialogFormLabel;
