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

import React, { Component } from "react";
import withStyles from "@mui/styles/withStyles";
import { Typography } from "@mui/material";

const styles = {
  root: {
    display: "flex",
    justifyContent: "center",
    padding: "20px",
  },
};

/* Used for default text if no content found for table/list */
// eslint-disable-next-line react/prefer-stateless-function
class NoContent extends Component {
  render() {
    const { classes, text, children } = this.props;
    return (
      <div className={classes.root}>
        <Typography variant="body1">{text || "No Content"}</Typography>
        {children}
      </div>
    );
  }
}

export default withStyles(styles)(NoContent);
