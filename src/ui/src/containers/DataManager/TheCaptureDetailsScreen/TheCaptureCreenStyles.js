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
    // CaptureLabelingPanel
    sementsChartPanelWrapper: {
      display: "grid",
      padding: "1rem",
      gridTemplateColumns: "35% 30% 35%",
      width: "calc(100% - 2rem)",
      alignItems: "center",
    },

    sementsChartPanelCenterWrap: {
      display: "flex",
      margin: "auto",
      justifyContent: "center",
      fontWeight: 500,
      color: theme.palette.primary.main,
    },

    labelingPanelActionWrapper: {
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-end",
      height: "100%",
      gap: theme.spacing(2),
    },

    labelWrapper: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: "100%",
    },
    labelActionWrapper: {
      display: "flex",
      alignItems: "center",
      gap: theme.spacing(2),
      height: "100%",
    },
    labelSelector: {
      minWidth: "200px",
    },
    labelActionButton: {
      border: `1px solid ${theme.palette.primary.main}`,
      // marginRight: theme.spacing(2),
    },
    loadingBox: {
      position: "absolute",
      top: 0,
      width: "100%",
    },
    // CaptureLabelingPanel
    cordinateWrap: {
      display: "flex",
      flexDirection: "column",
      justifyContent: "center",
      alignItems: "center",
      margin: `0 ${theme.spacing(2)}`,
    },
    captureMetadataWrapper: {
      display: "flex",
      maxWidth: theme.spacing(80),
      paddingLeft: theme.spacing(4),
    },
    chartInformationWrapper: {
      padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      gap: theme.spacing(1),
      borderBottom: `2px solid ${theme.backgroundApp}`,
    },
    chartInformation: {
      display: "flex",
      gap: theme.spacing(1),
      "@media (max-width: 1400px)": {
        minWidth: "30%",
      },
      "@media (max-width: 900px)": {
        flexDirection: "column",
        gap: "0",
      },
    },
    chartInformationAlertWholeLine: {
      width: "100%",
      borderBottom: `2px solid ${theme.backgroundApp}`,
      "& .MuiAlert-root": {
        padding: "0 0.5rem",
      },
    },
    chartInformationHeader: {
      color: theme.palette.primary.main,
      fontWeight: 500,
      marginRight: theme.spacing(1),
    },
  }))();

export default useStyles;
