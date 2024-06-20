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
    root: {
      background: theme.backgroundApp,
      minHeight: "calc(100vh - 65px)",
    },
    header: {
      marginBottom: theme.spacing(2),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(3),
      fontWeight: 600,
      color: theme.palette.notSelected?.main,
    },
    downloadWrapper: {
      //
    },
    cardBoardWrapper: {
      gap: "1rem",
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
    },
    cardElementWrapper: {
      padding: `${theme.spacing(2)} ${theme.spacing(4)}`,
    },
    cardWrapper: {
      alignItems: "flex-start",
      justifyContent: "center",
    },
    selectedPlatformLabel: {
      display: "flex",
      justifyContent: "space-between",
    },
    selectedPlatformTitle: {
      fontSize: theme.spacing(2.25),
      fontWeight: 600,
      color: theme.palette.primary.dark,
    },
    selectedPlatformLabelBtn: {
      border: `1px solid ${theme.palette.primary.main}`,
    },
    formControl: {
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
      position: "relative",
    },
    formControlPlatform: {
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
      position: "relative",
      borderBottom: 0,
    },
    helpIcon: {
      color: theme.palette.notSelected.light,
      position: "absolute",
      right: `${theme.spacing(3)}`,
      top: `${theme.spacing(3)}`,
    },
    profileHelpIcon: {
      color: theme.colorInfoLinks,
      position: "static",
      right: `${theme.spacing(1)}`,
      top: `${theme.spacing(0)}`,
    },
    formControlHelper: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    },
    formTitle: {
      marginBottom: theme.spacing(1),
      fontSize: theme.spacing(2.25),
      fontWeight: 600,
      color: theme.palette.primary.dark,
    },
    formSubTitle: {
      marginBottom: theme.spacing(2),
      fontSize: theme.spacing(2),
      fontWeight: 500,
      color: theme.palette.primary.dark,
    },
    classMaps: {
      margin: theme.spacing(1),
      justifyContent: "flex-start",
      flexWrap: "wrap",
    },
    classMap: {
      marginRight: theme.spacing(0.5),
      marginBottom: theme.spacing(0.5),
    },

    advancedSettingsNoHeight: { height: 0 },
    submitButtonsWrapper: {
      margin: `0 ${theme.spacing(1)}`,
    },
    actionButton: { width: "100%", marginTop: theme.spacing(2) },
    progressbarWrapper: {
      maxWidth: "100%",
      minHeight: "60vh",
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
    },
    progressbar: { width: "400px", marginTop: theme.spacing(1) },
    progressText: { marginTop: theme.spacing(1) },
    progressTextWarning: {
      marginTop: theme.spacing(1),
      padding: theme.spacing(2),
    },
    errorButtonWrapper: {
      display: "flex",
      width: "100%",
      justifyContent: "center",
    },
    goBackBtn: {
      minWidth: "160px",
      margin: theme.spacing(1),
      marginTop: theme.spacing(2),
    },
    grid: {},
    infoList: { padding: "0 !important" },
    infoListItem: { alignItems: "flex-start" },
    prefix: { marginRight: theme.spacing(1), minWidth: "100px" },
    upButtom: { marginBottom: "-1rem" },
    captureSubList: {
      marginTop: "-1rem",
    },
    captureSubListItem: {
      paddingLeft: theme.spacing(0),
    },
    captureSubSubList: {
      marginLeft: theme.spacing(2),
    },
    profileList: {
      marginTop: "1rem",
    },
  }))();

export default useStyles;
