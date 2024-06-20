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
    importDialogStepperRoot: {
      padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
      marginBottom: theme.spacing(2),
    },
    builderContainer: {
      padding: theme.spacing(2),
      width: "750px",
      minHeight: "60vh",
      margin: "auto",
      alignItems: "center",
    },

    builderFormWrapper: {
      padding: 0,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-around",
    },

    builderFormWrap: {
      width: "100%",
      display: "flex",
      marginBottom: theme.spacing(3),
    },
    builderDescriptionWrapper: {
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      width: "100%",
      margin: "0 0 1rem 0",
    },
    builderDescription: {
      padding: 0,
      width: "100%",
    },

    submitBtn: {
      marginTop: theme.spacing(2),
    },

    alertMessage: {
      minHeight: "60px",
      overflowY: "auto",
      paddingTop: theme.spacing(2),
      width: "100%",
      whiteSpace: "pre-line",
    },

    alertIcon: {
      padding: theme.spacing(1),
    },

    queryReplacementFormKey: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      paddingRight: theme.spacing(2),
    },
  }))();

export default useStyles;
