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

import _ from "lodash";

class BaseAPIError extends Error {
  constructor(errorCode, response) {
    super();
    if (errorCode === 404) {
      // eslint-disable-next-line max-len
      this.message = `Server doesn't support API endpoint ${response?.config?.url}. Please, contact support.`;
    } else if (errorCode !== 500) {
      this.message = _.truncate(_.trim(this.parseErrorData(response?.data)), { length: 300 });
    } else if (!response) {
      this.message = "Something went wrong. Please, contact support.";
    } else if (response && _.isString(response)) {
      this.message = response;
    } else {
      this.message = "Something went wrong. Please, contact support.";
    }
    this.name = this.constructor.name;
    this.errorCode = errorCode;
  }

  // eslint-disable-next-line class-methods-use-this
  parseErrorData(data) {
    let message = "";

    const concatMessage = (existingMessage, messageToJoin) => {
      return existingMessage ? `${existingMessage} ${messageToJoin}` : `${messageToJoin}`;
    };

    if (_.isArray(data?.data)) {
      data.data.forEach((value) => {
        if (_.isObject(value)) {
          _.entries(value).forEach(([dataKey, dataValue]) => {
            if (_.isArray(dataValue)) {
              message = concatMessage(message, `${dataKey}: `);
              dataValue.forEach((val) => {
                message = concatMessage(message, val);
              });
            } else {
              message = concatMessage(message, `${dataKey}: ${dataValue}`);
            }
          });
        } else {
          message = concatMessage(message, value);
        }
      });
    } else if (!_.isEmpty(data?.data)) {
      _.entries(data?.data).forEach(([dataKey, dataValue]) => {
        if (_.isArray(dataValue)) {
          message = concatMessage(message, `${dataKey}: `);
          dataValue.forEach((value) => {
            message = concatMessage(message, value);
          });
        } else {
          message = concatMessage(message, `${dataKey}: ${dataValue}`);
        }
      });
    }
    // in these cases details should be at the beginning
    if (data?.message) {
      return concatMessage(data.message, `${message ? "\n" : ""}${message}`);
    }
    if (data?.detail) {
      return concatMessage(data.detail, `${message ? "\n" : ""}${message}`);
    }
    if (data?.error_description) {
      return concatMessage(data.error_description, `${message ? "\n" : ""}${message}`);
    }

    if (!_.isEmpty(data)) {
      _.entries(data).forEach(([dataKey, dataValue]) => {
        if (_.isArray(dataValue)) {
          message = concatMessage(message, `${dataKey}: `);
          dataValue.forEach((value) => {
            message = concatMessage(message, value);
          });
        } else {
          message = concatMessage(message, `${dataKey}: ${dataValue}`);
        }
      });
    }
    return message;
  }
}

export default BaseAPIError;
