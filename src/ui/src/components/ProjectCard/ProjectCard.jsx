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

import React, { Fragment } from "react";
import { useDispatch } from "react-redux";
import { Box, Divider, FormControl, Grid, Tooltip, Typography, Button } from "@mui/material";
import useStyles from "./ProjectCardStyles";

const ProjectCard = ({ project, setActiveView, setActiveProject }) => {
  const dispatch = useDispatch();
  const classes = useStyles();
  const defaultBoxProps = {
    boxShadow: 3,
    m: 1,
    p: 2,
    borderRadius: "borderRadius",
  };
  const defaultTextTypoProps = {
    variant: "subtitle1",
    align: "center",
  };
  const defaultNumberTypoProps = {
    variant: "h6",
    component: "h6",
    align: "center",
  };
  const numericRenderer = (value) => {
    return value ? Math.round(parseFloat(value)) : 0;
  };

  const tiles = [
    {
      index: 1,
      title: "Files",
      tooltip: "Number Files in the project",
      count: project.files,
      style: classes.filesBox,
    },
    {
      index: 2,
      title: "Pipelines",
      tooltip: "Number of Pipelines in the project",
      count: project.pipelines,
      style: classes.pipelineBox,
    },
    {
      index: 3,
      title: "Size",
      tooltip: "Size of the project in MB",
      count: project.size_mb,
      style: classes.sizeBox,
    },
    {
      index: 4,
      title: "Queries",
      tooltip: "Number of Queries in the project",
      count: project.queries,
      style: classes.queriesBox,
    },
    {
      index: 5,
      title: "Models",
      tooltip: "Number of Models in the project",
      count: project.models,
      style: classes.modelsBox,
    },
  ];
  const showDetailsView = () => {
    dispatch(setActiveView(1));
    dispatch(setActiveProject(project.uuid));
  };
  return (
    <Box boxShadow={3} m={1} p={1} className={classes.box} alignItems="center">
      <Tooltip title={project.name}>
        <Typography variant="h5" component="h5" align="center" noWrap>
          {" "}
          {project.name}
        </Typography>
      </Tooltip>
      <Divider className={classes.divider} />
      <Grid container spacing={2}>
        <Grid item xs>
          <Grid container className={classes.grid} spacing={2}>
            {tiles.map((tile) => {
              return (
                <Fragment key={tile.index}>
                  <Grid item xs={4} style={{ textAlign: "center" }}>
                    <Tooltip title={tile.tooltip}>
                      <Box {...defaultBoxProps} className={`${tile.style} + ${classes.numberBox}`}>
                        <Typography {...defaultNumberTypoProps}>
                          {numericRenderer(tile.count)}
                        </Typography>
                      </Box>
                    </Tooltip>
                    <Typography {...defaultTextTypoProps}>{tile.title}</Typography>
                  </Grid>
                  {tile.index % 3 === 0 && tile.index !== tiles.length ? (
                    <Grid item xs={12}>
                      <Divider className={classes.divider} />
                    </Grid>
                  ) : null}
                </Fragment>
              );
            })}
          </Grid>
        </Grid>
      </Grid>
      <Divider className={classes.divider} />
      <FormControl fullWidth>
        <Tooltip title="Click here for project details.">
          <Button
            size="small"
            color="primary"
            className={classes.detailsButton}
            onClick={showDetailsView}
          >
            Details ...
          </Button>
        </Tooltip>
      </FormControl>
    </Box>
  );
};

export default ProjectCard;
