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

/* eslint-disable no-param-reassign */
/* eslint-disable no-unused-vars */
import React, { useEffect } from "react";
import ReactMarkdown from "react-markdown";
import helper from "store/helper";
import {
  Box,
  Button,
  Card,
  CardMedia,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Grid,
  IconButton,
  Divider,
  TextareaAutosize,
  Tooltip,
  Typography,
} from "@mui/material";
import ImageIcon from "@mui/icons-material/Image";
import EditIcon from "@mui/icons-material/Edit";
import FindInPageIcon from "@mui/icons-material/FindInPage";
import DeveloperBoardIcon from "@mui/icons-material/DeveloperBoard";
import DeviceHubIcon from "@mui/icons-material/DeviceHub";
import EventIcon from "@mui/icons-material/Event";
import ExtensionIcon from "@mui/icons-material/Extension";
import FileCopyIcon from "@mui/icons-material/FileCopy";
import LabelIcon from "@mui/icons-material/Label";
import LayersIcon from "@mui/icons-material/Layers";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import SaveIcon from "@mui/icons-material/Save";
import Icon from "@mui/material/Icon";
import AddBoxIcon from "@mui/icons-material/AddBox";
import CancelIcon from "@mui/icons-material/Cancel";
import ProjectImageSelector from "./ProjectImageSelector";
import useStyles from "./ProjectDescriptionStyles";

const getCard = (
  cls,
  fieldName,
  fieldValues,
  defaultValue,
  fieldIcon,
  toolTip,
  alignFieldValues,
) => {
  const getIcon = (fi, c, tt) => {
    return (
      <Tooltip title={tt}>
        <Icon className={c.dashboardIcon} color="primary">
          {fi}
        </Icon>
      </Tooltip>
    );
  };
  return (
    <Box boxShadow={2} p={1} className={cls.box}>
      <Grid container direction="column" spacing={0}>
        <Grid container direction="row" spacing={0}>
          <Grid item xs={12}>
            <Typography className={cls.fieldTitle} align="left" gutterBottom>
              {getIcon(fieldIcon, cls, toolTip || fieldName)}
              {` ${fieldName}`}
            </Typography>
            <Typography className={cls.fieldValue} align={alignFieldValues}>
              {` ${fieldValues}`}
            </Typography>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

const ProjectDescription = ({
  selectedProject,
  metadata,
  labelsData,
  sensorData,
  updateProject,
  uploadImage,
}) => {
  const classes = useStyles();
  const fieldTypeEnum = {
    fieldTypeBig: {
      box: classes.boxBig,
      fieldValue: classes.fieldValueBig,
      dashboardIcon: classes.dashboardIconBig,
      fieldTitle: classes.fieldTitleBig,
      fieldContent: classes.fieldContent,
      dataOuterDiv: classes.dataOuterDiv,
      dataInnerDiv: classes.dataInnerDiv,
      colOne: 7,
      name: "Big",
    },
    fieldTypeNormal: {
      box: classes.boxNormal,
      fieldValue: classes.fieldValueBig,
      dashboardIcon: classes.dashboardIconBig,
      fieldTitle: classes.fieldTitleBig,
      fieldContent: classes.fieldContent,
      dataOuterDiv: classes.dataOuterDiv,
      dataInnerDiv: classes.dataInnerDiv,
      colOne: 3,
      name: "Normal",
    },
    fieldTypeSmall: {
      box: classes.boxSmall,
      fieldValue: classes.fieldValueSmall,
      dashboardIcon: classes.dashboardIconBig,
      fieldTitle: classes.fieldTitleSmall,
      fieldContent: classes.fieldContent,
      dataOuterDiv: classes.dataOuterDiv,
      dataInnerDiv: classes.dataInnerDiv,
      colOne: 6,
      name: "Small",
    },
  };
  const [project, setProject] = React.useState(null);
  const [metadataValues, setMetadataValues] = React.useState(null);
  const [device, setDevice] = React.useState(null);
  const [sensors, setSensors] = React.useState(null);
  const [labeldataValues, setLabeldataValues] = React.useState(null);
  const [editDescription, setEditDescription] = React.useState(false);
  const [openImageSelector, setOpenImageSelector] = React.useState(false);
  const [projectImgSelected, setProjectImgSelected] = React.useState(null);
  const [dataDescription, setDataDescription] = React.useState(null);

  useEffect(() => {
    if (metadata && !metadata.isFetching) {
      setMetadataValues(metadata.data);
      const d = metadata.data.find((m) => m.name === "Device");
      if (d !== undefined) {
        setDevice(d.label_values);
      }
    }
  }, [metadata]);

  useEffect(() => {
    if (labelsData && !labelsData.isFetching) setLabeldataValues(labelsData.data);
  }, [labelsData]);

  useEffect(() => {
    if (sensorData && !sensorData.isFetching) setSensors(sensorData.data);
  }, [sensorData]);

  useEffect(() => {
    setProject(selectedProject);
    setDataDescription(selectedProject.description);
    setEditDescription(false);
  }, [selectedProject]);

  const saveDataDescription = (event) => {
    setEditDescription(false);
    if (selectedProject.description !== dataDescription) {
      selectedProject.description = dataDescription;
      updateProject(selectedProject);
    }
  };
  const editDataDescription = (event) => {
    setEditDescription(true);
  };
  const handleImageSelectorClose = (event) => {
    setOpenImageSelector(false);
  };
  const handlehandleImageSelectorSave = (event) => {
    selectedProject.img = projectImgSelected;

    uploadImage(projectImgSelected.data_url, projectImgSelected.file.name, project.uuid, () => {
      setOpenImageSelector(false);
    });
  };
  const changeProjectImage = (event) => {
    setOpenImageSelector(true);
  };
  const setProjectImage = (imageUrl) => {
    setProjectImgSelected(imageUrl);
  };

  return (
    <Grid
      className={classes.mainGrid}
      xs={12}
      item
      container
      direction="row"
      alignItems="stretch"
      spacing={1}
    >
      <Grid item xs={12} lg={4}>
        <Card className={classes.card}>
          <CardMedia
            component={"a"}
            alt="Contemplative Reptile"
            className={classes.media}
            image={
              project
                ? selectedProject.img
                  ? selectedProject.img.data_url
                  : `${process.env.REACT_APP_API_URL}project/${project.uuid}/image/`
                : null
            }
          />
          <Grid container direction="row" spacing={0} justifyContent="flex-end">
            <Typography className={"MuiTypography--heading"} variant={"h5"} gutterBottom>
              <Tooltip title="Change Image">
                <IconButton onClick={changeProjectImage} color="primary" size="large">
                  <ImageIcon />
                </IconButton>
              </Tooltip>
            </Typography>
          </Grid>
        </Card>
      </Grid>
      <Grid lg={8} xs={12} item container direction="row" alignItems="stretch" spacing={0}>
        <Grid item xs>
          {getCard(
            fieldTypeEnum.fieldTypeBig,
            "Captures",
            [project ? project.files : ""],
            0,
            <FileCopyIcon fontSize="inherit" />,
            "Total number of Capture Files.",
            "right",
          )}
        </Grid>
        <Grid item xs>
          {getCard(
            fieldTypeEnum.fieldTypeBig,
            "Queries",
            [project ? project.queries : ""],
            0,
            <FindInPageIcon fontSize="inherit" />,
            "Total number Of Queries.",
            "right",
          )}
        </Grid>
        <Grid item xs>
          {getCard(
            fieldTypeEnum.fieldTypeBig,
            "Pipelines",
            [project ? project.pipelines : ""],
            0,
            <DeviceHubIcon fontSize="inherit" />,
            "Total number Of Pipelines.",
            "right",
          )}
        </Grid>
        <Grid item xs>
          {getCard(
            fieldTypeEnum.fieldTypeBig,
            "Models",
            [project ? project.models : ""],
            0,
            <ExtensionIcon fontSize="inherit" />,
            "Total number Of Knowledge Packs.",
            "right",
          )}
        </Grid>
        <Grid item xs>
          {getCard(
            fieldTypeEnum.fieldTypeBig,
            "Segments",
            [project ? project.segments : ""],
            0,
            <LayersIcon fontSize="inherit" />,
            "Total number Of Segments.",
            "right",
          )}
        </Grid>
        <Grid item xs>
          {getCard(
            fieldTypeEnum.fieldTypeBig,
            "Size(MB)",
            [project ? project.size_mb : ""],
            0,
            <SaveIcon fontSize="inherit" />,
            "Total size of all Capture Files.",
            "right",
          )}
        </Grid>
        <Grid item xs={12}>
          {getCard(
            fieldTypeEnum.fieldTypeSmall,
            "Created Date",
            [project ? helper.convertToLocalDateTime(project.created_at) : ""],
            "N/A",
            <EventIcon fontSize="inherit" />,
            "Project created date.",
            "left",
          )}
        </Grid>
        <Grid item xs={12}>
          {getCard(
            fieldTypeEnum.fieldTypeSmall,
            "UUID",
            [project ? project.uuid : ""],
            "N/A",
            <EventIcon fontSize="inherit" />,
            "Project unique identifier.",
            "left",
          )}
        </Grid>

        <Grid item xs={12}>
          {getCard(
            fieldTypeEnum.fieldTypeSmall,
            "Sensors",
            [sensors ? sensors.join(", ") : ""],
            "N/A",
            <DeveloperBoardIcon fontSize="inherit" />,
            "Sensors captured by the device.",
            "left",
          )}
        </Grid>
        <Grid item xs={12}>
          {getCard(
            fieldTypeEnum.fieldTypeSmall,
            "Labels",
            labeldataValues
              ? labeldataValues.map(
                  (l) => `${l.name} : ${l.label_values.map((lv) => lv.value).join(", ")}`,
                )
              : ["N/A"],
            "",
            <LabelIcon fontSize="inherit" />,
            "Labels for the dataset",
            "left",
          )}
        </Grid>

        <Grid item xs={12}>
          {getCard(
            fieldTypeEnum.fieldTypeSmall,
            "Metadata",
            [metadataValues ? metadataValues.map((m) => m.name).join(", ") : ""],
            "N/A",
            <MenuBookIcon fontSize="inherit" />,
            "Metadata associated with this project.",
            "left",
          )}
        </Grid>
      </Grid>
      <Grid item xs={12}>
        <Box m={4}>
          <Divider orientation="horizontal" />
        </Box>
        <Grid container direction="row" spacing={0} justifyContent="space-between">
          <Typography className={"MuiTypography--heading"} variant={"h5"} gutterBottom>
            <b>Project Description: {selectedProject.name} </b>{" "}
          </Typography>
          <Typography className={"MuiTypography--heading"} variant={"h4"} gutterBottom>
            {editDescription ? (
              <span>
                <Tooltip title="Save Data Description">
                  <IconButton color="primary" onClick={saveDataDescription} size="large">
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
              </span>
            ) : (
              <Tooltip title="Edit Data Description (Markdown)">
                <IconButton color="primary" onClick={editDataDescription} size="large">
                  <EditIcon />
                </IconButton>
              </Tooltip>
            )}
          </Typography>
        </Grid>
      </Grid>

      {editDescription ? (
        <TextareaAutosize
          className={classes.dataDescription}
          id="dataDescription"
          variant="outlined"
          value={dataDescription}
          onChange={(event) => setDataDescription(event.target.value)}
          minRows={5}
        />
      ) : (
        <Grid>
          <ReactMarkdown>{dataDescription}</ReactMarkdown>
        </Grid>
      )}

      <Dialog
        disableEscapeKeyDown
        open={openImageSelector}
        onClose={handleImageSelectorClose}
        id="renameKnowledgePack"
        aria-labelledby="form-dialog-title"
      >
        <DialogTitle id="form-dialog-title">Replace Project Image</DialogTitle>
        <DialogContent>
          <DialogContentText id="form-dialog-content">
            Please select an Image.
            <ProjectImageSelector setProjectImage={setProjectImage} />
          </DialogContentText>
        </DialogContent>
        <DialogActions id="renameKnowledgepackActions">
          <Button
            onClick={handleImageSelectorClose}
            startIcon={<CancelIcon />}
            color="primary"
            variant="outlined"
          >
            Cancel
          </Button>
          <Button
            onClick={handlehandleImageSelectorSave}
            startIcon={<AddBoxIcon />}
            color="primary"
            variant="outlined"
          >
            Upload
          </Button>
        </DialogActions>
      </Dialog>
    </Grid>
  );
};

export default ProjectDescription;
