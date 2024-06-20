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

import React, { useState, useEffect } from "react";
import PlaylistAddCheckIcon from "@mui/icons-material/PlaylistAddCheck";
import TocIcon from "@mui/icons-material/Toc";
import ClickAwayListener from "@mui/material/ClickAwayListener";
import {
  Divider,
  Grow,
  ListItemIcon,
  Paper,
  Popper,
  MenuItem,
  MenuList,
  Typography,
} from "@mui/material";

import makeStyles from "@mui/styles/makeStyles";

const useStyles = () =>
  makeStyles((theme) => ({
    contextMenu: {
      zIndex: theme.zIndex.tooltip + 1,
    },
  }))();

export const SelectionMenu = ({
  closeAction,
  onSelectAllInTable,
  onUnSelectAllInTable,
  isDisabledSelectAll,
  openMenu,
  anchor,
}) => {
  const classes = useStyles();
  const [open, setOpen] = useState(openMenu);
  const [anchorRef, setAnchorRef] = useState(anchor);

  useEffect(() => {
    setOpen(openMenu);
  }, [openMenu]);

  const handleClose = (event) => {
    if (anchorRef.current && anchorRef.current.contains(event.target)) {
      return;
    }
    setOpen(false);
    closeAction(event);
  };

  const handleListKeyDown = (event) => {
    if (event.key === "Tab") {
      event.preventDefault();
      setOpen(false);
    }
  };

  // return focus to the button when we transitioned from !open -> open
  const prevOpen = React.useRef(open);
  React.useEffect(() => {
    if (prevOpen.current === true && open === false && anchorRef && anchorRef.current) {
      anchorRef.current.focus();
    }

    prevOpen.current = open;
  }, [open]);

  React.useEffect(() => {
    setAnchorRef(anchor);
  }, [anchor]);

  const handleSelectAllInTable = (event) => {
    if (onSelectAllInTable) {
      onSelectAllInTable(event);
    }
    handleClose(event);
  };

  const handleUnSelectAllInTable = (event) => {
    onUnSelectAllInTable(event);
    handleClose(event);
  };

  return (
    <Popper
      open={open}
      anchorEl={() => anchorRef || null}
      role={undefined}
      transition
      disablePortal
      className={classes.contextMenu}
    >
      {({ TransitionProps, placement }) => (
        <Grow
          {...TransitionProps}
          style={{
            transformOrigin: placement === "bottom" ? "center top" : "center bottom",
          }}
        >
          <Paper>
            <ClickAwayListener onClickAway={handleClose}>
              <MenuList autoFocusItem={open} id="menu-list-grow" onKeyDown={handleListKeyDown}>
                {!isDisabledSelectAll ? (
                  <>
                    <MenuItem onClick={handleSelectAllInTable}>
                      <ListItemIcon>
                        <PlaylistAddCheckIcon fontSize="small" color="primary" />
                      </ListItemIcon>
                      <Typography variant="inherit">Select All</Typography>
                    </MenuItem>
                    <Divider />
                  </>
                ) : null}
                <MenuItem onClick={handleUnSelectAllInTable}>
                  <ListItemIcon>
                    <TocIcon fontSize="small" color="primary" />
                  </ListItemIcon>
                  <Typography variant="inherit">Unselect All</Typography>
                </MenuItem>
              </MenuList>
            </ClickAwayListener>
          </Paper>
        </Grow>
      )}
    </Popper>
  );
};

export default SelectionMenu;
