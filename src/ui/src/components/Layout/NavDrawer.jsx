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

import React, { useCallback, useMemo } from "react";

import clsx from "clsx";
import { NavLink } from "react-router-dom";

import {
  Box,
  Collapse,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Tooltip,
} from "@mui/material";
import useStyles from "components/Layout/NavDrawer.styles";

import { MENU_ITEMS, MENU_ITEMS_INFO, MENU_ITEMS_EXTERNAL, getMenuProps } from "./LayoutConstants";

const NavDrawer = ({
  isOpen,
  onClose,
  isSmallScreen,
  selectedProject,
  selectedModel,
  selectedPipeline,
}) => {
  const classes = useStyles("layout");

  const isSubmenuItemsOpened = useCallback(
    (id) => {
      switch (id) {
        case MENU_ITEMS_INFO.MODELS.id:
          return Boolean(selectedModel);
        case MENU_ITEMS_INFO.BUILD_MODEL.id:
          return Boolean(selectedPipeline);
        default:
          return false;
      }
    },
    [selectedModel, selectedPipeline],
  );

  const filteredMenuItemsExternal = useMemo(
    () => MENU_ITEMS_EXTERNAL.filter((menuItem) => !menuItem.isHidden),
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
        <List
          sx={{ width: "100%", maxWidth: 360, bgcolor: "background.paper" }}
          className={classes.listWrapper}
        >
          {
            /* show only First Item when project is not selected either list without first page */
            MENU_ITEMS.filter(
              (el) =>
                (el?.id === "navHome" && !selectedProject) ||
                (selectedProject && el?.id !== "navHome"),
            ).map((menuItem) => (
              <Box key={`item_nav_link_${menuItem.id}`}>
                <NavLink
                  className={classes.navLink}
                  activeClassName={classes.selectedMenuText}
                  exact={["navChangeProject", "navHome"].includes(menuItem.id)}
                  to={menuItem.getPath({
                    ...(selectedProject && { projectUUID: selectedProject }),
                    ...(selectedModel && { modelUUID: selectedModel }),
                  })}
                  disabled={selectedProject === null}
                >
                  <ListItem key={menuItem.id} id={menuItem.id}>
                    <Tooltip title={menuItem.title} aria-label="add">
                      <ListItemIcon className={classes.iconButton}>
                        {menuItem.iconfn(getMenuProps(menuItem.orderIndex))}
                      </ListItemIcon>
                    </Tooltip>
                    <ListItemText primary={menuItem.title} />
                  </ListItem>
                </NavLink>

                {menuItem?.subItems ? (
                  <Collapse in={isSubmenuItemsOpened(menuItem.id)} timeout="auto" unmountOnExit>
                    <List key={`suitem_list_${menuItem.id}`} sx={{ pl: 2, pt: 0, pb: 0 }}>
                      {menuItem.subItems.map((subItem) => (
                        <NavLink
                          className={classes.navLink}
                          key={`subitem_nav_link_${subItem.id}`}
                          activeClassName={classes.selectedMenuText}
                          to={subItem.getPath({
                            ...(selectedProject && { projectUUID: selectedProject }),
                            ...(selectedModel && { modelUUID: selectedModel }),
                            ...(selectedPipeline && { pipelineUUID: selectedPipeline }),
                          })}
                          disabled={selectedProject === null}
                        >
                          <ListItem sx={{ pt: 0.5, pb: 0.5 }} id={subItem.id}>
                            <Tooltip title={subItem.title} aria-label="add">
                              <ListItemIcon className={classes.iconButton}>
                                {subItem.iconfn(getMenuProps(subItem.orderIndex))}
                              </ListItemIcon>
                            </Tooltip>
                            <ListItemText primary={subItem.title} />
                          </ListItem>
                        </NavLink>
                      ))}
                    </List>
                  </Collapse>
                ) : null}
              </Box>
            ))
          }
        </List>
        <Divider variant="middle" />
        <Box className={classes.navListsWrapper}>
          <List key={"external_items_list"} className={classes.listWrapper}>
            {filteredMenuItemsExternal.map((menuItem) => (
              <NavLink
                className={classes.navLink}
                key={menuItem.id}
                activeClassName={classes.selectedMenuText}
                to={menuItem.getPath()}
                target={menuItem.target}
              >
                <ListItem key={menuItem.id} id={menuItem.id}>
                  <ListItemIcon className={classes.iconButton}>
                    <Tooltip title={menuItem.tooltip} aria-label="add">
                      {menuItem.iconfn({ color: "inherit", fontSize: "small" })}
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
