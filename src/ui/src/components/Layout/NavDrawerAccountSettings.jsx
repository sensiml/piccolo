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
import LockOutlinedIcon from "@mui/icons-material/LockOutlined";
import AccountBalanceWalletOutlinedIcon from "@mui/icons-material/AccountBalanceWalletOutlined";
import VpnKeyOutlinedIcon from "@mui/icons-material/VpnKeyOutlined";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import SettingsApplicationsOutlinedIcon from "@mui/icons-material/SettingsApplicationsOutlined";

import { NavLink, generatePath } from "react-router-dom";
import { Drawer, List, ListItem, ListItemIcon, ListItemText, Tooltip } from "@mui/material";

import useStyles from "components/Layout/NavDrawer.styles";
import { ROUTES } from "routers";

import { getMenuProps } from "./LayoutConstants";

const MenuItems = [
  {
    title: "Home",
    id: "navHome",
    orderIndex: 0,
    iconfn: (iconProps) => <ExitToAppIcon {...iconProps} />,
    getPath: (params = {}) =>
      generatePath(ROUTES.MAIN.path, {
        ...params,
      }),
  },
  {
    title: "Account Info",
    id: "acccont_inofo",
    orderIndex: 0,
    iconfn: (iconProps) => <LockOutlinedIcon {...iconProps} />,
    getPath: () => ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_INFO.path,
  },
  {
    title: "Subscriptions",
    id: "subscriptions",
    orderIndex: 1,
    iconfn: (iconProps) => <AccountBalanceWalletOutlinedIcon {...iconProps} />,
    getPath: () => ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_SUBCRIPTIONS.path,
  },
  {
    title: "API Keys",
    id: "api_keys",
    orderIndex: 2,
    iconfn: (iconProps) => <VpnKeyOutlinedIcon {...iconProps} />,
    getPath: () => ROUTES.ACCOUNT_SETTINGS.child.ACCOUNT_API_KEYS.path,
  },
  {
    title: "Admin Console",
    id: "admin_console",
    orderIndex: 4,
    iconfn: (iconProps) => <SettingsApplicationsOutlinedIcon {...iconProps} />,
    getPath: () => `${process.env.REACT_APP_API_URL}admin/`,
    target: "_blank",
  },
];

const NavDrawerAccountSettings = ({ isOpen, onClose, isSmallScreen }) => {
  const classes = useStyles("layout");

  return (
    <div>
      <Drawer
        variant={isSmallScreen ? "temporary" : "permanent"}
        role="presentation"
        className={clsx(classes.drawer, {
          [classes.drawerOpen]: isOpen,
          [classes.drawerClose]: !isOpen,
        })}
        classes={{
          paper: clsx(classes.drawer, {
            [classes.drawerScrolled]: true,
            [classes.drawerOpen]: isOpen,
            [classes.drawerClose]: !isOpen,
          }),
          toolbar: classes.toolbar,
        }}
        open={isOpen}
        onClose={onClose}
        onClick={() => isSmallScreen && onClose()}
      >
        <List className={classes.listWrapper}>
          {MenuItems.map((menuItem, index) => {
            return (
              <NavLink
                key={`account_nav_link_${index}`}
                className={classes.navLink}
                exact
                activeClassName={classes.selectedMenuText}
                target={menuItem.target}
                to={{
                  pathname: menuItem.getPath(),
                  isConfirmed: true,
                }}
              >
                <ListItem key={menuItem.title} id={menuItem.id}>
                  <ListItemIcon className={classes.iconButton}>
                    <Tooltip title={menuItem.title} aria-label="add">
                      {menuItem.iconfn(getMenuProps(menuItem.orderIndex))}
                    </Tooltip>
                  </ListItemIcon>
                  <ListItemText primary={menuItem.title} />
                </ListItem>
              </NavLink>
            );
          })}
        </List>
      </Drawer>
    </div>
  );
};

export default NavDrawerAccountSettings;
