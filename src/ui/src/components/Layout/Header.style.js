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

const drawerWidth = 200;

const useStyles = () =>
  makeStyles((theme) => ({
    ...theme.common,
    root: {
      display: "flex",
    },
    projectHeaderLink: {
      cursor: "pointer",
    },
    appBar: {
      background: "white",
      color: theme.typography.h2.color,
      zIndex: theme.zIndex.drawer + 1,
      transition: theme.transitions.create(["width", "margin"], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      "&:before": {
        position: "absolute",
        bottom: "0",
        content: "''",
        height: "2px",
        width: "100%",
        background: theme.borderBrandGradient,
      },
    },
    toolbar: {
      display: "flex",
      alignItems: "center",
      "& img": {
        maxHeight: "24px",
      },
      "@media (max-width: 900px)": {
        marginLeft: 0,
        width: 0,
      },
      // marginLeft: drawerWidth,
      // width: `calc(100% - ${drawerWidth + 1}px)`,
      // transition: theme.transitions.create(["width", "margin"], {
      //   easing: theme.transitions.easing.sharp,
      //   duration: theme.transitions.duration.enteringScreen,
      // }),
    },
    menuButton: {
      marginLeft: ".25em",
      marginRight: ".25em",
    },
    hide: {
      display: "none",
    },
    drawerOpen: {
      width: drawerWidth,
      transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
    },
    drawerClose: {
      transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      overflowX: "hidden",
      width: theme.spacing(7) + 1,
      [theme.breakpoints.up("sm")]: {
        width: theme.spacing(7) + 1,
      },
      [theme.breakpoints.down("md")]: {
        width: 0,
        display: "none",
      },
    },

    rightToolbar: {
      marginLeft: 0,
      marginRight: -15,
      "@media (max-width: 310px)": {
        marginRight: 10,
      },
    },
    title: { paddingLeft: 10 },
    titleWithProjectName: { margin: "auto" },
    mainToolbar: {
      paddingLeft: 0,
      paddingRight: 24,
      "@media (min-width: 600px)": {
        paddingRight: 12,
      },
      "@media (min-width: 1440px)": {
        paddingRight: 24,
      },
    },
    iconButton: {
      minWidth: 25,
    },
    closeChevron: {
      padding: 0,
    },
    selectedMenuText: {
      color: theme.palette.primary.main,
    },
    disabledMenuText: {
      color: theme.palette.notSelected?.main,
    },
    accountCircle: {
      paddingRight: 4,
    },
    accountUpgradeListItem: {
      background: "#0ca1c7",
      color: "white",
      paddingTop: "0.75rem",
      paddingBottom: "0.75rem",
    },
  }))();

export default useStyles;
