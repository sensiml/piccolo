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

import React from "react";
import _ from "lodash";
import PropTypes from "prop-types";

import { Alert, FormControl } from "@mui/material";

import DynamicFormElement from "components/FormElements/DynamicFormElement";
import useStyle from "./CaptureMetadataFormStyles";

const CaptureMetadataForm = ({
  captureMetadataFormData,
  captureConfigurationFromData,
  onUpdateCaptureField,
  onUpdateMetadataField,
  alertMessage,
  validationErrors = [],
  alertType = "info",
}) => {
  const classes = useStyle();

  const handleUpdateConfiruration = (name, value) => {
    onUpdateCaptureField(name, value);
  };

  const handleUpdataMetadata = (name, value) => {
    onUpdateMetadataField(name, value);
  };

  return (
    <>
      {!_.isEmpty(validationErrors) ? (
        <Alert severity={"error"}>
          {validationErrors.map((validationMessage) => (
            <p>{validationMessage}</p>
          ))}
        </Alert>
      ) : null}
      {alertMessage ? <Alert severity={alertType}>{alertMessage}</Alert> : null}
      {!_.isEmpty(captureConfigurationFromData) &&
        captureConfigurationFromData.map((formDataProps) => (
          <FormControl key={formDataProps.name} fullWidth={true} className={classes.formControl}>
            <DynamicFormElement
              isUpdateWithDefault={false}
              {...formDataProps}
              onChange={handleUpdateConfiruration}
            />
          </FormControl>
        ))}
      {!_.isEmpty(captureMetadataFormData) &&
        captureMetadataFormData.map((formDataProps) => (
          <FormControl key={formDataProps.name} fullWidth={true} className={classes.formControl}>
            <DynamicFormElement
              isUpdateWithDefault={false}
              {...formDataProps}
              onChange={handleUpdataMetadata}
            />
          </FormControl>
        ))}
    </>
  );
};

export default CaptureMetadataForm;

CaptureMetadataForm.propTypes = {
  onUpdateCaptureField: PropTypes.func,
  onUpdateMetadataField: PropTypes.func,
};

CaptureMetadataForm.defaultProps = {
  onUpdateCaptureField: () => {},
  onUpdateMetadataField: () => {},
};
