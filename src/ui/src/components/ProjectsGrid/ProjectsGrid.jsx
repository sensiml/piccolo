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

import React, { useEffect } from "react";
import { Button, Grid, Paper, Typography } from "@mui/material";
import ProjectCard from "components/ProjectCard";
import ErrorBoundary from "components/ErrorBoundary";

import useStyles from "./ProjectsGridStyles";

const ProjectsGrid = ({ projectData, initialPageSize, setSelectedProject, setActiveView }) => {
  const [projectList, setProjectList] = React.useState(projectData);
  const [pageSize, setPageSize] = React.useState(initialPageSize);

  const classes = useStyles();

  const handleLoadMore = () => {
    setPageSize(pageSize + 10);
  };

  useEffect(() => {
    setProjectList(projectData);
  }, [projectData]);

  return (
    <ErrorBoundary>
      <Paper className={classes.paper}>
        <Grid container className={classes.grid} spacing={2}>
          {projectList.length > 0 ? (
            projectList.slice(0, pageSize).map((project) => {
              return (
                <Grid item xs key={project.uuid} className={classes.innerGrid}>
                  <ProjectCard
                    project={project}
                    setActiveView={setActiveView}
                    setActiveProject={setSelectedProject}
                  />
                </Grid>
              );
            })
          ) : (
            <Grid item xs>
              <Typography
                variant="h4"
                component="h4"
                align="center"
                className={classes.noProjectsMessage}
              >
                No Projects to display
              </Typography>{" "}
            </Grid>
          )}
          {projectList.length > pageSize ? (
            <Grid
              container
              justifyContent="center"
              className={classes.loadMoreButton}
              onClick={handleLoadMore}
            >
              <Button color="primary" variant="contained">
                Load More
              </Button>
            </Grid>
          ) : null}
        </Grid>
      </Paper>
    </ErrorBoundary>
  );
};

export default ProjectsGrid;
