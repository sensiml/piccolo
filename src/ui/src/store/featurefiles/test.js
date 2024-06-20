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

import * as featurefileActions from "./actions";
import { STORE_FEATURE_FILES, LOADING_FEATURE_FILES } from "./actionTypes";

import "regenerator-runtime/runtime";
import mockAxios from "axios";

describe("feature file actions", () => {
  it("should fetch all feature files for a project", async () => {
    //mock setup
    const expectedFeatureFiles = [
      {
        name: "FeatureFile1",
        created_at: "2019-04-04",
        uuid: "69b219e8-8868-4647-8f0f-284c4263572d"
      },
      {
        name: "test2",
        created_at: "2020-01-02",
        uuid: "726b26cf-4929-426e-8565-24e74c4dc408"
      }
    ];
    const mockedResponse = Promise.resolve({ data: expectedFeatureFiles });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_FEATURE_FILES
      },
      {
        type: STORE_FEATURE_FILES,
        featurefiles: expectedFeatureFiles
      }
    ];

    await featurefileActions.loadFeatureFiles(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should log error when feature files request fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_FEATURE_FILES
      },
      {
        type: STORE_FEATURE_FILES,
        featurefiles: []
      }
    ];

    await featurefileActions.loadFeatureFiles(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should return no feature files project is undefined", async () => {
    const projectUuid = undefined;
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_FEATURE_FILES
      },
      {
        type: STORE_FEATURE_FILES,
        featurefiles: []
      }
    ];

    await featurefileActions.loadFeatureFiles(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });
});
