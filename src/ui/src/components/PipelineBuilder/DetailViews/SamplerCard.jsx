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

import React, { useState, useEffect } from "react";
import { Avatar, Card, CardHeader, CardContent, Grid, Typography } from "@mui/material";
import useStyles from "./DetailViewStyles";
import DescriptionSection from "./DescriptionSection";
// eslint-disable-next-line import/no-cycle
import { getIcon, getTitle, renderInputRows } from "../PipelineBuilderConstants";

export default function SamplerCard({ pipeline, transforms }) {
  const classes = useStyles();
  const [transform, setTransform] = useState(null);
  useEffect(() => {
    if (!pipeline || !transforms) return;
    setTransform(transforms.find((t) => t.name === pipeline.name));
  }, [pipeline, transforms]);

  return (
    <Card className={`${classes.root}, ${classes.card}`}>
      <CardHeader
        avatar={
          <Avatar aria-label={pipeline.type} className={classes.avatar}>
            {getIcon(pipeline.type)}
          </Avatar>
        }
        titleTypographyProps={{ variant: "h4" }}
        title={getTitle(pipeline.type)}
      />
      <CardContent>
        <Grid container spacing={1}>
          <Grid item xs={3}>
            <Typography className={classes.title}>Name:</Typography>
          </Grid>
          <Grid item xs={8}>
            <Typography className={classes.pos}>{pipeline.name}</Typography>
          </Grid>
          <Grid item xs={1} />
          <Grid item xs={3}>
            <Typography className={classes.title}>Type:</Typography>
          </Grid>
          <Grid item xs={8}>
            <Typography className={classes.pos}>{pipeline.type}</Typography>
          </Grid>
          <Grid item xs={1} />
          {renderInputRows(transform, pipeline.inputs, classes)}
        </Grid>
      </CardContent>
      <DescriptionSection transform={transform} />
    </Card>
  );
}
