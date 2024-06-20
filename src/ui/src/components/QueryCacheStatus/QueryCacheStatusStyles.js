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

import { makeStyles } from "@mui/styles";

const useStyles = () =>
  makeStyles((theme) => ({
    statusBox: {
      padding: "0.25rem 0.5rem",
      border: `2px solid ${theme.palette.notSelected.light}`,
      borderRadius: "4px",
      display: "flex",
      alignItems: "center",
      justifyContent: "flex-start",
      color: "gray",
      textTransform: "uppercase",
      width: theme.spacing(14),
      gridGap: theme.spacing(1),
    },
    statusBoxCached: {
      borderColor: theme.palette.success.light,
      color: theme.palette.success.light,
    },
    statusBoxBuilding: {
      borderColor: theme.palette.primary.main,
      color: theme.palette.primary.main,
    },
    statusBoxFailed: {
      borderColor: theme.palette.error.main,
      color: theme.palette.error.main,
    },
  }))();

export default useStyles;
