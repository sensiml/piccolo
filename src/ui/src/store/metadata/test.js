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

import * as metadataActions from "./actions";
import { LOADING_METADATA, STORE_METADATA } from "./actionTypes";
import "regenerator-runtime/runtime";
import mockAxios from "axios";

describe("metadata actions", () => {
  it("should fetch all metadata for a project", async () => {
    //mock setup
    const expectedMetadata = [{ name: "test1" }, { name: "test2" }];
    const mockedResponse = Promise.resolve({ data: expectedMetadata });
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";
    mockAxios.get.mockResolvedValue(mockedResponse);
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedAction = {
      type: STORE_METADATA,
      metadata: expectedMetadata
    };
    await metadataActions.loadMetadata(projectUuid)(dispatch, getState);
    expect(dispatch).toBeCalledWith(expectedAction);
  });

  it("should log error when metadata request fails", async () => {
    const projectUuid = "73e6b86b-3b86-45fa-a3f4-02feb9112515";

    mockAxios.get.mockImplementation(() => {
      throw new Error("Some Error");
    });
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_METADATA
      },
      {
        type: STORE_METADATA,
        metadata: []
      }
    ];

    await metadataActions.loadMetadata(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });

  it("should return no metadata project is undefined", async () => {
    const projectUuid = undefined;
    const dispatch = jest.fn();
    const getState = jest.fn();

    const expectedActions = [
      {
        type: LOADING_METADATA
      },
      {
        type: STORE_METADATA,
        metadata: []
      }
    ];

    await metadataActions.loadMetadata(projectUuid)(dispatch, getState);

    expect(dispatch.mock.calls[0][0]).toEqual(expectedActions[0]);
    expect(dispatch.mock.calls[1][0]).toEqual(expectedActions[1]);
  });
});
