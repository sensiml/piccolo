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

/* eslint-disable jsx-a11y/anchor-is-valid */
import _ from "lodash";
import React, { useEffect, useState, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { Grid, IconButton, Snackbar, Tooltip, Typography, Paper, Box, Link } from "@mui/material";
import LaunchIcon from "@mui/icons-material/Launch";
import DeleteIcon from "@mui/icons-material/Delete";
import { useHistory, generatePath } from "react-router-dom";
import AddIcon from "@mui/icons-material/Add";

import logger from "store/logger";
import ToastMessage from "components/ToastMessage/ToastMessage";
import Capsule from "components/Capsule";
import ProjectSearch from "components/ProjectSearch";
import StandardTable from "components/StandardTable";
import DialogFormProject from "components/DialogFormProject";

import { ColumnType } from "components/ResponsiveTable/Filters/FilterConstants";
import { DialogConfirm } from "components/DialogConfirm";
import { UITablePanel } from "components/UIPanels";

import { UIButtonResponsiveToShort } from "components/UIButtons";

import { ROUTES } from "routers";
import { GETTING_STARTED_GUIDE_LINK } from "config";

import useStyles from "./ProjectsTableStyles";

const maxSegmentsForStarterEdition = 2500;

const convertToProjectSummary = (pList) => {
  if (!pList) return pList;
  return pList.map((p) => {
    return {
      ...p,
      created_at: p.created_at ? new Date(p.created_at).toLocaleDateString() : null,
    };
  });
};

const ProjectsTable = ({
  projectData,
  lastSelectedProject,
  selectedProject,
  userId,
  teamInfo,
  setSelectedProject,
  setLastSelectedProject,
  createProject,
  deleteProject,
  loadProjects,
}) => {
  const { t } = useTranslation("projects");
  const classes = useStyles();
  const routerHistory = useHistory();
  const [pageSize] = useState(10);
  const [projectList, setProjectList] = useState(convertToProjectSummary(projectData.data));
  const [open, setOpen] = React.useState(false);
  const [openSnackbar, setOpenSnackbar] = React.useState(false);
  const [snackBarMessage, setSnackBarMessage] = React.useState("");
  const [snackBarVariant, setSnackBarVariant] = React.useState("success");
  const [deletingProjectUuid, setDeletingProjectUuid] = useState("");
  const [deletingProjectName, setDeletingProjectName] = useState("");

  const [isOpenDialogCreateProject, setIsOpenDialogCreateProject] = useState(false);
  const [createProjectError, setCreateProjectError] = useState("");

  const projectNames = useMemo(() => {
    if (!_.isEmpty(projectData?.data)) {
      return projectData.data.map((el) => el.name);
    }
    return [];
  }, [projectData]);

  const searchProjects = (searchString) => {
    if (projectData.data && projectData.data.length > 0) {
      setProjectList(
        convertToProjectSummary(
          projectData.data.filter((project) => new RegExp(searchString, "i").test(project.name)),
        ),
      );
    }
  };

  const delayedQuery = _.debounce((q) => searchProjects(q), 200);

  const setSearchText = (searchText) => {
    delayedQuery(searchText);
  };

  const projectChanged = async (projectUUID) => {
    if (projectUUID === "") return;
    await setSelectedProject(projectUUID);
    const project = projectData.data && projectData.data.find((p) => p.uuid === projectUUID);
    setLastSelectedProject(project, teamInfo?.team, userId);
    logger.logInfo("", "open_project", {
      total_files: project?.files || 0,
      total_segments: project?.segments || 0,
      total_knowledge_packs: project?.models || 0,
      project_uuid: project?.uuid,
      project_name: project?.name,
    });

    routerHistory.push(generatePath(ROUTES.MAIN.PROJECT_SUMMARY.path, { projectUUID }));
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleRefreshAction = () => {
    setSearchText("");
    loadProjects();
  };

  const handleManageProject = (event, projectUuid) => {
    projectChanged(projectUuid);
  };

  useEffect(() => {
    const loadProjectsList = async () => {
      if (_.isEmpty(projectData.data)) {
        await loadProjects();
      }
    };
    loadProjectsList();
  }, []);

  useEffect(() => {
    setProjectList(convertToProjectSummary(projectData.data));
  }, [projectData]);

  const handleNulls = (value) => {
    return value || 0;
  };

  const handleSegments = (value) => {
    const v = value || 0;
    return teamInfo && teamInfo.subscription === "STARTER" ? (
      <Tooltip
        placement="bottom"
        classes={{ tooltip: classes.segmenterTooltip }}
        title={
          <>
            {" "}
            <Typography className={classes.segmenterTypography}>
              <pre style={{ fontFamily: "inherit" }}>
                Starter editions are limited to 2500 labeled segments per project.
              </pre>
            </Typography>
          </>
        }
      >
        <span>
          {" "}
          <Capsule value={v} highLimit={maxSegmentsForStarterEdition} />
        </span>
      </Tooltip>
    ) : (
      v
    );
  };

  const handleCloseSnackbar = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }
    setOpenSnackbar(false);
  };

  const handleDeleteProject = (value, uuid, name) => {
    setDeletingProjectName(name);
    setDeletingProjectUuid(uuid);
    setOpen(true);
  };

  const openSnackBarWithMsg = (variant, message) => {
    setSnackBarMessage(message);
    setSnackBarVariant(variant);
    setOpenSnackbar(true);
  };

  const handleProjectDeletion = async () => {
    setOpen(false);
    try {
      await deleteProject(deletingProjectUuid);
    } catch (err) {
      let errMessage = `Failed to deleted ${deletingProjectName}`;
      if (err && err.response && err.response.status && err.response.status === 403) {
        errMessage = "Your account does not have permission to delete a Project.";
      }
      openSnackBarWithMsg("error", errMessage);
      await loadProjects();
      return;
    }
    openSnackBarWithMsg(
      "success",
      t("table.success-msg-delete-project", { name: deletingProjectName }),
    );
  };

  const handleSwitchDialogCreateProject = (isOpen) => {
    if (createProjectError) {
      setCreateProjectError("");
    }
    setIsOpenDialogCreateProject(isOpen);
  };

  const handleCreateProject = async (name) => {
    try {
      await createProject(name);
      handleSwitchDialogCreateProject(false);
      openSnackBarWithMsg("success", t("table.success-msg-create-project", { name }));
    } catch (error) {
      setCreateProjectError(error.message);
    }
  };

  const openProjectRender = (value) => {
    return (
      <Tooltip title="Open Project..">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={(e) => handleManageProject(e, value)}
        >
          <LaunchIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const deleteProjectRender = (value, row) => {
    return (
      <Tooltip title="Delete Project.">
        <IconButton
          variant="contained"
          color="primary"
          size="small"
          onClick={(e) => handleDeleteProject(e, value, row.name)}
        >
          <DeleteIcon />
        </IconButton>
      </Tooltip>
    );
  };

  const columns = [
    {
      title: "",
      field: "uuid",
      render: openProjectRender,
    },
    {
      title: "Name",
      field: "name",
      primary: true,
      sortable: true,
      type: ColumnType.Text,
      filterable: true,
    },
    {
      title: "Files",
      field: "files",
      render: handleNulls,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Pipelines",
      field: "pipelines",
      render: handleNulls,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Size (MB)",
      field: "size_mb",
      render: handleNulls,
      type: ColumnType.Numeric,
      sortable: true,
      filterable: true,
    },
    {
      title: "Queries",
      field: "queries",
      render: handleNulls,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Models",
      field: "models",
      render: handleNulls,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Segments",
      field: "segments",
      render: handleSegments,
      sortable: true,
      type: ColumnType.Numeric,
      filterable: true,
    },
    {
      title: "Created Date",
      field: "created_at",
      type: "date",
      render: handleNulls,
      sortable: true,
      filterable: true,
    },
    {
      title: "Delete",
      field: "uuid",
      render: deleteProjectRender,
    },
  ];

  const options = {
    isDarkHeader: true,
    rowsPerPage: pageSize,
    showPagination: true,
    noContentText: (
      <>
        Welcome to the SensiML Analytics Toolkit. Follow the{" "}
        <Link target={"_blank"} href={GETTING_STARTED_GUIDE_LINK}>
          Getting Started guide
        </Link>{" "}
        to learn how to build your first application.
      </>
    ),
    excludePrimaryFromDetails: true,
    rowsPerPageOptions: [5, 10, 25, 50, 100, "All"],
    applyFilters: true,
    onRowDoubleClick: (event, row) => {
      handleManageProject(event, row.uuid, row.name);
    },
  };

  return (
    <Box className={classes.root}>
      <Grid container spacing={0}>
        <Grid item xs={12} className={classes.searchWrapper}>
          <Paper elevation={0}>
            <ProjectSearch setSearchText={setSearchText} resetHandler={handleRefreshAction} />
          </Paper>
        </Grid>
        <Grid item xs={12} className={classes.loadedElement}>
          <UITablePanel
            title={t("table.title")}
            ActionComponent={
              <>
                <UIButtonResponsiveToShort
                  variant={"outlined"}
                  color={"primary"}
                  onClick={() => handleSwitchDialogCreateProject(true)}
                  tooltip={"Create a new project"}
                  text={t("table.btn-create")}
                  icon={<AddIcon />}
                />
              </>
            }
          />
          <StandardTable
            className="step"
            tableId="projectList"
            tableColumns={columns}
            tableData={{ data: projectList, isFetching: projectData.isFetching }}
            tableOptions={options}
          />
        </Grid>
        {lastSelectedProject?.uuid && !selectedProject.uuid && !projectData.isFetching ? (
          <Grid item xs={12}>
            <Paper elevation={0} className={classes.lastProjectWrapper}>
              <Typography variant="h2" className={classes.lastProjectTitle}>
                Last opened project:{" "}
                <Link
                  underline="hover"
                  href="#"
                  onClick={(e) => handleManageProject(e, lastSelectedProject?.uuid)}
                >
                  {lastSelectedProject?.name}
                </Link>
              </Typography>
            </Paper>
          </Grid>
        ) : null}
        {isOpenDialogCreateProject ? (
          <DialogFormProject
            title={t("table.dialog-create-title")}
            isOpen={isOpenDialogCreateProject}
            existingNames={projectNames}
            validationError={createProjectError}
            onClose={() => handleSwitchDialogCreateProject(false)}
            onSubmit={handleCreateProject}
          />
        ) : null}
        <Grid item xs={12}>
          <DialogConfirm
            isOpen={open}
            title={t("table.dialog-delete-title")}
            text={t("table.dialog-delete-text", { deletingProjectName })}
            onConfirm={handleProjectDeletion}
            onCancel={handleClose}
            cancelText={t("dialog-confirm-delete.cancel")}
            confirmText={t("dialog-confirm-delete.delete")}
          />
          <Snackbar
            anchorOrigin={{
              vertical: "top",
              horizontal: "right",
            }}
            open={openSnackbar}
            autoHideDuration={2000}
            onClose={handleCloseSnackbar}
          >
            <ToastMessage
              onClose={handleCloseSnackbar}
              variant={snackBarVariant}
              message={snackBarMessage}
            />
          </Snackbar>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProjectsTable;
