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

import React from "react";

import makeStyles from "@mui/styles/makeStyles";
import { useTranslation } from "react-i18next";
import { Box, Typography, Skeleton } from "@mui/material";

const useStyles = () =>
  makeStyles((theme) => ({
    infoTitle: {
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(4),
      fontWeight: 500,
      textAlign: "center",
    },
    dialogTable: {
      width: "100%",
    },
    dialogTableRow: {
      "& h6": {
        display: "table-cell",
        padding: theme.spacing(0.5),
      },
    },
    utitCell: {
      textAlign: "end",
    },
  }))();

const AccountTableCredits = ({ teamUsageStats, isLoading }) => {
  const { t } = useTranslation("components");
  const classes = useStyles();

  return (
    <>
      {isLoading ? (
        <>
          <Skeleton animation="wave" width={"100%"} />
          <Skeleton animation="wave" width={"100%"} />
          <Skeleton animation="wave" width={"100%"} />
        </>
      ) : (
        <Box className={classes.dialogTable} display="table">
          <Box className={classes.dialogTableRow} display="table-row">
            <Typography variant="subtitle1" color="primary" gutterBottom>
              <b>{t("account-table-credits.cloud-resources")}</b>
            </Typography>
            <Typography
              variant="subtitle1"
              color="primary"
              className={classes.utitCell}
              gutterBottom
            >
              <b>{t("account-table-credits.limit")}</b>
            </Typography>
            <Typography
              variant="subtitle1"
              color="primary"
              className={classes.utitCell}
              gutterBottom
            >
              <b>{t("account-table-credits.used")}</b>
            </Typography>
            <Typography
              variant="subtitle1"
              color="primary"
              className={classes.utitCell}
              gutterBottom
            >
              <b>{t("account-table-credits.usage")}</b>
            </Typography>
          </Box>
          {teamUsageStats.map((el, index) => (
            <Box key={`ename_${index}`} display="table-row" className={classes.dialogTableRow}>
              <Typography variant="subtitle1" gutterBottom>
                {el.name}
              </Typography>
              <Typography variant="subtitle1" className={classes.utitCell} gutterBottom>
                {`${el.credits} ${el.unit || ""}`}
              </Typography>
              <Typography variant="subtitle1" className={classes.utitCell} gutterBottom>
                {`${el.creditsUsage} ${el.unit || ""}`}
              </Typography>
              <Typography variant="subtitle1" className={classes.utitCell} gutterBottom>
                {`${el.persantage} %`}
              </Typography>
            </Box>
          ))}
        </Box>
      )}
    </>
  );
};

export default AccountTableCredits;
