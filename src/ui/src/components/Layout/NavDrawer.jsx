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
import { NavLink, matchPath } from "react-router-dom";
import { ROUTES } from "routers";

import {
  Box,
  Collapse,
  Divider,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
} from "@mui/material";
import useStyles from "components/Layout/NavDrawer.styles";
import { StatusRunningIcon } from "components/LogsView";
import { RUNNING_STATUSES } from "consts";
import CloseIcon from "@mui/icons-material/Close";
import { filterTruncate } from "filters";

import { MENU_ITEMS, MENU_ITEMS_INFO, MENU_ITEMS_EXTERNAL, getMenuProps } from "./LayoutConstants";

const NavDrawer = ({
  isOpen,
  onClose,
  isSmallScreen,
  selectedProject,
  selectedModel,
  selectedPipeline,
  selectedPipelineName,
  handleChangePipeline,
  pipelineRunningStatus,
  selectedPipelineExecutionType,
}) => {
  const classes = useStyles("layout");

  const isSubmenuItemsOpened = useCallback(
    (id) => {
      switch (id) {
        case MENU_ITEMS_INFO.MODELS.id:
          return Boolean(selectedModel);
        case MENU_ITEMS_INFO.BUILD_MODEL.id:
          return Boolean(selectedPipelineName);
        default:
          return false;
      }
    },
    [selectedModel, selectedPipelineName],
  );

  const filteredMenuItemsExternal = useMemo(
    () => MENU_ITEMS_EXTERNAL.filter((menuItem) => !menuItem.isHidden),
    [],
  );

  const activePipelinePath = useMemo(() => {
    if (selectedPipelineExecutionType) {
      return ROUTES.MAIN.MODEL_BUILD.child[selectedPipelineExecutionType].path;
    }

    return "";
  }, [selectedPipelineExecutionType]);

  const showIfRunning = (parentId, pathToCheck) => {
    if (
      RUNNING_STATUSES.RUNNING === pipelineRunningStatus &&
      !matchPath(pathToCheck, { path: activePipelinePath, sctrict: false }) &&
      MENU_ITEMS_INFO.BUILD_MODEL.id === parentId
    ) {
      return false;
    }
    return true;
  };

  const getIsPathHasStatus = useCallback(
    (pathToCheck) => {
      if (pipelineRunningStatus && pipelineRunningStatus !== "NOT_STARTED") {
        return Boolean(matchPath(pathToCheck, { path: activePipelinePath, sctrict: false }));
      }
      return false;
    },
    [pipelineRunningStatus, activePipelinePath],
  );

  const SubItemTitle = ({ id, isMenuOpen }) => {
    return (
      <>
        {selectedPipelineName && MENU_ITEMS_INFO.BUILD_MODEL.id === id ? (
          <ListItem>
            {isMenuOpen ? (
              <ListItemText
                primary={filterTruncate(selectedPipelineName, 17)}
                className={classes.navTitle}
              />
            ) : null}
            <Tooltip title={"Close Pipeline"}>
              <IconButton onClick={(_e) => handleChangePipeline()} variant="contained" size="small">
                <CloseIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </ListItem>
        ) : null}
      </>
    );
  };

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
                    <Tooltip title={menuItem.tooltip || menuItem.title} aria-label={menuItem.title}>
                      <ListItemIcon className={classes.iconButton}>
                        {menuItem.iconfn(getMenuProps(menuItem.orderIndex))}
                      </ListItemIcon>
                    </Tooltip>
                    <ListItemText sx={{ pl: isOpen ? 0 : 2 }} primary={menuItem.title} />
                  </ListItem>
                </NavLink>

                {menuItem?.subItems ? (
                  <>
                    <Collapse in={isSubmenuItemsOpened(menuItem.id)} timeout={0}>
                      <Divider variant="middle" />
                      <SubItemTitle id={menuItem.id} isMenuOpen={isOpen} />
                      <List
                        key={`subitem_list_${menuItem.id}`}
                        sx={{ pl: isOpen ? 2 : 0, pt: 0, pb: 0 }}
                      >
                        {menuItem.subItems.map((subItem) => (
                          <Box key={`subitem_nav_link_${subItem.id}`}>
                            {showIfRunning(menuItem.id, subItem.getPath()) ? (
                              <NavLink
                                className={classes.navLink}
                                key={`subitem_nav_link_${subItem.id}`}
                                activeClassName={classes.selectedMenuText}
                                to={subItem.getPath({
                                  ...(selectedProject && { projectUUID: selectedProject }),
                                  ...(selectedModel && { modelUUID: selectedModel }),
                                  ...(selectedPipeline && { pipelineUUID: selectedPipeline }),
                                })}
                              >
                                <ListItem sx={{ pt: 0.5, pb: 0.5 }} id={subItem.id}>
                                  <Tooltip
                                    title={subItem.tooltip || subItem.title}
                                    aria-label={subItem.title}
                                  >
                                    <ListItemIcon className={classes.iconButton}>
                                      {getIsPathHasStatus(subItem.getPath()) ? (
                                        <StatusRunningIcon status={pipelineRunningStatus} />
                                      ) : (
                                        subItem.iconfn(getMenuProps(subItem.orderIndex))
                                      )}
                                    </ListItemIcon>
                                  </Tooltip>
                                  <ListItemText
                                    sx={{ pl: isOpen ? 0 : 2 }}
                                    primary={subItem.title}
                                  />
                                </ListItem>
                              </NavLink>
                            ) : null}
                          </Box>
                        ))}
                      </List>
                    </Collapse>
                  </>
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
                  <ListItemText sx={{ pl: isOpen ? 0 : 2 }} primary={menuItem.title} />
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
