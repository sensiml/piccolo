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

import React, { useEffect, useState } from "react";

import { useSelector } from "react-redux";
import { red } from "@mui/material/colors";
import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Tooltip,
  Divider,
  Typography,
} from "@mui/material";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/HighlightOff";
import IconButton from "@mui/material/IconButton";
import remove from "lodash/remove";
import helper from "store/helper";

import SelectForm from "components/FormElements/SelectForm";
import SelectMultiChip from "components/FormElements/SelectMultiChip";

import useStyles from "./QueryFilterStyles";

const KeyWords = {
  AND: {
    LowerCase: " and ",
    UpperCase: " AND ",
  },
  IN: {
    LowerCase: " in ",
    UpperCase: " IN ",
  },
};

const labelsToHide = ["SegmentID"];
const metadataToHide = ["capture_uuid", "segment_uuid"];
const QueryBuilder = ({ value, open, setOpen, setQueryFilter, queryMetada, queryLabel }) => {
  const [queryValue, setQueryValue] = useState(value);
  const [fieldId, setFieldId] = useState("");
  const [selectedFieldlValues, setSelectedFieldlValues] = useState([]);
  const [fieldlValues, setFieldlValues] = useState([]);
  const [splitQuery, setSplitQuery] = useState([]);
  const fieldData = [
    ...useSelector((state) => {
      return (
        state.labels.data &&
        state.labels.data.filter(
          (l) =>
            (helper.isNullOrEmpty(queryLabel) || queryLabel === l.name) &&
            !labelsToHide.includes(l.name),
        )
      );
    }),
    ...useSelector((state) => {
      return (
        state.metadata.data &&
        state.metadata.data.filter(
          (m) =>
            (!queryMetada || queryMetada.length === 0 || queryMetada.includes(m.name)) &&
            !metadataToHide.includes(m.name),
        )
      );
    }),
  ];

  const classes = useStyles();

  const getSelectedLabelValues = (selectedFieldValue) => {
    const selectedField = fieldData.find((field) => field.name === selectedFieldValue);
    return selectedField ? selectedField.label_values : [];
  };

  const getExistingLabelValues = (selectedFieldValue) => {
    let existingValues;
    if (splitQuery) {
      existingValues = splitQuery.find((sq) => sq.label === selectedFieldValue);
    }
    return existingValues ? existingValues.selectedValues : [];
  };

  const setExistingLabelValues = (selectedFieldValue, newFieldValues) => {
    let existingValues;
    if (splitQuery) {
      if (newFieldValues.length === 0) remove(splitQuery, (sq) => sq.label === selectedFieldValue);
      else {
        existingValues = splitQuery.find((sq) => sq.label === selectedFieldValue);

        if (existingValues) {
          existingValues.selectedValues = newFieldValues;
        } else {
          splitQuery.push({
            label: selectedFieldValue,
            selectedValues: newFieldValues,
          });
        }
      }
    }
    setQueryValue(
      splitQuery.map((sq) => `[${sq.label}] IN [${sq.selectedValues.join(",")}]`).join(" AND "),
    );
  };

  const labelChanged = (label) => {
    setFieldId(label);
    setFieldlValues(getSelectedLabelValues(label));
    setSelectedFieldlValues(getExistingLabelValues(label));
  };

  const labelValueChanged = (label, values) => {
    setSelectedFieldlValues(values);
    setExistingLabelValues(label, values);
  };

  const handleClose = () => {
    setQueryValue(value);
    setFieldId("");
    setSelectedFieldlValues([]);
    setFieldlValues([]);
    setSplitQuery([]);
    setOpen(false);
  };

  const handleSave = () => {
    setQueryFilter(queryValue);
    setOpen(false);
  };

  const handleLabelsChange = (_name, _value) => {
    labelChanged(_value);
  };

  const handleLabelValuesSelected = (_name, _value) => {
    labelValueChanged(fieldId, _value);
  };

  // eslint-disable-next-line no-shadow
  const getSplitQuery = (queryValue) => {
    if (queryValue.constructor.name === "SyntheticEvent") return [];
    return queryValue
      .replace(KeyWords.IN.LowerCase, KeyWords.IN.UpperCase)
      .replace(KeyWords.AND.LowerCase, KeyWords.AND.UpperCase)
      .replace(/\[|]/g, "")
      .split(KeyWords.AND.UpperCase)
      .map((val) => {
        const fieldVals = val.split(KeyWords.IN.UpperCase);
        return {
          label: (fieldVals[0] || "").trim(),
          selectedValues: (fieldVals[1] || "")
            .trim()
            .split(",")
            .map((f) => f.trim()),
        };
      });
  };

  useEffect(() => {
    setQueryValue(value);
    setFieldId("");
    setSelectedFieldlValues([]);
    setFieldlValues([]);
    setSplitQuery(value ? getSplitQuery(value) : []);
  }, [open, value]);

  useEffect(() => {
    const splitQ = getSplitQuery(value);
    const filteredLabels = [...queryMetada, queryLabel];
    const filtered = splitQ.filter((el) => filteredLabels.includes(el.label));

    setQueryFilter(
      filtered.map((sq) => `[${sq.label}] IN [${sq.selectedValues.join(",")}]`).join(" AND "),
    );
  }, [queryMetada, queryLabel, value]);

  return (
    <>
      <Dialog
        disableEscapeKeyDown
        open={open}
        fullWidth
        maxWidth="md"
        onClose={handleClose}
        aria-labelledby="form-dialog-title"
      >
        <DialogTitle id="form-dialog-title">Query Builder</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
            <Grid item xs>
              <Typography variant="h6" display="inline">
                Filter:{" "}
              </Typography>
              <Typography variant="subtitle1" display="inline">
                {queryValue.constructor.name === "SyntheticEvent"
                  ? queryValue.constructor.name
                  : queryValue}
              </Typography>
              <Divider />
            </Grid>
            {splitQuery.map((s, i) => (
              <Grid item xs={12} key={i}>
                <Grid container className={classes.splitQueryGrid}>
                  <Grid item>
                    <Tooltip title="Delete">
                      <IconButton
                        variant="contained"
                        style={{ color: red[800] }}
                        fontSize="small"
                        className={classes.splitQueryIcon}
                        onClick={() => {
                          labelValueChanged(s.label, []);
                          setFieldId("");
                        }}
                        size="large"
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Grid>
                  <Grid item>
                    <Tooltip title="Edit">
                      <IconButton
                        variant="contained"
                        color="primary"
                        fontSize="small"
                        className={classes.splitQueryIcon}
                        onClick={() => labelChanged(s.label)}
                        size="large"
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                  </Grid>
                  <Grid item className={classes.splitQueryLabel}>
                    <Typography variant="subtitle1">
                      {s.label} IN [{s.selectedValues.join(",")}]
                    </Typography>
                  </Grid>
                </Grid>
              </Grid>
            ))}
            <Grid item xs={12}>
              <SelectForm
                id="labelsList"
                labelId="labels"
                name="label"
                label="Label"
                fullWidth={false}
                onChange={handleLabelsChange}
                isUpdateWithDefault={false}
                isObserveDefaultValue={true}
                defaultValue={fieldId}
                options={
                  fieldData && fieldData.map((field) => ({ name: field.name, value: field.name }))
                }
              />
            </Grid>
            <Grid item xs={12}>
              <SelectMultiChip
                id="sourcesList"
                labelId="sourcesListId"
                name="source"
                label="Source"
                isUpdateWithDefault={false}
                isObserveDefaultValue={true}
                defaultValue={selectedFieldlValues}
                options={
                  fieldlValues &&
                  fieldlValues.map((fieldlValue) => ({
                    name: fieldlValue.value,
                    value: fieldlValue.value,
                  }))
                }
                onChange={handleLabelValuesSelected}
                displayEmpty
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSave} color="primary">
            Done
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default QueryBuilder;
