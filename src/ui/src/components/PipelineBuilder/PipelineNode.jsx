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

import React, { memo } from "react";
import { Box, Grid } from "@mui/material";
import useStyles from "./PipelineBuilderStyles";
import { getIcon, getNodeStyle } from "./PipelineBuilderConstants";

export default memo(({ data }) => {
  const classes = useStyles();
  const nodeStyle = getNodeStyle(data.pipeline.type, classes);

  return (
    <Box boxShadow={data.shadow} p={2} borderRadius="3%" className={nodeStyle} width={data.width}>
      <Grid container direction="row" justifyContent="center" alignItems="center" spacing={1}>
        <Grid item xs={2}>
          {getIcon(data.pipeline.type)}
        </Grid>
        <Grid item xs={10}>
          <Grid container spacing={0}>
            <Grid item xs={4}>
              Name:
            </Grid>
            <Grid item xs={8}>
              {data.pipeline.name}
            </Grid>
            <Grid item xs={4}>
              Type:
            </Grid>
            <Grid item xs={8}>
              {data.pipeline.type}
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
});
