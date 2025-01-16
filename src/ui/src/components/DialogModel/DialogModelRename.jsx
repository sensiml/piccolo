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

import _ from "lodash";
import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Button,
  TextField,
} from "@mui/material";
import AddBoxIcon from "@mui/icons-material/AddBox";
import CancelIcon from "@mui/icons-material/Cancel";
import { useTranslation } from "react-i18next";

const DialogModalRename = ({
  isOpen,
  parrentError,
  modelName,
  modelList,
  selectedModel,
  selectedPipeline,
  onClose,
  onSave,
}) => {
  const { t } = useTranslation("models");

  const [newModelName, setNewModelName] = useState();
  const [error, setError] = useState();

  useEffect(() => {
    setNewModelName(modelName);
  }, [modelName]);

  useEffect(() => {
    setError(parrentError);
  }, [parrentError]);

  const handleChangeModelName = (e) => {
    e.preventDefault();
    const { value } = e.target;
    setNewModelName(value);
  };

  const handleSave = async () => {
    const findInModelList = () =>
      modelList.find(
        (e) =>
          e.name.toUpperCase() === newModelName.toUpperCase() &&
          e.sandbox_uuid === selectedPipeline,
      );

    if (!newModelName) {
      setError(t("dialog-rename-models-error-required"));
      return;
    }

    if (_.isArray(modelList) && findInModelList()) {
      setError(t("dialog-rename-models-error-exist", { newModelName }));
      return;
    }
    const kp = modelList.find((model) => model.uuid === selectedModel);
    const re = new RegExp(`^${kp.name}_`, "g");
    const kpsToRename = [{ uuid: selectedModel, newName: newModelName }];

    if (!_.isEmpty(kp?.knowledgepack_description)) {
      _.keys(kp.knowledgepack_description).forEach((modelNameDesc) => {
        if (modelNameDesc !== "Parent") {
          const newKpName = `${newModelName}_${modelNameDesc.replace(re, "")}`;
          if (newKpName.length > 40) {
            setError(t("dialog-rename-models-error-limit", { newModelName }));
            return;
          }
          kpsToRename.push({
            uuid: kp.knowledgepack_description[modelNameDesc].uuid,
            newName: newKpName,
          });
        }
      });
    }

    onSave(kpsToRename);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSave();
  };

  return (
    <Dialog
      disableEscapeKeyDown
      open={isOpen}
      onClose={onClose}
      id="renameKnowledgePack"
      aria-labelledby="form-dialog-title"
    >
      <DialogTitle id="form-dialog-title">{t("dialog-rename-models-title")}</DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          <DialogContentText id="form-dialog-content">
            {t("dialog-rename-models-subtitle")}
          </DialogContentText>
          <TextField
            error={Boolean(error)}
            helperText={error}
            autoFocus
            margin="dense"
            id="newKnowledgepackName"
            label="Name"
            required
            defaultValue={modelName}
            onChange={handleChangeModelName}
            fullWidth
          />
        </DialogContent>
        <DialogActions id="renameKnowledgepackActions">
          <Button onClick={onClose} startIcon={<CancelIcon />} color="primary" variant="outlined">
            {t("dialog-rename-models-cancel-btn")}
          </Button>
          <Button
            type="submit"
            // onClick={onSave}
            startIcon={<AddBoxIcon />}
            color="primary"
            variant="outlined"
          >
            {t("dialog-rename-models-confirm-btn")}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
};

export default DialogModalRename;
