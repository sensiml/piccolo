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

import makeStyles from "@mui/styles/makeStyles";

const useStyles = () =>
  makeStyles((theme) => ({
    ...theme.common,
    consoleInfoFlex: {
      flex: 3,
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-start",
      color: theme.colorInfoText,
    },
    consoleActionFlex: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      flex: 1,
    },
    consoleBody: {
      boxShadow: "none",
      border: "none",
      whiteSpace: "pre",
      overflow: "visible",
      lineHeight: 1,
      fontFamily:
        // eslint-disable-next-line max-len
        "Consolas,Monaco,Lucida Console,Liberation Mono,DejaVu Sans Mono,Bitstream Vera Sans Mono,Courier New, monospace",
    },
    consoleIcon: {
      minWidth: theme.spacing(1),
      marginRight: theme.spacing(1),
    },
    statusMessages: {
      color: theme.colorConsoleBody,
      height: "30rem",
      overflowY: "auto",
      position: "relative",
      "&::-webkit-scrollbar": {
        width: theme.spacing(0.5),
        cursor: "pointer",
      },
      "&::-webkit-scrollbar-track": {
        boxShadow: "none",
        webkitBoxShadow: "none",
        backgroundColor: theme.colorConsoleScrollTrackBg,
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: theme.colorConsoleScrollBg,
        // outline: "1px solid slategrey",
      },
    },
    statusMessage: {
      padding: 0,
      marginBottom: theme.spacing(2),
    },
    notNessesaryText: {
      color: theme.colorConsoleInfoText,
    },
    preConsoleNoMargin: {
      margin: 0,
      lineHeight: 1,
    },
    preConsole: {
      fontSize: "0.85rem",
      margin: 0,
      lineHeight: 1,
      whiteSpace: "pre-wrap",
    },
  }))();

export default useStyles;
