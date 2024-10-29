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

import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import { Box, Button, FormControlLabel, Checkbox } from "@mui/material";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";
import useStyles from "./FormStyle";

const FormCreateFromSubtype = ({ subtypes, onClose, onSubmit }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const [selectedSubtype, setSelectedSubtype] = useState({});

  const handleChange = (event) => {
    const { name, checked } = event.target;
    setSelectedSubtype((prevVal) => ({ ...prevVal, [name]: checked }));
  };

  const handleSubmit = () => {
    onSubmit(
      Object.entries(selectedSubtype)
        .filter(([_, value]) => value)
        .map(([key, _]) => key),
    );
  };

  return (
    <Box className={classes.mt1}>
      <Box className={classes.formSubtypeWrapper}>
        {subtypes.map((el, index) => (
          <FormControlLabel
            key={`checkbox_${index}`}
            control={<Checkbox onChange={handleChange} name={el} color="primary" />}
            label={el}
          />
        ))}
      </Box>
      <Box className={classes.drawerFormButtonWrapper}>
        <Button
          className={`${classes.drawerFormButton} ${classes.mr2}`}
          size="large"
          startIcon={<CancelOutlinedIcon />}
          variant="outlined"
          color="primary"
          onClick={onClose}
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
        >
          {t("model-builder.drawer-new-step-btn-add")}
        </Button>
      </Box>
    </Box>
  );
};

export default FormCreateFromSubtype;
