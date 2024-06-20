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

import React, { useState, useEffect, Fragment } from "react";
import { useSelector } from "react-redux";
import helper from "store/helper";
import { Grid, Card, CardHeader, CardContent, Avatar, Typography } from "@mui/material";
import useStyles from "./DetailViewStyles";
// eslint-disable-next-line import/no-cycle
import { getIcon, getTitle } from "../PipelineBuilderConstants";

export default function InputCard({ pipeline }) {
  const classes = useStyles();
  const [query, setQuery] = useState(null);
  const [session, setSession] = useState(null);
  const queries = useSelector((state) => state.queries.queryList.data);
  const sessions = useSelector((state) => state.sessions.data);

  useEffect(() => {
    if (!pipeline || pipeline.type !== "query" || !queries) return;
    const qry = queries.find((q) => q.name === pipeline.name);
    setQuery(qry);
    setSession(sessions.find((s) => s.id === qry.segmenter_id));
  }, [pipeline, queries]);

  return (
    <Card className={`${classes.root} ${classes.card}`}>
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
          {query ? (
            <>
              <Grid item xs={3}>
                <Typography className={classes.title}>Session:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography className={classes.pos}>{(session || { name: "" }).name}</Typography>
              </Grid>
              <Grid item xs={1} />
              <Grid item xs={3}>
                <Typography className={classes.title}>Label:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography className={classes.pos}>{query.label_column}</Typography>
              </Grid>
              <Grid item xs={1} />
              <Grid item xs={3}>
                <Typography className={classes.title}>Metadata:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography className={classes.pos}>
                  {query.metadata_columns && query.metadata_columns.length > 0
                    ? query.metadata_columns.join(", ")
                    : ""}
                </Typography>
              </Grid>
              <Grid item xs={1} />
              <Grid item xs={3}>
                <Typography className={classes.title}>Source:</Typography>
              </Grid>
              <Grid item xs={8}>
                <Typography className={classes.pos}>
                  {query.columns && query.columns.length > 0 ? query.columns.join(", ") : ""}
                </Typography>
              </Grid>
              <Grid item xs={1} />
              {!helper.isNullOrEmpty(query.metadata_filter) ? (
                <>
                  <Grid item xs={3}>
                    <Typography className={classes.title}>Query Filter:</Typography>
                  </Grid>
                  <Grid item xs={8}>
                    <Typography className={classes.pos}>{query.metadata_filter}</Typography>
                  </Grid>
                  <Grid item xs={1} />
                </>
              ) : null}
            </>
          ) : null}
        </Grid>
      </CardContent>
    </Card>
  );
}
