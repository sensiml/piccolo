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
import { blue, deepPurple, indigo, purple, orange, deepOrange } from "@mui/material/colors";

const useStyles = () =>
  makeStyles((theme) => ({
    root: {
      flexGrow: 1,
    },
    box: {
      maxWidth: 285,
      minWidth: 285,
      margin: 10,
      padding: 30,
      paddingBottom: 20,
    },
    cardHeader: {
      flexGrow: 1,
      paddingTop: 15,
      paddingBottom: 0,
    },
    cardContent: {
      paddingTop: 5,
    },
    divider: {
      marginLeft: 5,
      marginRight: 5,
    },
    grid: {
      flexGrow: 0,
      paddingTop: 20,
      paddingBottom: 20,
    },
    numberBox: { maxWidth: 30, paddingTop: 15, paddingBottom: 15 },
    filesBox: {
      backgroundColor: blue[100],
    },
    pipelineBox: {
      backgroundColor: indigo[200],
    },
    metadataBox: {
      backgroundColor: purple[200],
    },
    sizeBox: {
      backgroundColor: deepPurple[200],
    },
    queriesBox: {
      backgroundColor: orange[200],
    },
    modelsBox: {
      backgroundColor: deepOrange[200],
    },
    detailsButton: {
      marginTop: 10,
    },
    arrow: {
      color: theme.palette.common.black,
    },
    tooltip: {
      backgroundColor: theme.palette.common.black,
    },
  }))();

export default useStyles;
