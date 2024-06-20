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
/* eslint-disable array-callback-return */
import React, { useState, useEffect } from "react";
import ReactFlow from "react-flow-renderer";
import ErrorBoundary from "components/ErrorBoundary";
import { Box, Grid } from "@mui/material";
import PipelineNode from "./PipelineNode";
import useStyles from "./PipelineBuilderStyles";
import { getDetailView } from "./PipelineBuilderConstants";

const defaultBoxShadow = 2;
const selectdBoxShadow = 20;
const nodeStyle = {
  fontSize: "14px",
  fontFamily: "Roboto, Helvetica, Arial, sans-serif",
};

const nodeTypes = {
  selectorNode: PipelineNode,
};

const PipelineBuilder = ({ pipelineSteps, transforms, sources }) => {
  const classes = useStyles();
  const [transformList, setTransformList] = useState([{ name: "" }]);
  const [showDetails, setShowDetails] = useState(false);
  const [pipelineStepDetails, setPipelineStepDetails] = useState([]);
  const [pipelineStepSelected, setPipelineStepSelected] = useState(null);

  const [graphStyles, setGraphStyles] = useState({
    width: "100%",
    maxWidth: "600px",
    display: "flex",
    justifyContent: "flex-right",
    overflowy: "true",
    height: `10px`,
  });

  const handleElementClick = (event, pl) => {
    setPipelineStepSelected(pl.data.pipeline);
    setShowDetails(true);
    setPipelineStepDetails((ppd) => {
      ppd.map((p) => {
        if (p.type === "selectorNode") {
          if (p.data.pipeline.name === pl.data.pipeline.name) {
            p.data.shadow = selectdBoxShadow;
          } else {
            p.data.shadow = defaultBoxShadow;
          }
        }
      });
      return ppd;
    });
  };

  useEffect(() => {
    setTransformList(transforms);
  }, [transforms]);

  useEffect(() => {
    if (!pipelineSteps) return;

    const ppd = [];
    const xPosition = 50;
    let yPosition = 0;
    let maxLength = 100 + Math.max(...pipelineSteps.map((p) => p.name.length)) * 10;
    if (maxLength > 500) maxLength = 500;
    pipelineSteps.map((pl, idx) => {
      ppd.push({
        id: `${idx + 1}`,
        data: {
          pipeline: pl,
          width: 350,
          shadow: defaultBoxShadow,
        },
        position: { x: xPosition, y: yPosition },
        type: "selectorNode",
        style: nodeStyle,
      });
      if (idx > 0) {
        ppd.push({
          id: `e${idx}-${idx + 1}`,
          source: `${idx}`,
          target: `${idx + 1}`,
          arrowHeadType: "arrowclosed",
        });
      }
      yPosition += 120;
    });

    setShowDetails(false);
    setPipelineStepDetails(ppd);
    setGraphStyles((prev) => ({
      ...prev,
      height: `${160 * pipelineSteps.length}px`,
    }));
  }, [pipelineSteps]);

  const onLoad = (reactFlowInstance) => reactFlowInstance;

  return (
    <ErrorBoundary>
      <Box p={4} className={classes.box}>
        <Grid container spacing={1}>
          <Grid item xs={6} className={classes.flowWrapper}>
            {pipelineStepDetails ? (
              <ReactFlow
                style={graphStyles}
                onElementClick={handleElementClick}
                elementsSelectable={false}
                nodesDraggable={false}
                zoomOnScroll={false}
                zoomOnDoubleClick={false}
                paneMoveable={false}
                elements={pipelineStepDetails}
                onLoad={onLoad}
                nodeTypes={nodeTypes}
                selectNodesOnDrag={true}
              />
            ) : null}
          </Grid>
          <Grid item xs={6}>
            {showDetails && pipelineStepSelected
              ? getDetailView(pipelineStepSelected, transformList, sources, classes)
              : null}
          </Grid>
        </Grid>
      </Box>
    </ErrorBoundary>
  );
};

export default PipelineBuilder;
