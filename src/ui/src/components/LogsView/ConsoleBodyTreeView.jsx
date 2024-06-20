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
import TreeView from "@mui/lab/TreeView";
import TreeItem from "@mui/lab/TreeItem";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ChevronRightIcon from "@mui/icons-material/ChevronRight";
import Highlight from "react-highlight.js";
import useStyles from "./ConsoleViewStyle";
import "./monokai-sublime.css";

const lineFeedRegex = /\\n/gi;

const ConsoleBodyTreeView = ({ logs }) => {
  const classes = useStyles();

  const getMessage = (log) => {
    return log.message.error_message || log.message;
  };

  const getChildren = (log) => {
    return (
      <Highlight language="json">
        <pre className={`${classes.preConsole}`}>
          {JSON.stringify(log, null, 2).replace(lineFeedRegex, "\n")}
        </pre>
      </Highlight>
    );
  };

  return (
    <TreeView
      className={classes.statusMessages}
      defaultCollapseIcon={<ExpandMoreIcon />}
      defaultExpandIcon={<ChevronRightIcon />}
    >
      {logs?.length ? (
        logs.map((log) => (
          <TreeItem
            className={classes.statusMessage}
            key={log.logid}
            nodeId={log.logid}
            label={
              <pre className={`${classes.preConsole}`}>
                {`${log.timestamp} - ${getMessage(log)}`}
              </pre>
            }
          >
            {getChildren(log)}
          </TreeItem>
        ))
      ) : (
        <></>
      )}
    </TreeView>
  );
};

export default ConsoleBodyTreeView;
