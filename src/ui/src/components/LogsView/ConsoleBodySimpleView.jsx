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

import React, { useEffect, useRef } from "react";
import { List, ListItem, ListItemIcon } from "@mui/material";

import { STATUSES } from "consts";
import useStyles from "./ConsoleViewStyle";
import StatusIcon from "./StatusIcon";

const ConsoleBodySimpleView = ({ logs }) => {
  const classes = useStyles();

  const listRef = useRef(null);

  const scrollToBottom = () => {
    const scroll = listRef.current.scrollHeight - listRef.current.clientHeight;
    listRef.current.scrollTo(0, scroll);
  };

  useEffect(scrollToBottom, [logs]);

  return (
    <List
      className={classes.statusMessages}
      component="nav"
      aria-label="secondary mailbox folder"
      ref={listRef}
    >
      {/* <ListItem key={`log_logo`} className={classes.statusMessage}>
        <pre className={`${classes.preConsoleNoMargin} ${classes.notNessesaryText}`}>
          {CONSOLE_LOGO}
        </pre>
      </ListItem> */}
      {logs?.length ? (
        logs.map((log, index) => (
          <ListItem key={`log_${index}`} className={classes.statusMessage}>
            <ListItemIcon className={classes.consoleIcon}>{StatusIcon(log.status)}</ListItemIcon>
            <pre
              className={`${classes.preConsole} ${
                log.status <= STATUSES.INFO && classes.notNessesaryText
              }`}
            >
              {log.message}
            </pre>
          </ListItem>
        ))
      ) : (
        <></>
      )}
    </List>
  );
};

export default ConsoleBodySimpleView;
