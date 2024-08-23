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
  makeStyles(() => ({
    root: {
      flexGrow: 1,
    },
    paper: {
      paddingTop: 2,
    },
    box: {
      minWidth: 245,
      minHeight: 400,
      paddingRight: 20,
    },
    mainLoader: {
      position: "absolute",
      paddingTop: "15%",
      width: "100%",
      height: "100%",
      zIndex: 1000,
      backgroundColor: "#000000",
      opacity: 0.5,
      textAlign: "center",
    },
    grid: {
      flexGrow: 1,
    },
    innerGrid: {
      flexGrow: 0,
    },
    noProjectsMessage: {
      flexGrow: 0,
      paddingTop: 50,
      paddingBottom: 50,
    },
    loadMoreButton: { marginBottom: 10 },
  }))();

export default useStyles;
