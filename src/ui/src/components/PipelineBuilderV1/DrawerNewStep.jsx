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

import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  Drawer,
  Box,
  Typography,
  FormControl,
  FormHelperText,
  Select,
  MenuItem,
  InputLabel,
  Button,
  Link,
} from "@mui/material";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";
import { useTheme } from "@mui/material/styles";

import useStyles from "./BuildModeStyle";

const DrawerNewStep = ({
  isOpen,
  onClose,
  onChangeStep,
  onCreate,
  getPipelineStepDescription,
  allSteps,
  availableSteps = [],
}) => {
  const classes = useStyles();
  const theme = useTheme();
  const { t } = useTranslation("models");
  const [newStep, setNewStep] = useState("");
  const [newStepName, setNewStepName] = useState("");

  const [newStepDescription, setNewStepDescription] = useState("");
  const [newStepDockLink, setNewStepDockLink] = useState("");

  const [isNewStepNameError, setIsNewStepNameError] = useState(false);

  useEffect(() => {
    if (availableSteps) {
      setNewStep({});
    }
  }, [availableSteps]);

  useEffect(() => {
    // call external step update
    if (newStep) {
      setIsNewStepNameError(false);
      onChangeStep(newStep);
    }
  }, [newStep]);

  const getStepValueByName = (name) => {
    return allSteps.find((el) => el.name?.trim() === name);
  };

  const handleSelectStep = (e) => {
    const { descpription, docLink } = getPipelineStepDescription(e.target.value);
    setNewStepName(e.target.value);
    setNewStep({
      ...getStepValueByName(e.target.value),
    });
    setNewStepDescription(descpription);
    setNewStepDockLink(docLink);
  };

  const handleSubmit = () => {
    if (!newStepName) {
      setIsNewStepNameError(true);
    } else {
      onCreate();
    }
  };

  return (
    <Drawer
      BackdropProps={{ style: { backgroundColor: theme.backgroundBackDoor } }}
      classes={{
        paperAnchorRight: classes.formDrawerSizing,
      }}
      open={isOpen}
      onClose={onClose}
      anchor={"right"}
      variant="temporary"
    >
      <Box data-test={"drawer-create-step-form"} className={classes.formStepDrawerContext}>
        <Typography variant="h2" className={classes.drawerHeader}>
          {t("model-builder.drawer-new-step-header")}
        </Typography>
        <Typography paragraph className={classes.drawerInfoText}>
          {t("model-builder.drawer-new-step-sub-header")}
        </Typography>
        {availableSteps ? (
          <FormControl
            required
            fullWidth={true}
            className={classes.formControl}
            error={isNewStepNameError}
          >
            <InputLabel htmlFor="select_pipeline">
              {t("model-builder.drawer-new-step-label-select")}
            </InputLabel>
            <Select
              name={"select_pipeline"}
              onChange={handleSelectStep}
              value={newStepName}
              data-testid={"select-tranform"}
            >
              {availableSteps.map((name, ind) => (
                <MenuItem data-test={"select-tranform-option"} value={name} key={`select_${ind}`}>
                  {name}
                </MenuItem>
              ))}
            </Select>
            {isNewStepNameError ? (
              <FormHelperText>{t("model-builder.drawer-new-error-error-requaried")}</FormHelperText>
            ) : null}
          </FormControl>
        ) : null}
        <Box className={classes.drawerInfoText}>
          <Typography paragraph className={classes.drawerContent}>
            {newStepDescription}
          </Typography>
          {newStepDockLink ? (
            <Typography paragraph className={classes.drawerContent}>
              <Link href={newStepDockLink} title={newStepDockLink} target="_blank">
                {t("model-builder.drawer-step-info-doc-link")}
              </Link>
            </Typography>
          ) : null}
        </Box>
        <Box className={classes.drawerFormButtonWrapper}>
          <Button
            className={`${classes.drawerFormButton} ${classes.mr2}`}
            size="large"
            startIcon={<CancelOutlinedIcon />}
            variant="outlined"
            color="primary"
            onClick={onClose}
            data-testid={"new-step-drawer-close"}
          >
            {t("model-builder.drawer-new-step-btn-cancel")}
          </Button>
          <Button
            onClick={handleSubmit}
            className={classes.drawerFormButton}
            size="large"
            startIcon={<AddIcon />}
            variant="contained"
            color="primary"
            data-testid={"new-step-drawer-create"}
          >
            {t("model-builder.drawer-new-step-btn-add")}
          </Button>
        </Box>
      </Box>
    </Drawer>
  );
};

export default DrawerNewStep;
