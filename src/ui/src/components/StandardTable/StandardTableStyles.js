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
import { red, green, orange, teal } from "@mui/material/colors";

const useStyles = (isDarkHeader) =>
  makeStyles((theme) => ({
    root: {
      display: "flex",
      overflowX: "hide",
      minHeight: 100,
      minWidth: 220,
    },
    contextMenuIcon: {
      position: "absolute",
      right: 50,
    },
    titleCell: {
      padding: theme.spacing(2),
    },
    title: {
      fontSize: theme.spacing(3),
      fontWeight: 600,
      color: theme.palette.notSelected?.main,
    },
    box: {},
    // overwrite
    sizeSmallCell: {
      padding: `${theme.spacing(2)} ${theme.spacing(1)}`,
    },

    tableHeader: {
      zIndex: 11,
      backgroundColor: isDarkHeader ? theme.bakgroundTableDarkHeader : theme.bakgroundTableHeader,
      borderBottom: `2px solid ${theme.tableBorderColor}`,
      borderTop: `2px solid ${theme.tableBorderColor}`,

      position: "relative",
      "&:last-child": {
        borderTopRightRadius: "0.25rem",
        borderRight: `2px solid ${theme.tableBorderColor}`,
      },
      "&:first-child": {
        borderTopLeftRadius: "0.25rem",
        borderLeft: `2px solid ${theme.tableBorderColor}`,
      },
      "&:not(:last-child)::before": {
        content: "''",
        position: "absolute",
        right: 0,
        top: "25%",
        width: "2px",
        height: "50%",
        backgroundColor: theme.tableBorderColor,
      },
    },
    tableCenteredHeader: {
      textAlign: "center",
    },
    tableHighlightedBlue: {
      backgroundColor: "#9acce6",
    },
    tableDelimiteddBlue: {
      backgroundColor: "#dae9f1",
    },
    tableMainCell: {
      backgroundColor: isDarkHeader ? theme.bakgroundTableDarkHeader : theme.bakgroundTableHeader,
      borderBottom: `1px solid ${theme.tableBorderColor}`,
      borderLeft: `1px solid ${theme.tableBorderColor}`,
      borderRight: `1px solid ${theme.tableBorderColor}`,
      textAlign: "center",
      fontSize: "0.875rem",
      fontWeight: "500",
    },
    tableRowGrey: {
      backgroundColor: "#e3e6e8 !important",
    },
    tableRowGreen: {
      backgroundColor: teal[50],
    },
    tableRowGreen10: {
      backgroundColor: green[50],
    },
    tableRowGreen20: {
      backgroundColor: green[100],
    },
    tableRowGreen30: {
      backgroundColor: green[200],
    },
    tableRowGreen40: {
      backgroundColor: green[300],
    },
    tableRowGreen50: {
      backgroundColor: green[400],
    },
    tableRowGreen60: {
      backgroundColor: green[500],
      color: theme.palette.common.white,
    },
    tableRowGreen70: {
      backgroundColor: green[600],
      color: theme.palette.common.white,
    },
    tableRowGreen80: {
      backgroundColor: green[700],
      color: theme.palette.common.white,
    },
    tableRowGreen90: {
      backgroundColor: green[800],
      color: theme.palette.common.white,
    },
    tableRowGreen100: {
      backgroundColor: green[900],
      color: theme.palette.common.white,
    },
    tableRowRed: {
      backgroundColor: orange[50],
    },
    tableRowRed10: {
      backgroundColor: red[50],
    },
    tableRowRed20: {
      backgroundColor: red[100],
    },
    tableRowRed30: {
      backgroundColor: red[200],
    },
    tableRowRed40: {
      backgroundColor: red[300],
    },
    tableRowRed50: {
      backgroundColor: red[400],
      color: theme.palette.common.white,
    },
    tableRowRed60: {
      backgroundColor: red[500],
      color: theme.palette.common.white,
    },
    tableRowRed70: {
      backgroundColor: red[600],
      color: theme.palette.common.white,
    },
    tableRowRed80: {
      backgroundColor: red[700],
      color: theme.palette.common.white,
    },
    tableRowRed90: {
      backgroundColor: red[800],
      color: theme.palette.common.white,
    },
    tableRowRed100: {
      backgroundColor: red[900],
      color: theme.palette.common.white,
    },

    tableGenericCenteredCell: {
      textAlign: "center",
    },
    circularProgress: {
      textAlign: "center",
    },
    scrolledConrainer: {
      cursor: "auto",
      "&::-webkit-scrollbar": {
        width: theme.spacing(0.75),
        height: theme.spacing(1.25),
        cursor: "pointer !important",
      },
      "&::-webkit-scrollbar-track": {
        boxShadow: "none",
        webkitBoxShadow: "none",
        backgroundColor: "transparent",
        cursor: "pointer !important",
        outline: `1px solid ${theme.palette.scrollBg}`,
        borderRadius: "5px",
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: theme.palette.scrollBg,
        cursor: "pointer !important",
        borderRadius: "5px",
      },
    },
    container: {
      maxWidth: "calc(100vw - 200px - 3.5rem)",
      minWidth: "100%",
    },
    // containerClosed: {
    //   maxWidth: "calc(100vw - 7rem)",
    // },
    tableSortLabelProps: {
      // backgroundColor: theme.palette.primary.main,
      // color: "inherit !important",
      // textAlign: "center",
      // borderBottom: 0,
      // fontSize: "0.875rem",
      // fontWeight: "500",
    },
  }))();

export default useStyles;
