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

import React, { useState } from "react";

import { useTranslation } from "react-i18next";
import { useParams, useHistory } from "react-router-dom";

import RefreshIcon from "@mui/icons-material/Refresh";
import ExitToAppIcon from "@mui/icons-material/ExitToApp";
import { Box, Divider, Grid, Tab, Tabs, Button, Paper } from "@mui/material";

import { useFilterTurncateResponsive, useIsShortText } from "hooks";
import { ROUTES } from "routers";

import ProjectDescription from "components/ProjectDescription";
import QueriesTable from "components/QueriesTable";
import PipelinesTable from "components/PipelinesTable";
import KnowledgepacksTable from "components/KnowledgepacksTable";
import TabPanel from "components/TabPanel";
import ControlPanel from "components/ControlPanel";
import LabelTable from "components/LabelTable";
import MetadataTable from "components/MetadataTable";

import { UIButtonResponsiveToShort } from "components/UIButtons";

import useStyles from "./ProjectSummaryStyles";

function a11yProps(index) {
  return {
    id: `full-width-tab-${index}`,
    "aria-controls": `full-width-tabpanel-${index}`,
  };
}

const ButtonInTabs = ({ className, onClick, children, color }) => {
  return (
    <Button className={className} onClick={onClick} color={color}>
      {children}
    </Button>
  );
};

const ProjectSummary = ({
  projectData,
  labelValues,
  labels,
  metadataData,
  labelsIsFetching,
  defaultLabel,
  loadProjectSummaryData,
  loadProjectData,
  createLabelValue,
  updateLabelValue,
  deleteLabelValue,
  loadMetadata,
  createMetadata,
  updateMetadata,
  deleteMetadata,
  createMetadataValue,
  updateMetadataValue,
  deleteMetadataValue,
}) => {
  const classes = useStyles();
  const routersHistory = useHistory();

  const { t } = useTranslation("projects");
  const { projectUUID } = useParams();

  const [activeProjectTab, setActiveProjectTab] = useState(0);
  const [activeProjectSettingTab, setActiveProjectSettingTab] = useState(0);

  const handleChangeActiveProjectTab = (event, newValue) => {
    setActiveProjectTab(newValue);
  };

  const handleChangeActiveProjectSettingTab = (event, newValue) => {
    setActiveProjectSettingTab(newValue);
  };

  const handledleUpdateAction = () => {
    loadProjectSummaryData(projectUUID);
  };

  const handleRefreshProjectData = () => {
    loadProjectSummaryData(projectUUID);
    loadProjectData(projectUUID);
  };

  const handleGoToProjectSelect = () => {
    routersHistory.push(ROUTES.MAIN.HOME.path);
  };

  const filterTruncateResponsive = useFilterTurncateResponsive();
  const isShortText = useIsShortText();

  return (
    <Box className={classes.box}>
      <Grid container>
        <Grid container className={classes.grid}>
          <Grid item xs={12}>
            <Box mb={2}>
              <ControlPanel
                title={
                  isShortText
                    ? t("project-control-panel.small-header", {
                        projectName: filterTruncateResponsive(projectData.name),
                      })
                    : t("project-control-panel.header", {
                        projectName: filterTruncateResponsive(projectData.name),
                      })
                }
                actionsBtns={
                  <UIButtonResponsiveToShort
                    variant={"outlined"}
                    color={"primary"}
                    onClick={() => handleGoToProjectSelect()}
                    tooltip={t("project-summary.change-project-btn")}
                    text={t("project-summary.change-project-btn")}
                    icon={<ExitToAppIcon />}
                  />
                }
              />
            </Box>
          </Grid>
          <Grid item xs={12}>
            <Paper elevation={0}>
              <Box mb={2}>
                <Tabs
                  id="projectSummaryTabList"
                  value={activeProjectTab}
                  onChange={handleChangeActiveProjectTab}
                  indicatorColor="primary"
                  textColor="primary"
                  variant="scrollable"
                  scrollButtons="auto"
                >
                  <Tab label={`Overview`} {...a11yProps(0)} />

                  <Tab label="Queries" {...a11yProps(2)} />
                  <Tab label="Pipelines" {...a11yProps(2)} />
                  <Tab label="Models" {...a11yProps(4)} />
                  <Tab label="Project Settings" {...a11yProps(5)} />
                  <Box className={classes.actionsBtns}>
                    <ButtonInTabs
                      variant="contained"
                      color="primary"
                      className={classes.rightAlign}
                      onClick={(e) => handleRefreshProjectData(e)}
                    >
                      <RefreshIcon />
                    </ButtonInTabs>
                  </Box>
                </Tabs>
              </Box>
            </Paper>
            <TabPanel p={0} value={activeProjectTab} index={0}>
              <ProjectDescription />
            </TabPanel>
            <TabPanel p={0} value={activeProjectTab} index={1}>
              <QueriesTable onUpdateProjectAction={handledleUpdateAction} />
            </TabPanel>
            <TabPanel p={0} value={activeProjectTab} index={2}>
              <PipelinesTable onUpdateProjectAction={handledleUpdateAction} />
            </TabPanel>
            <TabPanel
              p={0}
              value={activeProjectTab}
              index={3}
              classes={{ root: classes.resetedTab }}
            >
              <KnowledgepacksTable />
            </TabPanel>
            <TabPanel
              p={0}
              value={activeProjectTab}
              index={4}
              classes={{ root: classes.resetedTab }}
            >
              <Tabs
                id="projectSummaryTabList"
                value={activeProjectSettingTab}
                onChange={handleChangeActiveProjectSettingTab}
                indicatorColor="primary"
                textColor="primary"
                variant="scrollable"
                scrollButtons="auto"
              >
                <Tab label={`Segment Labels`} {...a11yProps(1)} />
                <Tab label="Metadata" {...a11yProps(1)} />
              </Tabs>
              <Divider />
              <TabPanel p={0} mt={0} value={activeProjectSettingTab} index={0}>
                <LabelTable
                  projectUUID={projectUUID}
                  defaultLabel={defaultLabel}
                  labelValues={{ data: labelValues, isFetching: labelsIsFetching }}
                  labels={labels}
                  // label
                  createLabel={createLabelValue}
                  updateLabel={updateLabelValue}
                  deleteLabel={deleteLabelValue}
                />
              </TabPanel>
              <TabPanel p={0} mt={0} value={activeProjectSettingTab} index={1}>
                <MetadataTable
                  projectUUID={projectUUID}
                  metadata={{ data: metadataData, isFetching: false }}
                  loadMetadata={loadMetadata}
                  createMetadata={createMetadata}
                  updateMetadata={updateMetadata}
                  deleteMetadata={deleteMetadata}
                  createMetadataValue={createMetadataValue}
                  updateMetadataValue={updateMetadataValue}
                  deleteMetadataValue={deleteMetadataValue}
                />
              </TabPanel>
            </TabPanel>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ProjectSummary;
