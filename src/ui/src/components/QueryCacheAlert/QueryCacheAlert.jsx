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

/* eslint-disable no-use-before-define */
/* eslint-disable no-unused-vars */
import React, { useState, useEffect, useCallback } from "react";

import AutorenewOutlinedIcon from "@mui/icons-material/AutorenewOutlined";

import { Alert, AlertTitle, Button, Box } from "@mui/material";
import { useTranslation } from "react-i18next";
import { useInterval } from "hooks";

import { AppLoader } from "components/UILoaders";

import { CACHE_STATUSES } from "store/queries/const";
import useStyles from "./QueryCacheAlertStyles";

const QueryCacheAlert = ({
  title,
  isNewQuery,
  selectedQuery,
  queryCacheStatusData,
  loadQuery,
  onBuildCache,
  onDismiss,
  isButtonsPanel,
}) => {
  const { t } = useTranslation("queries");
  const classes = useStyles();
  const [panelAlertStatus, setPanelAlertStatus] = useState("");
  const [panelAlertMessage, setPanelAlertMessage] = useState("");
  const [isShowAlertRebuildBtn, setIsShowAlertRebuildBtn] = useState(false);
  const [isQueryCacheBuilding, setIsQueryCacheBuilding] = useState(false);

  const setPanelStatus = () => {
    if (isNewQuery) {
      // is new query
      setPanelAlertStatus("info");
      setPanelAlertMessage(t("create-form.message-info"));
      setIsShowAlertRebuildBtn(false);
    } else if (
      queryCacheStatusData.status &&
      queryCacheStatusData.build_status === CACHE_STATUSES.CACHED
    ) {
      // if is up to date
      setPanelAlertStatus("success");
      setPanelAlertMessage(queryCacheStatusData.message);
      setIsShowAlertRebuildBtn(false);
    } else if (
      !queryCacheStatusData.status &&
      queryCacheStatusData.build_status === CACHE_STATUSES.CACHED
    ) {
      // if is not up to date
      setPanelAlertStatus("warning");
      setPanelAlertMessage(queryCacheStatusData.message);
      setIsShowAlertRebuildBtn(true);
    } else if (queryCacheStatusData.build_status === CACHE_STATUSES.BUILDING) {
      // if non cached data
      setPanelAlertStatus("info");
      setPanelAlertMessage(queryCacheStatusData.message);
      setIsQueryCacheBuilding(true);
      setIsShowAlertRebuildBtn(true);
    } else if (queryCacheStatusData.build_status === CACHE_STATUSES.NOT_BUILT) {
      // if non cached data
      setPanelAlertStatus("info");
      setPanelAlertMessage(queryCacheStatusData.message);
      setIsShowAlertRebuildBtn(true);
    } else if (queryCacheStatusData.build_status === CACHE_STATUSES.FAILED) {
      // if non cached data
      setPanelAlertStatus("error");
      setPanelAlertMessage(queryCacheStatusData.message);
      setIsShowAlertRebuildBtn(true);
    }
  };

  const getCacheStatus = () => {
    loadQuery(selectedQuery);
  };

  const getIsShowButtonPanel = useCallback(() => {
    return isShowAlertRebuildBtn;
  }, [isShowAlertRebuildBtn, queryCacheStatusData]);

  useInterval(
    async () => {
      await getCacheStatus();
    },
    isQueryCacheBuilding ? 5000 : null,
  );

  useEffect(() => {
    setPanelStatus();
  }, [queryCacheStatusData, isNewQuery, selectedQuery]);

  useEffect(() => {
    setPanelStatus();
  }, []);

  useEffect(() => {
    if (queryCacheStatusData.build_status !== CACHE_STATUSES.BUILDING) {
      setIsQueryCacheBuilding(false);
    }
  }, [queryCacheStatusData]);

  const handleBuildCache = () => {
    if (!isQueryCacheBuilding) {
      onBuildCache(selectedQuery);
      setIsQueryCacheBuilding(true);
    }
  };

  const handleDismiss = () => {
    if (!isQueryCacheBuilding) {
      onDismiss(selectedQuery);
    }
  };

  const renderButtons = () => (
    <>
      <Button
        id="build_cache_btn"
        data-testid="build_cache_btn"
        disabled={isQueryCacheBuilding}
        color="primary"
        className={classes.actionButtons}
        size="small"
        onClick={handleBuildCache}
        variant="outlined"
      >
        {t("cache.button-cache-rebuild")}
      </Button>
      {onDismiss ? (
        <Button
          id="dismiss_btn"
          data-testid="dismiss_btn"
          disabled={
            isQueryCacheBuilding || queryCacheStatusData.build_status === CACHE_STATUSES.FAILED
          }
          className={`${classes.actionButtons} ${classes.dismissButton}`}
          color="accent"
          size="small"
          onClick={handleDismiss}
          variant="outlined"
        >
          {t("cache.button-cache-dismiss")}
        </Button>
      ) : null}
    </>
  );

  return panelAlertMessage ? (
    <Alert
      variant="outlined"
      severity={panelAlertStatus}
      icon={
        isQueryCacheBuilding ? (
          <AutorenewOutlinedIcon color="primary" className={classes.spinnedIcon} />
        ) : null
      }
    >
      {title ? <AlertTitle>{title}</AlertTitle> : <></>}
      <span>{panelAlertMessage}</span>
      {getIsShowButtonPanel() ? (
        isButtonsPanel ? (
          <Box mt={1} ml={-1}>
            {renderButtons()}
          </Box>
        ) : (
          renderButtons()
        )
      ) : null}
    </Alert>
  ) : (
    <AppLoader isOpen={false} />
  );
};

export default QueryCacheAlert;
