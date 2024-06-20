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
    mainGrid: {
      marging: 0,
      padding: theme.spacing(2),
    },
    backdrop: {
      zIndex: theme.zIndex.drawer + 1,
      color: "#fff",
    },
    card: {
      margin: "auto",
      transition: "0.3s",
      boxShadow: "0 8px 40px -12px rgba(0,0,0,0.3)",
      "&:hover": {
        boxShadow: "0 16px 70px -12.125px rgba(0,0,0,0.3)",
      },
    },
    media: {
      paddingTop: "56.25%",
    },
    content: {
      textAlign: "left",
      padding: 7,
      minHeight: 150,
    },
    heading: {
      fontWeight: "bold",
    },
    subheading: {
      lineHeight: 1.8,
    },
    tabs: {
      "&:last-child": {
        position: "absolute",
        right: "0",
      },
    },
    boxBig: {
      minWidth: 150,
      minHeight: 60,
      paddingRight: 10,
      paddingTop: 3,
      margin: 2,
    },
    fieldTitleBig: {
      fontSize: 20,
      // fontWeight: "bold",
      color: theme.palette.primary.main,
    },
    fieldValueBig: {
      fontSize: 25,
      lineHeight: 1,
      // fontWeight: "bold",
      paddingTop: 15,
    },
    dashboardIconBig: {
      // minWidth: 60,
      fontSize: 20,
      // paddingRight: 5,
      verticalAlign: "middle",
    },
    boxNormal: {
      minWidth: 180,
      minHeight: 60,
      paddingRight: 20,
      margin: 2,
    },
    fieldTitleNormal: {
      fontSize: 13,
      fontWeight: "bold",
      color: theme.palette.primary.main,
    },
    fieldValueNormal: {
      fontSize: 20,
      fontWeight: "bold",
      float: "center",
    },

    dashboardIconNormal: {
      minWidth: 50,
      fontSize: 50,
      verticalAlign: "middle",
    },
    boxSmall: {
      minWidth: 200,
      minHeight: 40,
      paddingRight: 20,
      margin: 2,
    },
    fieldTitleSmall: {
      fontSize: 20,
      // fontWeight: "bold",
      color: theme.palette.primary.main,
    },
    fieldValueSmall: {
      fontSize: 17,
      // fontWeight: "bold",
      lineHeight: 1,
      float: "center",
    },
    dashboardIconSmall: {
      minWidth: 25,
      fontSize: 25,
      verticalAlign: "middle",
    },
    dataDescription: {
      width: "100%",
    },
    fieldContent: {
      margin: "auto",
      width: "60%",
      padding: 10,
    },
    dataOuterDiv: {
      display: "table",
      overflow: "hidden",
      height: "100%",
    },
    dataInnerDiv: {
      display: "table-cell",
      verticalAlign: "middle",
    },
    imageSelectorWrapper: {
      width: 400,
    },
    imageSelectionWrapper: {
      width: 400,
      paddingTop: 20,
    },
    SelectedImageStyle: {
      width: 385,
    },
  }))();

export default useStyles;
