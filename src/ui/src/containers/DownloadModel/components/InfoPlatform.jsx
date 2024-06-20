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
import { useTranslation } from "react-i18next";
import { Box, List, Link, ListItem } from "@mui/material";
import useStyles from "../DownloadModelStyles";

const InfoPlatform = ({ info }) => {
  const { t } = useTranslation("models");
  const classes = useStyles();

  return (
    <Box>
      <List dense className={classes.infoList}>
        <ListItem className={classes.infoListItem}>
          <b className={classes.prefix}>{t("info.platform-header")}</b>
          {info?.name}
        </ListItem>
        <ListItem className={classes.infoListItem}>
          <b className={classes.prefix}>{t("info.platform-manufacturer")}</b>
          {info?.manufacturer}
        </ListItem>
        <ListItem className={classes.infoListItem}>
          <b className={classes.prefix}>{t("info.platform-description")}</b>
          {`${info?.description} `}
          <br />
        </ListItem>
        <ListItem className={classes.infoListItem}>
          <b className={classes.prefix}>{t("info.platform-documentation")}</b>
          <Link href={info?.documentation} target={"_blank"}>
            {t("info.platform-documentation-link")}
          </Link>
        </ListItem>
      </List>
    </Box>
  );
};

export default InfoPlatform;
