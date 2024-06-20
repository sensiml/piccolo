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

import React, { useState, useCallback, useMemo, useEffect } from "react";
import _ from "lodash";
import TrendingFlatIcon from "@mui/icons-material/TrendingFlat";

import { Alert, Button, Box, FormControl, FormHelperText, Grid, Zoom } from "@mui/material";
import { useTranslation } from "react-i18next";

import SelectForm from "components/FormElements/SelectForm";
import TextFieldForm from "components/FormElements/TextFieldForm";

import DynamicFormElement from "components/FormElements/DynamicFormElement";
import UIRenderParameters from "components/UIRenderParameters";
import makeStyles from "@mui/styles/makeStyles";

import { IconSpinneAutoRenew } from "components/UIIcons";

const useStyles = () =>
  makeStyles((theme) => ({
    ...theme.common,

    formWrapper: {
      padding: 0,
      display: "flex",
      flexDirection: "column",
      justifyContent: "space-around",
    },
    formWrap: {
      width: "100%",
      display: "flex",
      marginBottom: theme.spacing(3),
    },
    submitBtn: {
      display: "flex",
      aliginItems: "center",
      justifyContent: "center",
      marginTop: theme.spacing(2),
    },
    alertIcon: {
      padding: theme.spacing(1),
    },
    queryReplacementFormKey: {
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      paddingRight: theme.spacing(2),
    },
  }))();

const PipelineQueryCreateForm = ({
  pipelineError,
  onSubmit,
  queryInputData,
  loadingPipelineSteps,
  importedQueryName,
  importedIsUseSessionPreprocessor,
  importedColumns,
}) => {
  const { t } = useTranslation("pipelines");
  const classes = useStyles();

  const [pipelineName, setPipelineName] = useState("");
  const [queryName, setQueryName] = useState("");
  const [isUseSessionPreprocessor, setIsUseSessionPreprocessor] = useState(true);
  const [replacedColumns, setReplacedColumns] = useState([]);
  const [queryFieldsError, setQueryFieldsError] = useState({});
  const [sensorErrors, setSensorErrors] = useState("");

  const queryFields = useMemo(() => {
    return _.filter(queryInputData, (el) => !el.descriptionParameters);
  }, [queryInputData]);

  const queryDescriptionParameters = useMemo(() => {
    // extract descriptionParameters
    const { descriptionParameters: res = [] } =
      queryInputData?.find((el) => el.descriptionParameters?.length) || {};
    return res.find((el) => el.name === queryName) || {};
  }, [queryInputData, queryName]);

  const queryDescParamsToRender = useMemo(() => {
    return {
      ...queryDescriptionParameters,
    };
  }, [queryInputData, queryName]);

  const importWarning = useMemo(() => {
    if (importedColumns?.length > queryDescriptionParameters?.columns?.length) {
      // eslint-disable-next-line max-len
      return t("form-import.alert-warning-sensor-replace");
    }
    return "";
  }, [importedColumns, queryDescriptionParameters]);

  const isNeededReplaceColumns = useMemo(() => {
    /**
     * check if imported pipeline has different sensors to show a replaced form
     */
    if (_.isArray(queryDescriptionParameters?.columns) && _.isArray(importedColumns)) {
      return !_.isEqual(importedColumns.sort(), queryDescriptionParameters?.columns.sort());
    }
    return false;
  }, [importedColumns, queryDescriptionParameters]);

  const getQueryColumnsOptions = useCallback(
    (currentVal) => {
      let res = [];
      if (!_.isEmpty(queryDescriptionParameters) && _.isArray(queryDescriptionParameters.columns)) {
        res = queryDescriptionParameters.columns
          .filter((el) => !_.values(replacedColumns).includes(el) || el === currentVal)
          .map((el) => ({
            name: el,
            value: el,
          }));
      }
      return res;
    },
    [queryInputData, queryName, replacedColumns],
  );

  const getQueryFieldError = useCallback(
    (name) => {
      if (queryFieldsError) {
        return queryFieldsError[name];
      }
      return "";
    },
    [queryFieldsError],
  );

  const getQueryFieldDefaultValue = useCallback(
    // eslint-disable-next-line consistent-return
    (name) => {
      if (name === "name") {
        return importedQueryName;
      }
      if (name === "use_session_preprocessor") {
        return _.isUndefined(importedIsUseSessionPreprocessor)
          ? true
          : importedIsUseSessionPreprocessor;
      }
    },
    [importedQueryName, importedIsUseSessionPreprocessor],
  );

  useEffect(() => {
    // clear sensor errors
    setSensorErrors("");
  }, [replacedColumns, importedColumns]);

  const clearErrors = () => {
    setSensorErrors("");
  };

  const validateForm = () => {
    let isValid = true;
    if (!queryName) {
      setQueryFieldsError({ name: t("form-import.error-required-query-name") });
      isValid = false;
    }
    if (isNeededReplaceColumns) {
      if (
        importedColumns?.length >= queryDescriptionParameters?.columns?.length &&
        _.filter(_.values(replacedColumns), (val) => val)?.length !==
          queryDescriptionParameters?.columns?.length
      ) {
        setSensorErrors(t("form-import.error-required-sensors"));
        isValid = false;
      } else if (
        importedColumns?.length < queryDescriptionParameters?.columns?.length &&
        _.filter(_.values(replacedColumns), (val) => val)?.length !== importedColumns?.length
      ) {
        setSensorErrors(t("form-import.error-required-sensors"));
        isValid = false;
      }
    }
    return isValid;
  };

  const handleChangePipelineName = (_name, value) => {
    setPipelineName(value);
  };

  const handleSubmit = () => {
    if (validateForm()) {
      onSubmit(pipelineName, queryName, isUseSessionPreprocessor, replacedColumns);
    }
  };

  const handleChangeQuery = (name, val) => {
    if (name === "name") {
      setQueryFieldsError((oldVal = {}) => {
        const updatedVal = { ...oldVal };
        updatedVal.name = null;
        return updatedVal;
      });
      clearErrors();
      setReplacedColumns([]);
      setQueryName(val);
    }
    if (name === "use_session_preprocessor") {
      setIsUseSessionPreprocessor(val);
    }
  };

  const handleChangeColumns = (importedColumn, selectedColumn) => {
    setReplacedColumns((value) => {
      const upatedValue = { ...value };
      upatedValue[importedColumn] = selectedColumn;
      return upatedValue;
    });
  };

  return (
    <Box className={classes.dialogFormWrapper}>
      <Box>
        <TextFieldForm
          id="name"
          label={t("form-import.crate-label-new-name")}
          className={classes.formWrap}
          onChange={handleChangePipelineName}
          error={Boolean(pipelineError)}
          helperText={pipelineError}
          variant="outlined"
          autoFocus
          fullWidth
        />
        {queryFields.map((formItemProps = {}) => (
          <FormControl
            className={classes.formWrap}
            error={Boolean(getQueryFieldError(formItemProps.name))}
          >
            <DynamicFormElement
              formType={formItemProps?.type}
              variant="outlined"
              {...formItemProps}
              onChange={handleChangeQuery}
              defaultValue={getQueryFieldDefaultValue(formItemProps.name)}
              error={Boolean(getQueryFieldError(formItemProps.name))}
            />
            <FormHelperText error>{getQueryFieldError(formItemProps.name)}</FormHelperText>
          </FormControl>
        ))}
        {!_.isEmpty(queryDescriptionParameters) ? (
          <Zoom in={!_.isEmpty(queryDescriptionParameters)}>
            <Box>
              <UIRenderParameters parameters={queryDescParamsToRender} />
            </Box>
          </Zoom>
        ) : null}
        {isNeededReplaceColumns ? (
          // form for replacing sensors
          <>
            <Alert variant="outlined" severity={importWarning ? "warning" : "info"}>
              {importWarning || t("form-import.alert-info-sensor-replace", { queryName })}
            </Alert>
            <UIRenderParameters parameters={{ sensorColumns: "" }} />
            {importedColumns.map((importedColumn) => (
              <Grid
                container
                className={classes.formWrap}
                key={`sensor_${importedColumn}_${queryName}`}
              >
                <Grid item className={classes.queryReplacementFormKey} xs={4}>
                  {`${importedColumn}`} <TrendingFlatIcon color="primary" />
                </Grid>
                <Grid item xs={8}>
                  <SelectForm
                    id={"select_query"}
                    labelId={"select_query_label"}
                    name={importedColumn}
                    options={getQueryColumnsOptions(replacedColumns[importedColumn])}
                    onChange={handleChangeColumns}
                    isCleared
                    fullWidth
                  />
                  <FormHelperText error>{sensorErrors}</FormHelperText>
                </Grid>
              </Grid>
            ))}
          </>
        ) : null}
      </Box>

      <Box className={classes.formWrapper}>
        <Button
          className={classes.submitBtn}
          color="primary"
          variant="contained"
          onClick={handleSubmit}
          disabled={loadingPipelineSteps?.isLoading}
        >
          {loadingPipelineSteps?.isLoading ? (
            <>
              <IconSpinneAutoRenew />
              {loadingPipelineSteps?.message}
            </>
          ) : (
            t("form-import.create-btn")
          )}
        </Button>
      </Box>
    </Box>
  );
};

export default PipelineQueryCreateForm;
