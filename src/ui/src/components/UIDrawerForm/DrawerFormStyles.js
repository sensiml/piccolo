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
    drawerHeader: {
      marginBottom: theme.spacing(2),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(3),
      fontWeight: 600,
      color: theme.palette.notSelected?.main,
    },
    formDrawerRoot: {
      zIndex: theme.zIndex.drawer + 3,
    },
    formDrawerSizing: {
      boxSizing: "border-box",
      width: "55vw",
      "@media (max-width: 900px)": {
        width: "95vw",
      },
    },
    formStepDrawerContext: {
      // width: "50vh",
      padding: theme.spacing(4),
      paddingTop: theme.spacing(8),
      paddingRight: theme.spacing(8),
      paddingBottom: theme.spacing(10),
    },
    drawerContent: {
      whiteSpace: "pre-wrap",
    },
    drawerFormButtonWrapper: {
      zIndex: theme.zIndex.drawer + 3,
      boxSizing: "border-box",
      position: "fixed",
      right: 0,
      bottom: 0,
      display: "flex",
      marginTop: theme.spacing(2),
      justifyContent: "flex-end",
      padding: theme.spacing(2),
      background: theme.backgroundElements,
      borderTop: `1px solid ${theme.palette.primary.main}`,
      width: "55vw",
      "@media (min-width: 1650px)": {
        width: "55vw",
      },
      "@media (max-width: 900px)": {
        width: "95vw",
      },
    },
    drawerFormButton: {
      minWidth: theme.spacing(15),
      textTransform: "uppercase",
      "&:first-child": {
        marginRight: "1rem",
      },
    },
  }))();

export default useStyles;
