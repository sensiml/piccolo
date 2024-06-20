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

import * as platformActions from "./actions";
import { STORE_PLATFORMS, LOADING_PLATFORMS } from "./actionTypes";

import "regenerator-runtime/runtime";
import mockAxios from "axios";

describe("platforms actions", () => {
  it("should fetch all platforms", async () => {
    //mock setup
    const responsePlatforms = [
      {
        applications: "SensiML",
        platform_versions: ["2.1", "1.3"],
        uuid: "test",
        name: "SensiML",
      },
      {
        applications: "Arm GCC",
        platform_versions: ["2.1", "1.3"],
        uuid: "e9f53dfa-f434-4f24-9577-839c190f74da",
        name: "Arm GCC",
      },
    ];

    const expectedPlatforms = [
      {
        applications: "Arm GCC",
        platform_versions: ["2.1", "1.3"],
        uuid: "e9f53dfa-f434-4f24-9577-839c190f74da",
        name: "Arm GCC",
      },
      {
        applications: "SensiML",
        platform_versions: ["2.1", "1.3"],
        uuid: "test",
        name: "SensiML",
      },
    ];
    const mockedResponse = Promise.resolve({ data: responsePlatforms });
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PLATFORMS,
      },
      {
        type: STORE_PLATFORMS,
        platforms: expectedPlatforms,
      },
    ];
    await platformActions.loadPlatforms()(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when platforms request fails", async () => {
    //mock setup
    const expectedPlatforms = [];

    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_PLATFORMS,
      },
      {
        type: STORE_PLATFORMS,
        platforms: expectedPlatforms,
      },
    ];
    await platformActions.loadPlatforms()(dispatch, getState);
    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });
});
