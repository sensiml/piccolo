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

import React, { useState, useCallback, useEffect } from "react";
import _ from "lodash";
import { useTranslation } from "react-i18next";
import { Alert, Box, Button, FormControl } from "@mui/material";
import CancelOutlinedIcon from "@mui/icons-material/CancelOutlined";

import filters from "filters";
import DynamicFormElement from "components/FormElements/DynamicFormElement";

import FormUIDescriptionParameters from "../DrawerDescriptionParameters";
import useStyles from "../../../containers/BuildModel/BuildModeStyle";

const FormQuery = ({
  inputData,
  options,
  onSubmit,
  onClose,
  onChangeData,
  getQueriesDescriptionParameters,
}) => {
  const { t } = useTranslation("models");
  const classes = useStyles();
  const [warningMessage, setWarningMessage] = useState("");
  const [initialParameters, setInitialParameters] = useState({});
  const [descriptionParameters, setDescriptionParameters] = useState({});
  const [isChangedColumns, setIsChangedColumns] = useState(false);
  const [isChangedSession, setIsChangedSession] = useState(false);
  const [queryData, setQueryData] = useState({});

  const getParameterList = useCallback(() => {
    return getQueriesDescriptionParameters(inputData);
  }, [inputData]);

  const getDescriptonParameters = useCallback(() => {
    const parameters = getParameterList();

    if (!_.isEmpty(parameters)) {
      const objParams = parameters.find((paramsObj) => paramsObj.name === queryData.name) || {};
      return objParams;
    }
    return {};
  }, [queryData]);

  const getDefault = (el) => {
    return el.default;
  };

  useEffect(() => {
    const parameters = getDescriptonParameters();

    if (!_.isEmpty(parameters) && _.isEmpty(initialParameters)) {
      setInitialParameters({ ...parameters, name: queryData.name });
    }

    if (!_.isEmpty(initialParameters) && !_.isEmpty(parameters)) {
      // check if any of columns have been changed

      const isEqualColumns = _.isEqual(
        _.sortBy(parameters?.columns),
        _.sortBy(initialParameters?.columns),
      );
      const isEqualMetadataColumns = _.isEqual(
        _.sortBy(parameters?.metadata_columns),
        _.sortBy(initialParameters?.metadata_columns),
      );

      setIsChangedSession(parameters.session === initialParameters.session);

      if (!isEqualColumns || !isEqualMetadataColumns) {
        if (!options?.is_should_be_reviewed) {
          // show warning message is it's not first query edit
          setWarningMessage(
            t("model-builder.drawer-edit-step-warning-query-disable", {
              name: initialParameters.name,
              params: `${!isEqualColumns ? "Columns" : ""}${
                !isEqualMetadataColumns ? " Metadata Columns" : ""
              }`,
            }),
          );
        }
        setIsChangedColumns(true);
      } else {
        setWarningMessage("");
        setIsChangedColumns(false);
      }
    }
    setDescriptionParameters(parameters);
  }, [queryData]);

  const handleUpdateValues = (name, value, defaultValue) => {
    if (name === "name") {
      onChangeData(value !== defaultValue, { transform: value, [name]: value });
    } else {
      onChangeData(value !== defaultValue, { [name]: value });
    }
    setQueryData((prevVal) => ({ ...prevVal, [name]: value }));
  };

  const handleSubmit = () => {
    const hiddenData = {};
    if (inputData?.length) {
      inputData
        .filter((formEl) => formEl.isFormHidden)
        .forEach((formEl) => {
          hiddenData[formEl.name] = formEl.default;
        });
    }
    const customName = inputData?.customName || queryData.name;
    onSubmit({
      customName,
      data: { ...queryData, ...hiddenData },
      options: { descriptionParameters, isChangedColumns, isChangedSession },
    });
  };

  return (
    <>
      <FormUIDescriptionParameters descriptionParameters={descriptionParameters} />
      {warningMessage ? (
        //
        <Box mt={2}>
          <Alert severity="warning">{warningMessage}</Alert>
        </Box>
      ) : null}
      {inputData?.length &&
        inputData
          .filter((formEl) => !formEl.isFormHidden)
          .map((formEl, index) => (
            <FormControl
              key={`${formEl.name}-${index}`}
              required
              fullWidth={true}
              className={classes.formControl}
            >
              <DynamicFormElement
                {...formEl}
                id={`top_level_${filters.filterToSnakeCase(inputData.type)}`}
                labelId={`top_level_label_${filters.filterToSnakeCase(inputData.type)}`}
                formType={formEl.type}
                value={queryData[formEl.name] || getDefault(formEl)}
                defaultValue={getDefault(formEl)}
                // onChange={(name, val) => handleUpdateValues(formEl.name, val, formEl)}
                onChange={(name, value) => handleUpdateValues(name, value, getDefault(formEl))}
                name={formEl.name}
                label={formEl.label}
                options={formEl.options}
              />
            </FormControl>
          ))}
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
          disabled={Boolean(warningMessage)}
        >
          {t("model-builder.drawer-edit-step-btn-add")}
        </Button>
      </Box>
    </>
  );
};

export default FormQuery;
