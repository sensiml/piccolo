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

import clsx from "clsx";
import { NavLink } from "react-router-dom";

import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
} from "@mui/material";
import useStyles from "components/Layout/NavDrawer.styles";

import { MenuItems, MenuItemsExternal, getMenuProps } from "./LayoutConstants";

const NavDrawer = ({ isOpen, onClose, isSmallScreen, selectedProject, selectedModel }) => {
  const classes = useStyles("layout");

  const filteredMenuItemsExternal = useMemo(
    () => MenuItemsExternal.filter((menuItem) => !menuItem.isHidden),
    [],
  );

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
        }}
        open={isOpen}
        onClose={onClose}
        onClick={() => isSmallScreen && onClose()}
      >
        <List className={classes.listWrapper}>
          {
            /* show only First Item when project is not selected either list without first page */
            MenuItems.filter(
              (el) =>
                (el?.id === "navHome" && !selectedProject) ||
                (selectedProject && el?.id !== "navHome"),
            ).map((menuItem, index) => (
              <NavLink
                key={`nav_link_${index}`}
                className={classes.navLink}
                activeClassName={classes.selectedMenuText}
                exact={["navChangeProject", "navHome"].includes(menuItem.id)}
                to={menuItem.getPath({
                  ...(selectedProject && { projectUUID: selectedProject }),
                  ...(selectedModel && { modelUUID: selectedModel }),
                })}
                disabled={selectedProject === null}
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
            ))
          }
        </List>
        <Divider variant="middle" />
        <Box className={classes.navListsWrapper}>
          <List className={classes.listWrapper}>
            {filteredMenuItemsExternal.map((menuItem) => (
              <NavLink
                className={classes.navLink}
                key={menuItem.id}
                activeClassName={classes.selectedMenuText}
                to={menuItem.getPath()}
                target={menuItem.target}
              >
                <ListItem id={menuItem.id}>
                  <ListItemIcon className={classes.iconButton}>
                    <Tooltip title={menuItem.tooltip} aria-label="add">
                      {menuItem.iconfn({ color: "inherit", fontSize: "medium" })}
                    </Tooltip>
                  </ListItemIcon>
                  <ListItemText
                    primary={menuItem.title}
                    classes={{
                      primary: classes.disabledMenuText,
                    }}
                  />
                </ListItem>
              </NavLink>
            ))}
          </List>
        </Box>
      </Drawer>
    </div>
  );
};

export default NavDrawer;
