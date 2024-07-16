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

import React, { useMemo } from "react";
import { Card, Box, Button, Stack, Typography, CardContent } from "@mui/material";
import { useTranslation } from "react-i18next";

import PageHeader from "containers/AccountSettings/components/PageHeader";
import useStyles from "containers/AccountSettings/AccountSettings.style";
import { CHANGE_PASSWORD_LINK } from "config";

const TheAccountInfo = ({ userId, teamName }) => {
  const classes = useStyles();
  const { t } = useTranslation("account");

  const infoItems = useMemo(() => {
    const _infoItems = [{ type: t("account-info.basic-info-email"), value: userId }];
    if (teamName) {
      _infoItems.push({ type: t("account-info.basic-info-team"), value: teamName });
      return _infoItems;
    }
    return _infoItems;
  }, [teamName, userId]);

  return (
    <Stack>
      <PageHeader title={t("account-info.title")} description={t("account-info.description")} />
      <Box
        display={"grid"}
        gridTemplateColumns={"repeat(auto-fit, minmax(280px, 1fr))"}
        gap={"2rem"}
      >
        <Card variant="outlined">
          <CardContent sx={{ p: 4, pb: 4 }}>
            <Typography className={classes.cardTitle} mb={4} variant="h3">
              {t("account-info.basic-info-header")}
            </Typography>
            {infoItems &&
              infoItems.map((el, index) => (
                <Stack key={`info-item-${index}`} mb={3} spacing={2} direction={"row"}>
                  <Typography className={classes.cartItemKey} variant="body1" component="div">
                    {el.type}
                  </Typography>
                  <Typography className={classes.cartItemValue} component="div">
                    {el.value}
                  </Typography>
                </Stack>
              ))}
          </CardContent>
        </Card>
        <Card variant="outlined">
          <CardContent sx={{ p: 4 }}>
            <Typography className={classes.cardTitle} variant="h3">
              {t("account-info.password-header")}
            </Typography>
            <Stack mb={3} spacing={2} direction={"row"} alignItems={"center"}>
              <Typography className={classes.cartItemValue} component="div">
                {"************"}
              </Typography>
              <Button
                variant="outlined"
                color="primary"
                target="_blank"
                href={CHANGE_PASSWORD_LINK}
              >
                {t("account-info.change-password-btn")}
              </Button>
            </Stack>
          </CardContent>
        </Card>
      </Box>
    </Stack>
  );
};

export default TheAccountInfo;
