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
import _ from "lodash";
import { useTranslation } from "react-i18next";
import {
  Box,
  IconButton,
  Button,
  FormControlLabel,
  Checkbox,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";

import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";
import AddIcon from "@mui/icons-material/Add";
import ContentCopyOutlinedIcon from "@mui/icons-material/ContentCopyOutlined";

import useStyles from "./FormStyle";

const FormSetTransormFormAdd = ({ transforms, onClose, onSubmit, isUniqueTransforms }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const [selectedTransforms, setSelectedTransforms] = useState({});
  const [extraTransforms, setExtraTransforms] = useState([]);

  const handleSelect = (id, localId, checked) => {
    setSelectedTransforms((prevVal) => ({ ...prevVal, [localId]: { checked, id } }));
  };

  const handleSubmit = () => {
    onSubmit(
      _.values(selectedTransforms)
        .filter((value) => value?.checked)
        .map(({ id, localId }) => ({ id, localId })),
    );
  };

  const handleAddTransform = (transform) => {
    const updatedTrtansform = { ...transform, localId: _.uniqueId() };
    setExtraTransforms((_transorms) => _.orderBy(_transorms.concat(updatedTrtansform), "name"));
    setSelectedTransforms((prevVal) => ({
      ...prevVal,
      [transform.localId]: { checked: true, name: transform.name, id: transform.id },
      [updatedTrtansform.localId]: {
        checked: true,
        name: updatedTrtansform.name,
        id: transform.id,
      },
    }));
  };

  useEffect(() => {
    setExtraTransforms(transforms.map((el) => ({ ...el, localId: _.uniqueId() })));
  }, []);

  return (
    <Box>
      <TableContainer>
        <Table className={classes.table} aria-label="simple table">
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell align="right">Subtype</TableCell>
              <TableCell align="right">Dublicate</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {extraTransforms.map((row, index) => (
              <TableRow key={`${row.id}-${row.name}-${index}`}>
                <TableCell component="th" scope="row">
                  <FormControlLabel
                    className={classes.formCreateFormControl}
                    control={
                      <Checkbox
                        onChange={(e) => handleSelect(row.id, row.localId, e.target.checked)}
                        name={row.id}
                        color="primary"
                        checked={selectedTransforms[row.localId]?.checked || false}
                      />
                    }
                    label={row.name}
                  />
                </TableCell>
                <TableCell align="right">
                  <Typography paragraph className={classes.formFeatureCreateSubtype}>
                    {row.subtype}
                  </Typography>
                </TableCell>
                {!isUniqueTransforms ? (
                  <TableCell align="right">
                    <IconButton onClick={() => handleAddTransform(row, index)}>
                      <ContentCopyOutlinedIcon color="primary" />
                    </IconButton>
                  </TableCell>
                ) : null}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

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

export default FormSetTransormFormAdd;
