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
    root: {
      flexGrow: 1,
    },
    mainHeader: {
      paddingLeft: 10,
    },
    box: {
      minWidth: 245,
      minHeight: 400,
    },
    grid: {},
    sessionWrapper: {
      padding: `${theme.spacing(2)}`,
      marginTop: theme.spacing(2),
      marginBottom: theme.spacing(2),
    },
    fileTypes: {
      marginTop: -20,
    },
    actionButton: {
      marginTop: 10,
    },
    actionStopButton: {
      marginTop: 10,
      marginLeft: 30,
    },
    progressbar: {
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
    },
    backdrop: {
      zIndex: theme.zIndex.drawer + 1,
      color: "#fff",
    },
    classificationChart: {
      width: "100%",
    },
    classifierResults: {
      paddingTop: 10,
    },
    classifierResultsTabGrid: {
      maxWidth: "100%",
    },
    classifierResultsTabPanel: {
      flexGrow: 1,
      width: "100%",
      backgroundColor: theme.palette.background.paper,
    },
  }))();

export default useStyles;
