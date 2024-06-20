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

/* eslint-disable prefer-object-spread */
import React, { useState, useEffect } from "react";
import {
  Avatar,
  Box,
  Grid,
  Card,
  CardHeader,
  CardContent,
  FormControl,
  MenuItem,
  Select,
  Typography,
} from "@mui/material";
import useStyles from "./DetailViewStyles";
import DescriptionSection from "./DescriptionSection";
// eslint-disable-next-line import/no-cycle
import { getIcon, getTitle, renderInputRows } from "../PipelineBuilderConstants";

export default function SetCard({ pipeline, transforms }) {
  const classes = useStyles();
  const [transform, setTransform] = useState([]);
  const [functionInputs, setFunctionInputs] = useState(pipeline ? pipeline.inputs : []);
  const [functionList, setFunctionList] = useState(null);
  const [functionSelected, setFunctionSelected] = useState(null);
  const [selectedFunctionIndex, setSelectedFunctionIndex] = useState(0);

  const handleFunctionNameChange = (event) => {
    const selectedFunction = pipeline.set[event.target.value];
    setSelectedFunctionIndex(event.target.value);
    setFunctionSelected(selectedFunction);
    setFunctionInputs(
      Object.assign({}, selectedFunction ? selectedFunction.inputs : [], pipeline.inputs),
    );
    setTransform(transforms.find((t) => t.name === selectedFunction.function_name) || {});
  };

  useEffect(() => {
    if (!pipeline) {
      return;
    }

    if (pipeline.set && pipeline.set.length > 0) {
      setFunctionList(pipeline.set.map((s) => s.function_name));
      const selectedFunction = pipeline.set[0];
      setFunctionSelected(selectedFunction);
      setSelectedFunctionIndex(0);
      setTransform(transforms.find((t) => t.name === selectedFunction.function_name) || {});
    }
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
            <Typography className={classes.pos}>
              {transform.type ? transform.type : pipeline.type}
            </Typography>
          </Grid>
          <Grid item xs={1} />
          <Grid item xs={3}>
            <Typography className={classes.title}>Number Of Functions:</Typography>
          </Grid>
          <Grid item xs={8}>
            <Typography className={classes.pos}>{pipeline.set.length}</Typography>
          </Grid>
          <Grid item xs={1} />
          {functionList ? (
            <>
              <Grid item xs={3}>
                <Typography className={classes.title}>Function:</Typography>
              </Grid>
              <Grid item xs={8}>
                <FormControl fullWidth>
                  <Select
                    name="functions"
                    value={selectedFunctionIndex}
                    onChange={handleFunctionNameChange}
                  >
                    {functionList &&
                      functionList.map((functionName, index) => {
                        return (
                          <MenuItem key={`${functionName}-${index}`} value={index}>
                            {functionName}
                          </MenuItem>
                        );
                      })}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={1} />
            </>
          ) : null}
          {functionSelected && functionSelected.inputs ? (
            <Grid item xs={12}>
              <Box boxShadow={3} m={1} p={1}>
                <Grid container spacing={1}>
                  <Grid item xs={12}>
                    <Typography variant="h6">Function Inputs</Typography>
                  </Grid>
                  {renderInputRows(transform, functionInputs, classes)}
                </Grid>
                <DescriptionSection transform={transform} />
              </Box>
            </Grid>
          ) : null}
        </Grid>
      </CardContent>
    </Card>
  );
}
