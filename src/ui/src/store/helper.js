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

/* eslint-disable func-names */
/* eslint-disable wrap-iife */
import TokenStorage from "services/TokenStorage";

const helper = (() => {
  const conditionalLowerCase = (value, convertToLower) => {
    return convertToLower === true ? value.toLocaleLowerCase() : value;
  };

  const sortObjects = (objArray, fieldName, caseIncensitive, sortType) => {
    const sortDirection = sortType && sortType === "dsc" ? -1 : 1;

    if (objArray) {
      objArray.sort(
        (a, b) =>
          (conditionalLowerCase(a[fieldName], caseIncensitive) >
          conditionalLowerCase(b[fieldName], caseIncensitive)
            ? 1
            : -1) * sortDirection,
      );
    }
    return objArray;
  };

  const safeGetValue = (source, defaultValue) => {
    return typeof source === "undefined" ? defaultValue : source;
  };

  const isNullOrEmpty = (value) => {
    return !(typeof value === "string" && value.length > 0);
  };

  const isNumber = (value) => {
    return typeof value === "number";
  };

  const getResponseErrorDetails = (err) => {
    return err.response && err.response.data && err.response.data.detail
      ? `${err.response.data.detail}${
          err.response.data.data && err.response.data.data.name
            ? ` - ${err.response.data.data.name[0]}`
            : ""
        }`
      : err.message;
  };

  const getResponseErrorData = (err) => {
    return err.response && err.response.data ? JSON.stringify(err.response.data.data) : "";
  };

  const getKeyByValue = (object, value) => {
    return Object.keys(object).find((key) => object[key] === value);
  };

  const getModeFrequency = (array) => {
    const counts = {};
    let frequency = 0;
    let mode = 0;

    for (let i = 0, len = array.length; i < len; i++) {
      const value = array[i];

      if (counts[value] === undefined) {
        counts[value] = 1;
      } else {
        counts[value] = counts[value] + 1;
      }
      if (counts[value] > frequency) {
        frequency = counts[value];
        mode = value;
      }
    }
    return { mode, frequency };
  };

  const getHeader = (apiToken) => {
    return {
      headers: {
        Authorization: `Bearer ${apiToken || TokenStorage.getToken()}`,
      },
    };
  };

  const hasAllProperties = (source, properties) => {
    if (!properties || !source) return false;

    for (let i = 0; i < properties.length; i++) {
      // eslint-disable-next-line no-prototype-builtins
      if (!source.hasOwnProperty(properties[i])) {
        return false;
      }
    }
    return true;
  };

  const perfLog = (sectionName, doWork) => {
    // eslint-disable-next-line prefer-destructuring
    const performance = window.performance;
    const t0 = performance.now();
    doWork();
    const t1 = performance.now();
    // eslint-disable-next-line no-console
    console.info(`Call to ${sectionName} took ${t1 - t0} milliseconds.`);
  };

  const convertToLocalDate = (dt) => {
    return dt ? new Date(dt).toLocaleDateString() : null;
  };

  const convertToLocalDateTime = (dt) => {
    if (!dt) return dt;
    // eslint-disable-next-line no-param-reassign
    dt = new Date(dt);
    return `${dt.toLocaleDateString()} ${dt.toLocaleTimeString("en-US")}`;
  };

  const capitalizeWords = (str) => {
    return str.replace(/\w\S*/g, (txt) => {
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
  };

  const b64toBlob = (b64Data, contentTypeParam, sliceSizeParam) => {
    const contentType = contentTypeParam || "";
    const sliceSize = sliceSizeParam || 512;

    const byteCharacters = atob(b64Data);
    const byteArrays = [];

    for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
      const slice = byteCharacters.slice(offset, offset + sliceSize);
      const byteNumbers = new Array(slice.length);

      for (let i = 0; i < slice.length; i++) {
        byteNumbers[i] = slice.charCodeAt(i);
      }
      const byteArray = new Uint8Array(byteNumbers);
      byteArrays.push(byteArray);
    }
    const blob = new Blob(byteArrays, { type: contentType });
    return blob;
  };

  return {
    capitalizeWords,
    convertToLocalDate,
    convertToLocalDateTime,
    getResponseErrorDetails,
    getResponseErrorData,
    getKeyByValue,
    getModeFrequency,
    getHeader,
    hasAllProperties,
    isNullOrEmpty,
    isNumber,
    perfLog,
    sortObjects,
    safeGetValue,
    b64toBlob,
  };
})();

export default helper;
