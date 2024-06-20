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
import { NavLink, generatePath } from "react-router-dom";
import { IconButton, AppBar, Toolbar, Tooltip, Typography } from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import AccountCircle from "@mui/icons-material/AccountCircle";

import { ROUTES } from "routers";
import logoImg from "assets/images/sensiml-logo-hz.png";
import useStyles from "components/Layout/Header.style";

import { IconButtonConvertibleToShort } from "components/UIIcons";

const HeaderAppBar = ({
  isOpen,
  isShortBtnText,
  userId,
  onDrawerClose,
  onDrawerOpen,
  onOpenMenu,
  headerTitle,
}) => {
  const { t } = useTranslation(["layout", "team"]);
  const classes = useStyles();

  return (
    <AppBar elevation={0} position="fixed" className={clsx(classes.appBar)}>
      <Toolbar className={classes.mainToolbar}>
        <Tooltip title={isOpen ? t("nav-drawer.tooltip-collapse") : t("nav-drawer.tooltip-expand")}>
          <IconButton
            onClick={() => (isOpen ? onDrawerClose() : onDrawerOpen())}
            className={clsx(classes.menuButton)}
          >
            <MenuIcon />
          </IconButton>
        </Tooltip>
        <div className={classes.toolbar}>
          {isShortBtnText ? null : (
            <NavLink
              className={classes.navLink}
              activeClassName={classes.selectedMenuText}
              to={generatePath(ROUTES.MAIN.HOME.path)}
            >
              <img src={`${logoImg}`} className={classes.logoImg} id="logoImg" alt="logo" />
            </NavLink>
          )}
        </div>
        <Typography variant="h6" id="headerTitle" className={classes.titleWithProjectName}>
          {headerTitle}
        </Typography>
        <section className={classes.rightToolbar}>
          <IconButtonConvertibleToShort
            edge="end"
            aria-label="account of current user"
            aria-controls="primary-account-menu"
            aria-haspopup="true"
            isShort={isShortBtnText}
            onClick={onOpenMenu}
            color="inherit"
            size="large"
            icon={<AccountCircle className={classes.accountCircle} />}
            shortIcon={
              <>
                <AccountCircle className={classes.accountCircle} />
                <Typography variant="body1" id="loginId">
                  {userId}
                </Typography>
              </>
            }
          />
        </section>
      </Toolbar>
    </AppBar>
  );
};

export default HeaderAppBar;
