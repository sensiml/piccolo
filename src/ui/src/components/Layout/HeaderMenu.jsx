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

import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import InfoIcon from "@mui/icons-material/Info";
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart";
import CloudIcon from "@mui/icons-material/Cloud";

import { Menu, MenuItem, ListItemIcon, Link, Typography } from "@mui/material";

import { useTranslation } from "react-i18next";
import { PLANS_LINK } from "config";

import makeStyles from "@mui/styles/makeStyles";

const useStyles = () =>
  makeStyles((_theme) => ({
    accountUpgradeListItem: {
      background: "#0ca1c7 !important",
      color: "white",
      paddingTop: "0.75rem",
      paddingBottom: "0.75rem",
    },
  }))();

const HeaderMenu = ({
  isOpen,
  anchorEl,
  isFreeAccount,
  onClose,
  onClickHome,
  onClickAccountSetting,
  onClickShowAbout,
  onClickLogOut,
}) => {
  const { t } = useTranslation("layout");
  const classes = useStyles();

  return (
    <Menu
      anchorEl={anchorEl}
      elevation={3}
      id="topMenu"
      keepMounted
      anchorOrigin={{
        vertical: "bottom",
        horizontal: "center",
      }}
      transformOrigin={{
        vertical: "top",
        horizontal: "center",
      }}
      open={isOpen}
      onClose={onClose}
    >
      {onClickHome ? (
        <MenuItem onClick={onClickHome}>
          <ListItemIcon>
            <CloudIcon fontSize="small" />
          </ListItemIcon>
          <Typography variant="inherit">{t("header-menu.home")}</Typography>
        </MenuItem>
      ) : null}
      {onClickAccountSetting ? (
        <MenuItem onClick={onClickAccountSetting}>
          <ListItemIcon>
            <CloudIcon fontSize="small" />
          </ListItemIcon>
          <Typography variant="inherit">{t("header-menu.account-settings")}</Typography>
        </MenuItem>
      ) : null}
      {onClickShowAbout ? (
        <MenuItem onClick={onClickShowAbout}>
          <ListItemIcon>
            <InfoIcon fontSize="small" />
          </ListItemIcon>
          <Typography variant="inherit">{t("header-menu.about")}</Typography>
        </MenuItem>
      ) : null}
      {onClickLogOut ? (
        <MenuItem onClick={onClickLogOut}>
          <ListItemIcon>
            <ExitToAppIcon fontSize="small" />
          </ListItemIcon>
          <Typography variant="inherit" id="logoutButton">
            {t("header-menu.log-out")}
          </Typography>
        </MenuItem>
      ) : null}
      {isFreeAccount ? (
        <Link
          href={PLANS_LINK}
          title={t("header-menu.upgrade-to-proto")}
          style={{ textDecoration: "none" }}
          target="_blank"
        >
          <MenuItem className={classes.accountUpgradeListItem}>
            <ListItemIcon>
              <ShoppingCartIcon style={{ color: "white" }} fontSize="small" />
            </ListItemIcon>
            <Typography variant="inherit" id="logoutButton">
              {t("header-menu.upgrade-to-proto")}
            </Typography>
          </MenuItem>
        </Link>
      ) : null}
    </Menu>
  );
};

export default HeaderMenu;
