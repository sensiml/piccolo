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

import { Box, Button, Card, CardContent, Stack, Typography } from "@mui/material";
import { useTranslation } from "react-i18next";

import DialogFormAPIKey from "components/DialogFormAPIKey";
import PageHeader from "containers/AccountSettings/components/PageHeader";
import AccountTableAPIKeys from "components/AccountTableAPIKeys";

import useStyles from "containers/AccountSettings/AccountSettings.style";

const TheAccountAPIKeys = ({
  accountAPIKeysIsLoading,
  accountAPIKeys,
  loadAccountApiKeys,
  createAccountApiKey,
  deleteApiKey,
}) => {
  const classes = useStyles();
  const { t } = useTranslation("account");

  const [isOpenCreationForm, setIsOpenCreationForm] = useState(false);

  const handleOpenCreationForm = () => {
    setIsOpenCreationForm(true);
  };

  const handleCloseCrationForm = () => {
    setIsOpenCreationForm(false);
  };

  const handleCreateAPIKey = (name) => {
    return createAccountApiKey(name);
  };

  const APIKeyNames = useMemo(() => {
    if (!_.isUndefined(accountAPIKeys)) {
      return accountAPIKeys.map((el) => el.name);
    }
    return [];
  }, [accountAPIKeys]);

  useEffect(() => {
    loadAccountApiKeys();
  }, []);

  return (
    <>
      <Stack>
        <PageHeader
          title={t("account-api-keys.title")}
          description={t("account-api-keys.description")}
        />
        <Card variant="outlined">
          <CardContent sx={{ p: 4, mb: 5 }}>
            <Stack direction={"row"} mb={2} justifyContent={"space-between"} alignItems={"center"}>
              <Box>
                <Typography className={classes.cardTitle} mb={2} variant="h3">
                  {t("account-api-keys.header")}
                </Typography>
              </Box>
              <Button variant="outlined" color="primary" onClick={handleOpenCreationForm}>
                {t("account-api-keys.create-btn")}
              </Button>
            </Stack>
            <AccountTableAPIKeys
              isLoading={accountAPIKeysIsLoading}
              APIKeys={accountAPIKeys}
              onDeleteAPIKey={deleteApiKey}
            />
          </CardContent>
        </Card>
      </Stack>
      <DialogFormAPIKey
        title={t("account-api-keys.create-title")}
        isOpen={isOpenCreationForm}
        onClose={handleCloseCrationForm}
        onSubmit={handleCreateAPIKey}
        existingNames={APIKeyNames}
      />
    </>
  );
};

export default TheAccountAPIKeys;
