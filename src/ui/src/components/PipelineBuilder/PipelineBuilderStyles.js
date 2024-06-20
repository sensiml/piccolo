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
    formControl: {
      margin: theme.spacing(1),
      minWidth: 393,
      "@media (max-width: 2600px)": {
        minWidth: 800,
        maxWidth: 1210,
      },
      "@media (max-width: 2000px)": {
        minWidth: 400,
        maxWidth: 1210,
      },
      "@media (max-width: 1450px)": {
        minWidth: 390,
        maxWidth: 650,
      },
      "@media (max-width: 1250px)": {
        minWidth: 400,
        maxWidth: 600,
      },
      "@media (max-width: 1050px)": {
        minWidth: 400,
        maxWidth: 600,
      },
      "@media (max-width: 770px)": {
        minWidth: 600,
        maxWidth: 700,
      },
    },
    flowWrapper: {
      display: "flex",
      justifyContent: "flex-end",
    },
    errorDiv: {
      marginTop: -22,
      minHeight: 50,
    },
    errorMessage: {
      color: theme.palette.error.main,
    },
    addNewButton: {
      marginRight: 20,
      marginTop: 20,
    },
    pipelineDetails: {
      position: "sticky",
      top: "100px",
    },
    backdrop: {
      zIndex: theme.zIndex.drawer + 1,
      color: "#fff",
    },
    nodeColor1: {
      backgroundColor: "#e3f2fd",
    },
    nodeColor2: {
      backgroundColor: "#e8eaf6",
    },
    nodeColor3: {
      backgroundColor: "#fff3e0",
    },
    nodeColor4: {
      backgroundColor: "#f9fbe7",
    },
    nodeColor5: {
      backgroundColor: "#cfd8dc",
    },
    nodeColor6: {
      backgroundColor: "#c8e6c9",
    },
    nodeColor7: {
      backgroundColor: "#e0f2f1",
    },
    nodeColor8: {
      backgroundColor: "#f1f8e9",
    },
  }))();

export default useStyles;
