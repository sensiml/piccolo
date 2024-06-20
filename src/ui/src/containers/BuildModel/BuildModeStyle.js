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

const useStyles = (navBarIsOpen) =>
  makeStyles((theme) => ({
    ...theme.common,
    toptopPanelWrapperFixed: {
      zIndex: theme.zIndex.drawer - 1,
      position: "fixed",
      width: `calc(100% - 2rem ${navBarIsOpen ? "- 200px" : "- 56px"})`,
      top: "4rem",
      "@media (max-width: 900px)": {
        width: `calc(100% - 2rem ${navBarIsOpen ? "- 200px" : ""})`,
      },
      "@media (max-width: 800px)": {
        width: `100%`,
        top: "3.5rem",
        height: "3rem",
        left: 0,
      },
    },
    topPanelTopOverlap: {
      background: theme.backgroundApp,
      height: "1rem",
      zIndex: 1001,
    },
    topPanelWrapper: {
      minWidth: theme.responsive.minWidthContainer,
      "@media (max-width: 800px)": {
        margin: "auto",
        width: "calc(100% - 2rem)",
      },
    },
    topPanelBottomOverlap: {
      background: theme.backgroundApp,
      width: "calc(100%)",
      height: "0.5rem",
    },
    createDialogTitle: {
      marginBottom: theme.spacing(2),
      textAlign: "center",
    },
    // select page

    createCardDescList: {
      paddingInlineStart: theme.spacing(2),
      margin: 0,
    },
    createCardDescListItem: {
      marginTop: theme.spacing(1),
      lineHeight: "1.2",
    },
    queryAlert: {
      width: "100%",
    },
    builderContainer: {
      padding: theme.spacing(2),
    },
    builderFormCheckBoxWrapper: {
      display: "flex",
      justifyContent: "flex-start",
      alignItems: "center",
      columnGap: theme.spacing(2),
    },
    builderFormWrapper: {
      padding: `0 ${theme.spacing(4)}`,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-around",
    },
    builderDescription: {
      display: "flex",
      alignItems: "center",
    },
    // pipeline page
    stepperWrapper: {
      display: "flex",
      alignItems: "center",
      padding: "1rem 2rem",
    },
    stepperBackButton: {
      border: `1px solid ${theme.palette.primary.main}`,
      position: "absolute",
    },
    stepperRoot: {
      width: "80%",
      padding: 0,
      margin: "auto",
    },
    stepperLabel: {
      cursor: "pointer",
    },

    selectHeader: {
      fontWeight: 600,
      fontSize: theme.spacing(3),
      marginBottom: theme.spacing(3),
      marginTop: theme.spacing(3),
    },
    selectCard: {},
    selectCardGridWrapper: {
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(320px,1fr))",
      gap: theme.spacing(2),
    },
    selectCardInfoIcon: {
      color: theme.colorInfoLinks,
    },
    headerPipeline: {
      color: theme.colorBrandText,
    },

    pipelineSettingsWrapper: {
      display: "flex",
      alignItems: "flex",
      justifyContent: "flex-end",
      width: "100%",
    },
    pipelineIcon: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-start",
      width: "100%",
    },
    header: {
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(4),
      justifyContent: "center",
      fontWeight: 500,
      textAlign: "center",
      color: theme.colorBrandText,
      display: "flex",
      alignItems: "center",
    },
    infoTitle: {
      marginBottom: theme.spacing(4),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(4),
      fontWeight: 500,
      textAlign: "center",
    },
    cardWrapper: {
      marginTop: theme.spacing(2),
    },
    additionalSettingWrapper: {
      padding: theme.spacing(2),
    },
    builderWrapper: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      margin: "auto",
    },
    cardTextWrap: {
      cursor: "default",
      display: "grid",
      gap: theme.spacing(0.5),
      fontWeight: 400,
      marginLeft: theme.spacing(2.0),
      "& span:first-child": { fontWeight: 600, flex: "initial" },
      "& span:nth-child(2)": {
        flex: "auto",
        textAlign: "left",
      },
    },
    cardParamsWrapper: {
      "& span:nth-child(2)": {
        marginLeft: "auto",
      },
    },

    cardParamsWrap: {
      display: "flex-inline",
      lineHeight: "1.1",

      "& span": { color: theme.colorInfoText },
      "& span:first-child": {
        color: theme.colorInfoText,
        fontWeight: 400,
        marginRight: ".5rem",
      },
    },
    stepWrapper: {
      display: "grid",
      justifyContent: "center",
      gridRow: "auto",
      gridTemplateColumns: "1fr",
      width: "100%",
      maxWidth: "550px",
      margin: "auto",
    },
    pipelineBuilderWrapper: {
      width: "100%",
      display: "flex",
      flexDirection: "column",
      maxWidth: "630px",
      margin: "auto",
    },
    cardStep: {
      marginBottom: "3rem",
    },
    cardStepDisabledToEdit: {
      opacity: "0.8",
      zIndex: "100",
      transition: theme.transitions.create(["width"], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
    },
    IconWrapper: {
      height: theme.spacing(5),
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
    },
    cardInfoIcon: {
      cursor: "pointer",
      marginLeft: theme.spacing(0.5),
      display: "flex",
      alignItems: "center",
    },

    NewCardWrapper: {
      height: theme.spacing(18),
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      width: "100%",
      maxWidth: "550px",
      margin: "auto",
    },
    fullWidthIcon: {
      position: "absolute",
      zIndex: 0,
    },
    drawerHeader: {
      marginBottom: theme.spacing(2),
      marginTop: theme.spacing(2),
      fontSize: theme.spacing(3),
      fontWeight: 600,
      color: theme.palette.notSelected?.main,
    },
    drawerHeaderAlert: {
      display: "flex",
      alignItems: "center",
    },
    drawerHeaderAlertIcon: {
      marginRight: theme.spacing(1),
    },
    drawerInfoText: {
      marginTop: theme.spacing(2),
      marginBottom: theme.spacing(2),
      fontSize: theme.spacing(2),
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      color: theme.colorInfoText,
    },
    drawerInfoPreDescription: {
      margin: "-1rem",
      color: theme.palette.notSelected?.main,
    },
    formDrawerRoot: {
      zIndex: theme.zIndex.drawer + 3,
    },
    formDrawerSizing: {
      width: "55vw",
      boxSizing: "border-box",
      "@media (min-width: 1650px)": {
        width: "50vw",
      },
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
    // drawe common
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
      "&:first-child": {
        marginRight: "1rem",
      },
    },
    infoDrawer: {
      padding: theme.spacing(4),
      paddingTop: theme.spacing(8),
    },
    drawerContent: {
      whiteSpace: "pre-wrap",
    },
    infoDrawerContext: {
      padding: theme.spacing(4),
      paddingTop: theme.spacing(8),
    },
    descriptionContainer: {
      margin: `${theme.spacing(2)} 0`,
    },
    descriptionParamsWrapper: {
      display: "flex",
      flexDirection: "row",
    },
    descriptionParamsWrap: {
      justifyContent: "flex-start",
      alignItems: "center",
      display: "flex",
      flex: 2,
      marginTop: theme.spacing(1),
      marginBottom: theme.spacing(1),
      "&:first-child": {
        fontWeight: 600,
        flex: 1,
        color: theme.colorBrandText,
      },
    },
    paramChipItem: {
      margin: theme.spacing(0.5),
    },
    // forms
    formControl: {
      marginTop: theme.spacing(2),
      marginBottom: theme.spacing(2),
      position: "relative",
    },
    helpIcon: {
      cursor: "pointer",
      color: theme.colorInfoLinks,
      position: "absolute",
      right: `-${theme.spacing(4)}`,
      top: "30%",
    },
    actionButton: {
      width: "100%",
      textTransform: "uppercase",
      fontSize: "1rem",
      padding: "0.75rem",
      transition: "all 0.1s linear",
    },
    scrollButton: {
      padding: 0,
      transition: "all 0.1s linear",
    },
    customName: {
      fontWeight: "500",
    },
    dangerColor: {
      color: theme.palette.error.light,
    },
    chartMetricsWrapper: {
      marginTop: theme.spacing(2),
      padding: `${theme.spacing(2)}`,
      height: theme.spacing(55),
    },
    fixedOptimizeButtonWrapper: {
      bottom: 0,
      zIndex: "999",
      // background: "#f4f5f7",
      width: "35rem",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      position: "fixed",
      paddingBottom: "0.5rem",
      paddingTop: "0.5rem",
      transition: "all 0.2s linear",
      "@media (max-width: 1600px)": {
        width: "30rem",
      },
      "@media (max-width: 1366px)": {
        width: "27rem",
      },
    },

    // warning dialog
    dialogTable: {
      width: "100%",
    },
    dialogTableRow: {
      "& h6": {
        display: "table-cell",
      },
    },
    groupBox: {
      borderLeft: "5px solid rgb(4 118 190 / 66%)",
      borderRight: "5px solid rgb(4 118 190 / 66%)",
      borderBottom: "5px solid rgb(4 118 190 / 66%)",
      margin: "auto",
      maxWidth: "580px",
      padding: "1rem",
      borderRadius: "5px",
      paddingBottom: "0",
      position: "relative",
      marginTop: "1rem",
      "&::before": {
        content: "''",
        width: "30%",
        height: "5px",
        left: "0",
        top: "0",
        position: "absolute",
        zIndex: "9",
        background: "rgb(4 118 190 / 66%)",
      },
      "&::after": {
        content: "''",
        width: "30%",
        height: "5px",
        right: "0",
        top: "0",
        position: "absolute",
        zIndex: "9",
        background: "rgb(4 118 190 / 66%)",
      },
    },
    groupHeader: {
      display: "flex",
      justifyContent: "center",
      marginBottom: "1rem",
      fontSize: "1.25rem",
      color: "#0277be",
      fontWeight: 600,
      position: "relative",
      marginTop: "-1.75rem",
    },
  }))();

export default useStyles;
