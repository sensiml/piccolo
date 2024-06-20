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

/* eslint-disable */
// Link.react.test.js
import React from "react";
import QueryCacheAlert from ".";
import { CACHE_STATUSES } from "store/queries/const";

import { screen, fireEvent, cleanup } from "@testing-library/react";

import { renderWithTheme } from "tests";

describe("Testing QueryCacheAlert component", () => {
  const title = "Title";
  const selectedQuery = "1";
  const queryCacheStatusDataEmpty = { message: "Message", status: false, build_status: "FAILED" };
  const queryCacheStatusDataUpToDate = {
    message: "Message SUCCESS",
    status: true,
    build_status: CACHE_STATUSES.CACHED,
  };
  const queryCacheStatusDataOutOfSync = {
    message: "Message OUT OF SYNC",
    status: false,
    build_status: CACHE_STATUSES.CACHED,
  };
  const queryCacheStatusDataBuilding = {
    message: "Message OUT OF BUILDING",
    status: false,
    build_status: CACHE_STATUSES.BUILDING,
  };
  const queryCacheStatusDataNotBuild = {
    message: "Message OUT OF NOT_BUILT",
    status: false,
    build_status: CACHE_STATUSES.NOT_BUILT,
  };
  const queryCacheStatusDataFailed = {
    message: "Message OUT OF FAILDED",
    status: false,
    build_status: CACHE_STATUSES.FAILED,
  };

  afterEach(cleanup);

  it("isNewQuery -> Should show new test query message", () => {
    // withHooks(() => {
    renderWithTheme(
      <QueryCacheAlert
        title={title}
        isNewQuery={true}
        selectedQuery={selectedQuery}
        queryCacheStatusData={queryCacheStatusDataEmpty}
      />,
    );

    expect(screen.getByRole("alert").className).toContain("Info");
    expect(screen.getByRole("alert")).toHaveTextContent("create-form.message-info");
  });

  it("Query cache has up to date -> Should show success alert without build btn", () => {
    renderWithTheme(
      <QueryCacheAlert
        title={title}
        selectedQuery={selectedQuery}
        queryCacheStatusData={queryCacheStatusDataUpToDate}
      />,
    );
    expect(screen.getByRole("alert").className).toContain("Success");
    expect(screen.getByRole("alert")).toHaveTextContent(queryCacheStatusDataUpToDate.message);
  });

  it("Query cache is out of sync -> Should show warning alert with build btn", () => {
    const mockHandleBuild = jest.fn();
    const mockHandleDismiss = jest.fn();

    renderWithTheme(
      <QueryCacheAlert
        title={title}
        selectedQuery={selectedQuery}
        queryCacheStatusData={queryCacheStatusDataOutOfSync}
        onBuildCache={mockHandleBuild}
        onDismiss={mockHandleDismiss}
      />,
    );
    expect(screen.getByRole("alert").className).toContain("Warning");
    expect(screen.getByRole("alert")).toHaveTextContent(queryCacheStatusDataOutOfSync.message);

    fireEvent.click(screen.getByTestId("dismiss_btn"));
    expect(mockHandleDismiss).toHaveBeenCalled();

    fireEvent.click(screen.getByTestId("build_cache_btn"));
    expect(mockHandleBuild).toHaveBeenCalled();
  });

  it("Query cache is building -> Should show warning alert with disabled btns", () => {
    const mockHandleBuild = jest.fn();
    const mockHandleDismiss = jest.fn();

    renderWithTheme(
      <QueryCacheAlert
        title={title}
        selectedQuery={selectedQuery}
        queryCacheStatusData={queryCacheStatusDataBuilding}
        onBuildCache={mockHandleBuild}
        onDismiss={mockHandleDismiss}
      />,
    );

    expect(screen.getByRole("alert").className).toContain("Info");
    expect(screen.getByRole("alert")).toHaveTextContent(queryCacheStatusDataBuilding.message);

    expect(screen.getByTestId("dismiss_btn").className).toContain("disabled");
    expect(screen.getByTestId("build_cache_btn").className).toContain("disabled");
  });

  it("Query cache has not built -> Should show warning alert with enabled btns", () => {
    const mockHandleBuild = jest.fn();
    const mockHandleDismiss = jest.fn();

    renderWithTheme(
      <QueryCacheAlert
        title={title}
        selectedQuery={selectedQuery}
        queryCacheStatusData={queryCacheStatusDataNotBuild}
        onBuildCache={mockHandleBuild}
        onDismiss={mockHandleDismiss}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(queryCacheStatusDataNotBuild.message);
    expect(screen.getByRole("alert").className).toContain("Info");

    fireEvent.click(screen.getByTestId("dismiss_btn"));
    expect(mockHandleDismiss).toBeCalled();

    fireEvent.click(screen.getByTestId("build_cache_btn"));
    expect(mockHandleBuild.mock.calls[0][0]).toEqual(selectedQuery);
  });

  it("Query cache has failed -> Should show error alert with disabled dismiss btn", () => {
    const mockHandleBuild = jest.fn();
    const mockHandleDismiss = jest.fn();

    renderWithTheme(
      <QueryCacheAlert
        title={title}
        selectedQuery={selectedQuery}
        queryCacheStatusData={queryCacheStatusDataFailed}
        onBuildCache={mockHandleBuild}
        onDismiss={mockHandleDismiss}
      />,
    );

    expect(screen.getByRole("alert")).toHaveTextContent(queryCacheStatusDataFailed.message);
    expect(screen.getByRole("alert").className).toContain("Error");

    // only dissmiss should be disabled
    expect(screen.getByTestId("dismiss_btn").className).toContain("disabled");
    expect(screen.getByTestId("build_cache_btn").className).not.toContain("disabled");

    fireEvent.click(screen.getByTestId("build_cache_btn"));

    expect(mockHandleBuild.mock.calls[0][0]).toEqual(selectedQuery);
  });
});
