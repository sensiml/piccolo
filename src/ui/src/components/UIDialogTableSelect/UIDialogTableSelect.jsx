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
import React from "react";

import makeStyles from "@mui/styles/makeStyles";

import { Box, Button, Typography, Tooltip } from "@mui/material";
import { useTranslation } from "react-i18next";

import DialogInformation from "components/DialogInformation";

const useStyles = () =>
  makeStyles((theme) => ({
    ///
    infoTitle: {
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(4),
      fontWeight: 500,
      textAlign: "center",
    },
    dialogTable: {
      marginTop: theme.spacing(1),
      width: "100%",
    },
    selectedRow: {
      background: "#76ccfd24",
    },
    dialogTableRow: {
      "& h6": {
        display: "table-cell",
        padding: theme.spacing(0.5),
        borderBottom: "1px solid silver",
      },
    },
    utitCell: {
      width: "100px",
      textAlign: "center",
    },
  }))();

const UIDialogTableSelect = ({ title, isOpen, columns = [], data = [], onClose, onSelect }) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  return (
    <DialogInformation isOpen={isOpen} onClose={onClose}>
      <Box>
        <Typography variant="h2" className={classes.infoTitle}>
          {title}
        </Typography>
        <Box className={classes.dialogTable} display="table">
          <Box className={classes.dialogTableRow} display="table-row">
            {columns.map((el) => (
              <Typography key={`header_${el.field}`} variant="subtitle1" gutterBottom>
                <b>{el.title}</b>
              </Typography>
            ))}
            <Typography key={`header_select_empty`} variant="subtitle1" gutterBottom>
              {""}
            </Typography>
          </Box>
          {data.map((row, index) => (
            <Box
              key={`row_${index}`}
              display="table-row"
              className={`${classes.dialogTableRow} ${row?.isSelected && classes.selectedRow}`}
            >
              {columns.map((column, columnIndex) => (
                <Typography key={`${column.field}-${columnIndex}`} variant="subtitle1" gutterBottom>
                  {column?.render ? column?.render(row) : row[column.field]}
                </Typography>
              ))}

              <Typography variant="subtitle1" gutterBottom>
                <Tooltip title={t("dialog-table-select.btn-select-tooltip")}>
                  <span>
                    <Button
                      variant="outlined"
                      color="primary"
                      onClick={() => onSelect(row)}
                      disabled={row?.isSelected || false}
                    >
                      {row?.isSelected
                        ? t("dialog-table-select.btn-selected")
                        : t("dialog-table-select.btn-select")}
                    </Button>
                  </span>
                </Tooltip>
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </DialogInformation>
  );
};

export default UIDialogTableSelect;
