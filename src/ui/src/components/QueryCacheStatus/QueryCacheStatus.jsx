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
import clsx from "clsx";
import { useTranslation } from "react-i18next";
import { Tooltip, Box } from "@mui/material";

import IconSpinneAutoRenew from "components/UIIcons/IconSpinneAutoRenew";

import DoneIcon from "@mui/icons-material/Done";
import NotInterestedIcon from "@mui/icons-material/NotInterested";
import { CACHE_STATUSES } from "store/queries/const";

import useStyles from "./QueryCacheStatusStyles";

const QueryCacheStatus = ({ cacheStatus }) => {
  const { t } = useTranslation("queries");
  const classes = useStyles();

  const getIcon = () => {
    switch (cacheStatus) {
      case CACHE_STATUSES.CACHED:
        return <DoneIcon />;
      case CACHE_STATUSES.BUILDING:
        return <IconSpinneAutoRenew />;
      default:
        return <NotInterestedIcon />;
    }
  };

  const getTooltip = () => {
    switch (cacheStatus) {
      case CACHE_STATUSES.CACHED:
        return t("cache.cache");
      case CACHE_STATUSES.BUILDING:
        return t("cache.building-cache");
      case CACHE_STATUSES.FAILED:
        return t("cache.failed-building-cache");
      default:
        return t("cache.no-cache");
    }
  };

  return (
    <Tooltip title={getTooltip(cacheStatus)}>
      <Box
        className={clsx(classes.statusBox, {
          [classes.statusBoxCached]: cacheStatus === CACHE_STATUSES.CACHED,
          [classes.statusBoxBuilding]: cacheStatus === CACHE_STATUSES.BUILDING,
          [classes.statusBoxFailed]: cacheStatus === CACHE_STATUSES.FAILED,
        })}
      >
        {getIcon(cacheStatus)} {cacheStatus || t("cache.no-cache-status-text")}
      </Box>
    </Tooltip>
  );
};

export default QueryCacheStatus;
