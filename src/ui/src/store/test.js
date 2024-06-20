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

import helper from "./helper";
import logger from "./logger";
import mockAxios from "axios";
import "regenerator-runtime/runtime";

describe("helper actions", () => {
  it("should get default value if undefined", () => {
    expect(helper.safeGetValue(undefined, "test")).toEqual("test");
    expect(helper.safeGetValue("test1", "test")).toEqual("test1");
  });

  it("should sort objects by field", () => {
    let expectedList = [
      { name: "adam" },
      { name: "brian" },
      { name: "carl" },
      { name: "david" },
      { name: "eric" },
    ];
    let actualList = [
      { name: "carl" },
      { name: "david" },
      { name: "adam" },
      { name: "brian" },
      { name: "eric" },
    ];
    expect(helper.sortObjects(actualList, "name")).toEqual(expectedList);
    expect(helper.sortObjects(undefined, "name")).toEqual(undefined);
  });

  it("should check if field is string and is null or empty", () => {
    expect(helper.isNullOrEmpty("not empty")).toEqual(false);
    expect(helper.isNullOrEmpty("")).toEqual(true);
    expect(helper.isNullOrEmpty(undefined)).toEqual(true);
    expect(helper.isNullOrEmpty({ name: "Test" })).toEqual(true);
    expect(helper.isNullOrEmpty(["Test1", "Test2"])).toEqual(true);
  });

  it("should return error details for a given error response", () => {
    expect(
      helper.getResponseErrorDetails({
        response: { data: { detail: "My Details" } },
        message: "Some Message",
      })
    ).toEqual("My Details");
    expect(
      helper.getResponseErrorDetails({
        response: { data: {} },
        message: "Some Message",
      })
    ).toEqual("Some Message");
    expect(
      helper.getResponseErrorDetails({ response: {}, message: "Some Message" })
    ).toEqual("Some Message");
    expect(helper.getResponseErrorDetails({ message: "Some Message" })).toEqual(
      "Some Message"
    );
  });

  it("should return error data for a given error response", () => {
    expect(
      helper.getResponseErrorData({
        response: { data: { data: { value1: "value1", value2: "value2" } } },
      })
    ).toEqual(JSON.stringify({ value1: "value1", value2: "value2" }));
    expect(helper.getResponseErrorData({ response: {} })).toEqual("");
    expect(helper.getResponseErrorData({})).toEqual("");
  });
});

describe("logger actions", () => {
  it("should log to console", () => {
    const expectedConsole = jest.spyOn(console, "log");
    logger.logConsole("", "hello", "stack trace", "");
    expect(expectedConsole).toHaveBeenCalledWith(
      "message:hello, stacktrace:stack trace"
    );
    expectedConsole.mockClear();
  });

  it("should log to console with array of stack trace items", () => {
    const expectedConsole = jest.spyOn(console, "log");
    logger.logConsole(
      "",
      "hello",
      ["stack message1", "stack message2", "stack message3"],
      ""
    );
    expect(expectedConsole).toHaveBeenCalledWith(
      "message:hello, stacktrace:stack message1, stack message2, stack message3"
    );
    expectedConsole.mockClear();
  });

  it("should log Error to the server", () => {
    logger.logError("trilochan", "hello", "stack trace", "error tag");
    let expectedQryStr = getLogObjectQueryString(
      "ERROR",
      "trilochan",
      "hello",
      '"stack trace"',
      "error tag"
    );
    expect(mockAxios.post).toHaveBeenCalledWith("/log/", expectedQryStr);
  });

  it("should log Warning to the server", () => {
    logger.logWarning("trilochan", "hello", "stack trace", "error tag");
    let expectedQryStr = getLogObjectQueryString(
      "WARNING",
      "trilochan",
      "hello",
      '"stack trace"',
      "error tag"
    );
    expect(mockAxios.post).toHaveBeenCalledWith("/log/", expectedQryStr);
  });

  it("should log Info to the server", () => {
    logger.logInfo("trilochan", "hello", "stack trace", "error tag");
    let expectedQryStr = getLogObjectQueryString(
      "INFO",
      "trilochan",
      "hello",
      '"stack trace"',
      "error tag"
    );
    expect(mockAxios.post).toHaveBeenCalledWith("/log/", expectedQryStr);
  });

  it("should log Debug to the server", () => {
    logger.logDebug("trilochan", "hello", "stack trace", "error tag");
    let expectedQryStr = getLogObjectQueryString(
      "DEBUG",
      "trilochan",
      "hello",
      '"stack trace"',
      "error tag"
    );
    expect(mockAxios.post).toHaveBeenCalledWith("/log/", expectedQryStr);
  });

  it("should log Debug to the server with array of stack trace items", () => {
    logger.logDebug(
      "trilochan",
      "hello",
      ["stack message1", "stack message2", "stack message3"],
      "error tag"
    );
    let expectedQryStr = getLogObjectQueryString(
      "DEBUG",
      "trilochan",
      "hello",
      ["stack message1", "stack message2", "stack message3"],
      "error tag"
    );
    expect(mockAxios.post).toHaveBeenCalledWith("/log/", expectedQryStr);
  });
});

function getLogObjectQueryString(loglevel, username, message, stacktrace, tag) {
  let logObject = {
    loglevel: loglevel,
    username: username,
    application: "Web Client",
    message,
    stacktrace: Array.isArray(stacktrace) ? stacktrace.join(", ") : stacktrace,
    tag: tag,
    browser: "Netscape",
    client_information: JSON.stringify({
      browserName: navigator.appName,
      browserEngine: navigator.product,
      browserVersion1a: navigator.appVersion,
      browserVersion1b: navigator.userAgent,
      browserLanguage: navigator.language,
      browserOnline: navigator.onLine,
      browserPlatform: navigator.platform,
      sizeDocW: document.width,
      sizeDocH: document.height,
    }),
  };
  let esc = encodeURIComponent;
  return Object.keys(logObject)
    .map((k) => esc(k) + "=" + esc(logObject[k]))
    .join("&");
}
