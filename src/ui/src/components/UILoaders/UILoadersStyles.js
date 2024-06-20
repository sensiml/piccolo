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
    apploaderIcon: {
      color: theme.colorLoader,
    },
    messageLoader: {
      color: theme.colorBrandText,
    },
    appBackdrop: {
      backgroundColor: theme.backgroundLoaderBackdrop,
      flexDirection: "column",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    },
    elementBackdrop: {
      width: "100%",
      height: "100%",
      flexDirection: "column",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      minHeight: theme.spacing(20),
      backgroundColor: theme.backgroundLoaderElementBackdrop,
      zIndex: 1,
    },
  }))();

export default useStyles;
