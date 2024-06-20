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
    refreshBtn: {
      marginLeft: theme.spacing(2),
    },
    mainHeader: {
      paddingLeft: 10,
    },
    formControl: {
      margin: theme.spacing(1),
      minWidth: 300,
      [theme.breakpoints.up("lg")]: {
        // maxWidth: 1000,
      },
      [theme.breakpoints.down("md")]: {
        maxWidth: 600,
      },
    },
    formControlButtons: {
      minWidth: 300,
      [theme.breakpoints.up("lg")]: {
        // maxWidth: 1000,
      },
      [theme.breakpoints.down("md")]: {
        maxWidth: 600,
      },
    },
    queryBox: {
      minWidth: 245,
      minHeight: 525,
      paddingRight: 20,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-between",
    },
    queryForms: {
      display: "flex",
      flexDirection: "column",
    },
    grid: { maxWidth: 1900 },
    chartGrid: { padding: theme.spacing(2), marginBottom: theme.spacing(2) },
    fixedHeight: {
      margin: theme.spacing(1),
      paddingTop: theme.spacing(1),
      paddingBottom: theme.spacing(5),
      height: 320,
      minWidth: 300,
    },
    buttonWrapper: {
      display: "flex",
      gap: theme.spacing(1),
      marginTop: theme.spacing(2),
    },
    errorDiv: {
      marginTop: -22,
      minHeight: 50,
    },
    errorMessage: {
      color: theme.palette.error.main,
    },
    backdrop: {
      zIndex: theme.zIndex.drawer + 1,
      color: "#fff",
    },
    textFieldHide: { display: "none" },
    queryTextField: { marginTop: 20 },
  }))();

export default useStyles;
