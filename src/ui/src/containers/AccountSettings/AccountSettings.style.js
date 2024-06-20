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
    cardTitle: {
      lineHeight: theme.spacing(3),
      fontSize: theme.spacing(3),
      fontWeight: 500,
    },
    cardSubtitle: {
      lineHeight: theme.spacing(3),
      fontSize: theme.spacing(2.5),
      fontWeight: 500,
    },
    cartItemKey: {
      flex: 1,
      fontWeight: 500,
      fontSize: theme.spacing(2),
      lineHeight: theme.spacing(2.5),
      color: theme.palette.text.secondary,
    },
    cartItemValue: {
      flex: 1,
      fontSize: theme.spacing(2),
      lineHeight: theme.spacing(2.5),
    },
    cardActions: {
      justifyContent: "flex-start",
      borderTop: `1px solid ${theme.palette.divider}`,
      padding: `${theme.spacing(2)} ${theme.spacing(4)}`,
    },
  }))();

export default useStyles;
