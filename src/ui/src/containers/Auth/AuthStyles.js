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
    root: { backgroundColor: "rgb(232, 232, 232)" },
    card: {
      paddingTop: theme.spacing(2),
      maxWidth: 600,
      minWidth: 250,
      margin: "auto",
    },
    rememberMe: {
      alignContent: "flex-start",
      textTransform: "none",
      fontSize: "0.8125rem",
    },
    forgotPassword: {
      textAlign: "right",
      marginTop: 4,
    },
    textButton: {
      textTransform: "none",
    },
    register: {
      textAlign: "center",
    },
    logoImg: {
      display: "block",
      marginLeft: "auto",
      marginRight: "auto",
      paddingBottom: 30,
      height: 156,
    },
    responsiveViewImg: {
      height: 300,
      width: 480,
      paddingLeft: theme.spacing(10),
      paddingTop: 60,
      "@media (max-width: 775px)": {
        height: 240,
        width: 385,
        paddingTop: 10,
      },
    },
    featureList: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    featureListIcon: {
      minWidth: 30,
    },
    loginButton: {
      marginBottom: 10,
    },
    loginSection: { backgroundColor: "rgb(251,251,251)", height: "97vh" },
    loginGrid: { height: "100%" },
    evalSection: {
      backgroundColor: "rgb(232, 232, 232)",
      textAlign: "center",
      verticalAlign: "center",
      color: theme.palette.text.primary,
    },
    footer: {
      backgroundColor: "rgb(251, 251, 251)",
      width: "100%",
      textAlign: "center",
      fontSize: "0.50rem",
      bottom: 0,
      height: "3vh",
    },
    evalButtons: {
      marginRight: theme.spacing(2),
      marginTop: theme.spacing(2),
    },
    paper: {
      padding: theme.spacing(2),
      textAlign: "center",
      color: theme.palette.text.secondary,
    },
    cardHeader: {
      paddingTop: 15,
      paddingBottom: 0,
      textAlign: "center",
    },
    cardContent: {
      paddingTop: 5,
    },
    errorDiv: {
      paddingBottom: 25,
    },
    errorMessage: {
      color: theme.palette.error.main,
    },
    socialAuthWrappep: {
      width: "100%",
    },
    pos: {
      marginBottom: theme.spacing(2),
    },
    button: {
      margin: theme.spacing(1),
    },
    mainGrid: { minHeight: "100vh", color: "white" },
    media: {
      height: 40,
      width: 30,
      paddingLeft: 60,
      marginLeft: 15,
      marginTop: 15,
    },
  }))();

export default useStyles;
