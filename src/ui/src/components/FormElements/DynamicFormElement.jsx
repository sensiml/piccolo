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
import PropTypes from "prop-types";

import { FORM_TYPES } from "consts";
import InputNumberForm from "./InputNumberForm";
import TextFieldForm from "./TextFieldForm";
import SwitchBooleanForm from "./SwitchBooleanForm";
import SelectForm from "./SelectForm";
import SelectMultiChip from "./SelectMultiChip";
import SliderNumberForm from "./SliderNumberForm";
import SliderMinMaxForm from "./SliderMinMaxForm";

import InputDictSelectMultiChip from "./InputDictSelectMultiChip";
import InputArrayNumber from "./InputArrayNumber";
import InputArrayString from "./InputArrayString";

const DynamicFormElement = ({ formType, ...formProps }) => {
  switch (formType) {
    case FORM_TYPES.FORM_INT_TYPE:
      return <InputNumberForm {...formProps} />;
    case FORM_TYPES.FORM_INT_16T_TYPE:
      return <InputNumberForm {...formProps} />;
    case FORM_TYPES.FORM_NUMERIC_TYPE:
      return <InputNumberForm {...formProps} />;
    case FORM_TYPES.FORM_STRING_TYPE:
      return <TextFieldForm {...formProps} />;
    case FORM_TYPES.FORM_FLOAT_TYPE:
      return <InputNumberForm isFloat {...formProps} />;
    case FORM_TYPES.FORM_BOOLEAN_TYPE:
      return <SwitchBooleanForm {...formProps} />;
    case FORM_TYPES.FORM_BOOL_TYPE:
      return <SwitchBooleanForm {...formProps} />;
    case FORM_TYPES.FORM_SELECT_TYPE:
      return <SelectForm {...formProps} />;
    case FORM_TYPES.FORM_MULTI_SELECT_TYPE:
      return <SelectMultiChip {...formProps} />;
    case FORM_TYPES.FORM_RANGE_NUMERIC_TYPE:
      return <InputNumberForm {...formProps} />;
    case FORM_TYPES.FORM_RANGE_INT_TYPE:
      return <SliderNumberForm {...formProps} />;
    case FORM_TYPES.FORM_RANGE_FLOAT_TYPE:
      return <SliderNumberForm isFloat {...formProps} />;
    case FORM_TYPES.FORM_RANGE_MIN_MAX_TYPE:
      return <SliderMinMaxForm isFloat {...formProps} />;
    case FORM_TYPES.FORM_DICT_MULTISELECT_TYPE:
      return <InputDictSelectMultiChip {...formProps} />;
    case FORM_TYPES.FORM_DICT_MULTISELECT_STR_TYPE:
      return <InputDictSelectMultiChip {...formProps} />;
    case FORM_TYPES.FORM_EDITABLE_LIST_INT_TYPE:
      return <InputArrayNumber {...formProps} />;
    case FORM_TYPES.FORM_EDITABLE_LIST_FLOAT_TYPE:
      return <InputArrayNumber isFloat {...formProps} />;
    case FORM_TYPES.FORM_EDITABLE_LIST_STR_TYPE:
      return <InputArrayString {...formProps} />;

    default:
      return <div>{formProps.name}</div>;
  }
};

DynamicFormElement.propTypes = {
  id: PropTypes.string.isRequired,
};

export default DynamicFormElement;
