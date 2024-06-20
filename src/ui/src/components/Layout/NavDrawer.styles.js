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
    drawer: {
      marginTop: 64,
      backgroundColor: theme.backgroundAppElement,
      width: 200,
      flexShrink: 0,
      whiteSpace: "nowrap",
      "@media (max-width: 600px)": {
        marginTop: 56,
      },
    },
    drawerScrolled: {
      "&::-webkit-scrollbar": {
        width: theme.spacing(0.25),
        height: theme.spacing(1.25),
        cursor: "pointer !important",
      },
      "&::-webkit-scrollbar-track": {
        boxShadow: "none",
        webkitBoxShadow: "none",
        backgroundColor: "transparent",
        cursor: "pointer !important",
        // outline: `1px solid ${theme.borderBrandTransparent}`,
        borderRadius: "5px",
      },
      "&::-webkit-scrollbar-thumb": {
        backgroundColor: theme.palette.primary.main,
        cursor: "pointer !important",
        borderRadius: "5px",
      },
    },
    drawerOpen: {
      width: 200,
      transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.enteringScreen,
      }),
    },

    navListsWrapper: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "space-between",
    },

    navListsBottomWrapper: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    },

    listWrapper: {
      width: "100%",
    },

    menuListItem: {
      height: theme.spacing(6),
    },

    navLink: {
      textDecoration: "none",
      alignItems: "center",
      display: "flex",
      justifyContent: "flex-start",
      color: "grey",
      "&svg": {
        color: "red",
      },
    },

    drawerClose: {
      transition: theme.transitions.create("width", {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      overflowX: "hidden",
      width: theme.spacing(7),
      [theme.breakpoints.up("sm")]: {
        width: theme.spacing(7),
      },
      [theme.breakpoints.down("md")]: {
        width: 0,
        display: "none",
      },
    },
    toolbar: {
      display: "flex",
      alignItems: "center",
    },
    iconButton: {
      minWidth: 40,
    },
    selectedMenuText: {
      color: theme.palette.primary.main,
      backgroundColor: theme.bakgroundSelected,
      "& svg": {
        color: theme.palette.primary.main,
      },
    },
    disabledMenuText: {
      color: theme.palette.notSelected?.main,
    },
  }))();

export default useStyles;
