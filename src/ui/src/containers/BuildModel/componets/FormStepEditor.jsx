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

import React, { useMemo, useRef, useEffect, useState, useCallback } from "react";
import _ from "lodash";
import Alert from "@mui/material/Alert";
import MonacoEditor, { useMonaco } from "@monaco-editor/react";
import SearchOutlinedIcon from "@mui/icons-material/SearchOutlined";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";

import { Box, Button, IconButton, Zoom } from "@mui/material";
import { useTranslation } from "react-i18next";

import useStyles from "../BuildModeStyle";

const FormStepEditor = ({ name, data, transforms, onClose, onChangeData, onSubmit }) => {
  const monaco = useMonaco();
  const editorRef = useRef(null);
  const classes = useStyles();
  const [parsedValue, setParsedValue] = useState({});
  const [editorValidationError, setEditorValidationError] = useState("");

  const { t } = useTranslation("models");

  const getFromTemplate = useCallback(
    (_codePart, _docPart, isSplitByComma) => {
      const filteredCodePart = _.entries(_codePart).reduce((acc, [key, val]) => {
        if (!["transform", "input_data", "isSelected"].includes(key)) {
          acc[key] = val;
        }
        return acc;
      }, {});
      return `\n${JSON.stringify(filteredCodePart, null, 2)}${
        isSplitByComma ? "," : ""
      }\n /* \n Documentation: \n${JSON.stringify(_docPart, null, 2)}  \n*/`;
    },
    [data],
  );

  const getTransformDoc = useCallback(
    (transformName, filteredParams = []) => {
      const transformObj = _.find(transforms, (trnsf) => trnsf.name === transformName) || {};
      let res = {};

      if (_.isArray(transformObj.input_contract)) {
        res = transformObj.input_contract
          .filter((constrant) => filteredParams.includes(constrant?.name))
          .reduce((acc, contract) => {
            if (!["input_data"].includes(contract?.name)) {
              acc.push({ ...contract });
            }
            return acc;
          }, []);
      }
      return res;
    },
    [data],
  );

  const parseEditorValue = (value) => {
    try {
      // remove comments
      return JSON.parse(value.replace(/\/\*[\s\S]*?\*\/|\/\/.*/g, "").trim());
    } catch (_err) {
      return undefined;
    }
  };

  const handleChange = (value) => {
    const _parsedValue = parseEditorValue(value);
    if (_parsedValue) {
      onChangeData(true, _parsedValue);
      setParsedValue(_parsedValue);
    }
  };

  const handleSubmit = () => {
    let _data = data;
    if (_.isArray(parsedValue)) {
      _data = parsedValue;
    } else if (!_.isEmpty(parsedValue)) {
      _data = { ...data, ...parsedValue };
    }
    onSubmit({
      data: _data,
      customName: data.transform || name,
    });
  };

  const handleEditorError = (validationErrors) => {
    if (!_.isEmpty(validationErrors)) {
      setEditorValidationError(
        `${_.map(validationErrors, (el) => `${el.message} at line ${el.endLineNumber}`).join("")}`,
      );
    } else {
      setEditorValidationError("");
    }
  };

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
  };

  const handleOpenSearch = () => {
    editorRef.current.getAction("actions.find").run("");
  };

  useEffect(() => {
    setEditorValidationError("");
  }, []);

  useEffect(() => {
    // do conditional chaining
    // or make sure that it exists by other ways
    if (monaco) {
      monaco.languages.json.jsonDefaults.setDiagnosticsOptions({
        validate: true,
        allowComments: false,
        schemaValidation: "error",
        comments: "ignore",
      });
    }
  }, [monaco]);

  const editorData = useMemo(() => {
    if (_.isArray(data)) {
      return `[${data
        .filter((el) => el !== "transform")
        .map((el, index) =>
          getFromTemplate(
            el,
            getTransformDoc(el.name, _.keys(el?.params)),
            index < data.length - 1,
          ),
        )
        .join("\n")}]`;
    }
    return getFromTemplate(data, getTransformDoc(data?.transform, _.keys(data)));
  }, [data]);

  return (
    <>
      {editorValidationError ? (
        <Zoom in={Boolean(editorValidationError)} className={classes.mb2}>
          <Alert variant="outlined" severity="error">
            {editorValidationError}
          </Alert>
        </Zoom>
      ) : (
        <Box display="flex" justifyContent={"flex-end"}>
          <IconButton onClick={handleOpenSearch} size="large">
            <SearchOutlinedIcon />
          </IconButton>
        </Box>
      )}
      <MonacoEditor
        height={"70vh"}
        defaultLanguage="json"
        defaultValue={editorData}
        options={{
          minimap: { enabled: false },
          scrollbar: {
            vertical: "hidden",
            horizontal: "hidden",
            verticalHasArrows: false,
            verticalSliderSize: 0,
          },
        }}
        onValidate={handleEditorError}
        onChange={(value) => handleChange(value)}
        onMount={handleEditorDidMount}
      />
      <Box className={classes.drawerFormButtonWrapper}>
        <Button
          className={`${classes.drawerFormButton} ${classes.mr2}`}
          size="large"
          startIcon={<CancelOutlinedIcon />}
          variant="outlined"
          color="primary"
          onClick={onClose}
          data-testid={"edit-step-form-close"}
        >
          {t("model-builder.drawer-edit-step-btn-cancel")}
        </Button>
        <Button
          onClick={handleSubmit}
          className={classes.drawerFormButton}
          size="large"
          variant="contained"
          color="primary"
          data-testid={"edit-step-form-submit"}
        >
          {t("model-builder.drawer-edit-step-btn-add")}
        </Button>
      </Box>
    </>
  );
};

export default FormStepEditor;
