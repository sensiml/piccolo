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
    root: {
      flexGrow: 1,
    },
    resetedTab: {
      padding: 0,
    },
    mainHeader: {
      paddingLeft: 10,
    },
    box: {
      minHeight: 400,
      paddingRight: 5,
      paddingBottom: 20,
    },
    actionsBtns: {
      marginLeft: "auto",
      alignItems: "center",
      display: "flex",
    },
    summaryPanel: {
      minHeight: "70vh",
      background: theme.backgroundElements,
    },
    redreshButton: {
      marginTop: theme.spacing(1),
    },
    rightAlign: {
      marginLeft: "auto",
      flat: "right",
    },
  }))();

export default useStyles;
