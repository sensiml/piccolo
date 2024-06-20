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
import { Alert, Box, Typography, Link } from "@mui/material";

import { useTranslation } from "react-i18next";
import ElementLoader from "components/UILoaders/ElementLoader";

import DialogInformation from "components/DialogInformation";

import makeStyles from "@mui/styles/makeStyles";

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

const DialogAccountCreditInfo = ({
  isOpen,
  isLoading,
  title,
  teamSubscription,
  plansLink,
  teamUsageStats,
  onClose,
}) => {
  const { t } = useTranslation("team");
  const classes = useStyles();

  return (
    <DialogInformation isOpen={isOpen} onClose={onClose}>
      <Box>
        {title ? (
          <Typography variant="h2" className={classes.infoTitle}>
            {title}
          </Typography>
        ) : null}
        <Box mt={1} mb={2}>
          <Alert severity="info">
            {t("dialog-account-credits.description-plan")}
            {": "}
            <b>{t(`subscriptions.${teamSubscription}`)}</b>
            <br />
            {t("dialog-account-credits.description-text")}{" "}
            <Link href={plansLink} alt={plansLink} target="_blank">
              {plansLink}
            </Link>
          </Alert>
        </Box>
        {isLoading ? (
          <ElementLoader isOpen={true} />
        ) : (
          <Box className={classes.dialogTable} display="table">
            <Box className={classes.dialogTableRow} display="table-row">
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <b>{t("dialog-account-credits.type-subscription")}</b>
              </Typography>
              <Typography variant="subtitle1" className={classes.utitCell} gutterBottom>
                <b>{t("dialog-account-credits.header-credits")}</b>
              </Typography>
              <Typography variant="subtitle1" className={classes.utitCell} gutterBottom>
                <b>{t("dialog-account-credits.header-credits-used")}</b>
              </Typography>
              <Typography variant="subtitle1" className={classes.utitCell} gutterBottom>
                <b>{`${t("dialog-account-credits.header-usage")} %`}</b>
              </Typography>
            </Box>
            {teamUsageStats
              .filter((el) => el.isPrimary && !el.isPurchased)
              .map((el, index) => (
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
            <Box className={classes.dialogTableRow} display="table-row">
              <Typography variant="subtitle1" color="primary" gutterBottom>
                <b>{t("dialog-account-credits.type-purchased")}</b>
              </Typography>
            </Box>
            {teamUsageStats
              .filter((el) => el.isPrimary && el.isPurchased)
              .map((el, index) => (
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
      </Box>
    </DialogInformation>
  );
};

export default DialogAccountCreditInfo;
