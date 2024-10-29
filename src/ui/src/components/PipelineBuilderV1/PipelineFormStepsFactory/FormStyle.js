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
    formSubtypeWrapper: {
      display: "grid",
      gridTemplateColumns: "50% 50%",
    },
    addButtonWrapper: {
      display: "flex",
      marginTop: theme.spacing(2),
      marginBottom: theme.spacing(2),
      gap: theme.spacing(1),
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
        width: "50vw",
      },
      "@media (max-width: 900px)": {
        width: "95vw",
      },
    },
    drawerFormButton: {
      minWidth: theme.spacing(15),
      textTransform: "uppercase",
      marginRight: "1rem",
    },
    formCreateWrapper: {
      display: "flex",
      flexDirection: "column",
    },
    formCreateFormControl: {
      marginBottom: theme.spacing(1),
      marginTop: theme.spacing(1),
    },
    // feature forms
    subtypesWrapper: {
      display: "flex",
      flexDirection: "column",
    },
    subtypesWrap: {
      // marginBottom: theme.spacing(2),
    },
    wrapperCheckHeader: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-start",
    },
    featureFormSubtypeHeaderClicked: {
      cursor: "pointer",
      "&:hover": {
        color: theme.palette.primary.main,
        fontWeight: 600,
      },
    },
    wrapperCheckFeatureHeader: {
      cursor: "pointer",
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-start",
      padding: `${theme.spacing(1)} 0`,
    },
    featureFormSubtypeHeader: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      marginBottom: theme.spacing(1),
    },
    featureFormSubtypeHeaderTitle: {
      fontSize: theme.spacing(2.25),
      fontWeight: 600,
      color: theme.palette.notSelected?.main,
    },
    columnsRow: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      flexFlow: "wrap",
      gap: "0.25rem",
      padding: "0.5rem",
    },
    borderedFormWrapper: {
      border: "1px solid #0277be73",
      borderRadius: "5px",
    },
    collapseFormWrapper: {
      width: "100%",
      borderBottom: "1px solid transparent",
    },
    formWrapper: {
      padding: "0 1rem",
    },
    formDefaultWrapper: {
      marginBottom: theme.spacing(2),
    },
    formControl: {
      marginBottom: theme.spacing(2),
      position: "relative",
    },
    collapseFormSummary: {
      display: "flex",
      alignItems: "center",
      width: "100%",
      justifyContent: "space-between",
    },
    collapseFormSummaryIconsWrapper: {
      display: "flex",
      justifyContent: "flex-end",
    },
    formFeatureCreateSubtype: {
      fontSize: theme.spacing(2),
      color: theme.palette.primary.main,
    },
  }))();

export default useStyles;
