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

/* eslint-disable no-unused-vars */
import React, { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";
import _ from "lodash";

import CloudUploadOutlinedIcon from "@mui/icons-material/CloudUploadOutlined";
import makeStyles from "@mui/styles/makeStyles";

import { Box, Zoom } from "@mui/material";

const useStyles = () =>
  makeStyles((theme) => ({
    root: {
      position: "relative",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      borderRadius: theme.spacing(0.5),
      width: "100%",
      height: "100%",
      border: `1px solid ${theme.palette.primary.light}`,
    },
    draggingIn: {
      borderColor: theme.palette.primary.light,
      borderStyle: "dashed",
      transition: theme.transitions.create(["border-color"], {
        duration: theme.transitions.duration.complex,
      }),
    },
    isError: {
      borderColor: theme.palette.error.light,
      borderWidth: "2px",
      transition: theme.transitions.create(["border-color"], {
        duration: theme.transitions.duration.complex,
      }),
    },
    draggingWrapper: {
      position: "absolute",
      backgroundColor: theme.backgroundLoaderBackdrop,
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      flexDirection: "column",
      gap: theme.spacing(2),
      top: 0,
      bottom: 0,
      left: 0,
      right: 0,
      zIndex: 9999,
    },
  }))();

const UploadFileDnd = ({ children, isError, onDrop }) => {
  const classes = useStyles();
  const dropRef = useRef();

  let counter = 0;

  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragEnd = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDragIn = (e) => {
    e.preventDefault();
    e.stopPropagation();
    counter++;
    setIsDragging(true);
  };

  const handleDragOut = (e) => {
    e.preventDefault();
    e.stopPropagation();
    counter--;
    if (counter === 0) {
      setIsDragging(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && !_.isEmpty(e.dataTransfer.files)) {
      onDrop(e.dataTransfer.files);
      // e.dataTransfer.clearData();
      counter = 0;
      setIsDragging(false);
    }
  };

  const subscribeToEvents = () => {
    const box = dropRef.current;
    box.removeEventListener("dragover", handleDragOver);
    box.removeEventListener("dragenter", handleDragIn);
    box.removeEventListener("dragleave", handleDragOut);
    box.removeEventListener("drop", handleDrop);
    box.removeEventListener("dropend", handleDragEnd);
  };

  const unsubscribeFromEvents = () => {
    const box = dropRef.current;
    box.addEventListener("dragover", handleDragOver);
    box.addEventListener("dragenter", handleDragIn);
    box.addEventListener("dragleave", handleDragOut);
    box.addEventListener("drop", handleDrop);
    box.addEventListener("dropend", handleDragEnd);
  };

  useEffect(() => {
    subscribeToEvents();
    return unsubscribeFromEvents();
  }, []);

  return (
    <Box
      ref={dropRef}
      className={`${classes.root} ${
        isDragging ? classes.draggingIn : isError ? classes.isError : ""
      }`}
      p={6}
    >
      <Zoom in={isDragging}>
        <Box className={classes.draggingWrapper}>
          <CloudUploadOutlinedIcon color="primary" fontSize="large" />
          Drop here
        </Box>
      </Zoom>
      {children}
    </Box>
  );
};

UploadFileDnd.propTypes = {
  onDrop: PropTypes.func.isRequired,
  children: PropTypes.node.isRequired,
};

export default UploadFileDnd;
