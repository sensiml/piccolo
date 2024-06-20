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
    cardStepWrapper: {
      padding: "0.25rem 0.75rem",
      boxSizing: "border-box",
      display: "inline-flex",
      zIndex: 1,
      minHeight: "5.5rem",
      transition: theme.transitions.create(["width", "visibility", "show"], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
      width: "100%",
      /* "@media (max-width: 1366px)": {
        width: "27rem",
      },
      "@media (max-width: 900px)": {
        width: "20rem",
      },
      */
    },
    cardDisable: {
      opacity: "0.6",
      pointerEvents: "none",
      cursor: "no-drop",
      zIndex: "100",
      width: "90%",
      margin: "auto",
      transition: theme.transitions.create(["width"], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
    },
    customStepWrapper: {
      // padding: "0.75rem 0",
      boxSizing: "border-box",
      // width: "30rem",
      display: "flex",
      justifyContent: "center",
      zIndex: 1,
      transition: theme.transitions.create(["width"], {
        easing: theme.transitions.easing.sharp,
        duration: theme.transitions.duration.leavingScreen,
      }),
    },
    arrDisable: {
      opacity: "0.6",
      pointerEvents: "none",
      cursor: "no-drop",
      zIndex: "100",
    },
    IconWrap: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    ActionWrap: {
      display: "flex",
      justifyContent: "flex-end",
      alignItems: "center",
    },
    ActionIcon: {
      cursor: "pointer",
      marginTop: theme.spacing(0.5),
    },
    cardStepRegular: {
      borderPosition: "",
    },
    cardStepRegularNew: {
      borderPosition: "",
      border: `1px dashed ${theme.colorNewItems}`,
    },
    cardStepIcon: {
      fontSize: "2rem",
    },
    cardStepActionIcon: {
      fontSize: "1.5rem",
      borderRadius: "100%",
    },
    TextWrap: {
      width: "100%",
      alignItems: "center",
      display: "flex",
      padding: "0.75rem 0",
    },
    "@media (min-width: 1600px)": {
      cardStepIcon: {
        fontSize: "2rem",
      },
      cardStepActionIcon: {
        fontSize: "1.75rem",
      },
    },
    ...theme.common,
  }))();

export default useStyles;
