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

import React, { useEffect } from "react";
import { Box, Button, Card, CardActions, CardContent, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";
import { SUBSCRIPTION_LINK } from "config";

import PageHeader from "containers/AccountSettings/components/PageHeader";
import AccountTableCredits from "components/AccountTableCredits";
import useStyles from "containers/AccountSettings/AccountSettings.style";

const TheAccountSubscription = ({
  subscription,
  teamUsageStats,
  teamUsageStatsIsLoading,
  loadTeamInfo,
}) => {
  const classes = useStyles();
  const { t } = useTranslation("account");

  useEffect(() => {
    loadTeamInfo();
  }, []);

  return (
    <Stack>
      <PageHeader
        title={t("account-subscription.title")}
        description={t("account-subscription.description")}
      />
      <Card variant="outlined" sx={{ p: 4, mb: 5 }}>
        <Stack direction={"row"} justifyContent={"space-between"} alignItems={"center"}>
          <Box>
            <Typography className={classes.cardTitle} mb={2} variant="h3">
              {t("account-subscription.plan-header")}
            </Typography>
            <Typography className={classes.cardSubtitle} mb={2} color={"primary"} variant="body1">
              {subscription}
            </Typography>
          </Box>
          <Button variant="outlined" color="primary" target="_blank" href={SUBSCRIPTION_LINK}>
            {t("account-subscription.plan-btn")}
          </Button>
        </Stack>
      </Card>
      <Card variant="outlined">
        <CardContent sx={{ p: 4 }}>
          <Box mb={4.5}>
            <Typography className={classes.cardTitle} mb={2} variant="h3">
              {t("account-subscription.credits-plan-title")}
            </Typography>
            <Typography
              className={classes.cardSubtitle}
              mb={2}
              color={"text.secondary"}
              variant="h3"
            >
              {t("account-subscription.credits-plan-description")}
            </Typography>
            <AccountTableCredits
              teamUsageStats={teamUsageStats.filter((el) => el.isPrimary && !el.isPurchased)}
              isLoading={teamUsageStatsIsLoading}
            />
          </Box>
          <Box mb={2}>
            <Typography className={classes.cardTitle} mb={2} variant="h3">
              {t("account-subscription.credits-plan-title")}
            </Typography>
            <Typography
              className={classes.cardSubtitle}
              mb={2}
              color={"text.secondary"}
              variant="h3"
            >
              {t("account-subscription.credits-purchased-description")}
            </Typography>
            <AccountTableCredits
              teamUsageStats={teamUsageStats.filter((el) => el.isPrimary && el.isPurchased)}
              isLoading={teamUsageStatsIsLoading}
            />
          </Box>
        </CardContent>
        <CardActions className={classes.cardActions}>
          <Button color="primary" target="_blank" href={SUBSCRIPTION_LINK}>
            {t("Manage Cloud Resources")}
          </Button>
        </CardActions>
      </Card>
    </Stack>
  );
};

export default TheAccountSubscription;
